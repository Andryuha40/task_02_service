from pathlib import Path
from threading import Lock

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

DATA_FILE = Path(__file__).with_name("data.csv")
REQUIRED_COLUMNS = [
    "id",
    "timestep",
    "consumption_eur",
    "consumption_sib",
    "price_eur",
    "price_sib",
]
DATA_LOCK = Lock()


class RecordCreate(BaseModel):
    timestep: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
    consumption_eur: float = Field(..., ge=0)
    consumption_sib: float = Field(..., ge=0)
    price_eur: float = Field(..., ge=0)
    price_sib: float = Field(..., ge=0)


class Record(RecordCreate):
    id: int


app = FastAPI(title="Electricity Market API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def save_data(df: pd.DataFrame) -> None:
    df.to_csv(DATA_FILE, index=False)


def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise RuntimeError(f"Файл данных не найден: {DATA_FILE}")

    try:
        df = pd.read_csv(DATA_FILE)
    except Exception as exc:
        raise RuntimeError("Не удалось прочитать CSV файл.") from exc

    if "id" not in df.columns:
        df.insert(0, "id", range(1, len(df) + 1))
        save_data(df)

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise RuntimeError(
            "В файле нет обязательных колонок: " + ", ".join(missing_columns)
        )

    return df[REQUIRED_COLUMNS].copy()


def next_id(df: pd.DataFrame) -> int:
    if df.empty:
        return 1
    return int(df["id"].max()) + 1


@app.exception_handler(Exception)
async def global_exception_handler(_, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Внутренняя ошибка сервера: {type(exc).__name__}"},
    )


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.get("/records", response_model=list[Record])
def get_records():
    with DATA_LOCK:
        df = load_data()
    return df.to_dict(orient="records")


@app.post("/records", response_model=Record, status_code=201)
def create_record(record: RecordCreate):
    with DATA_LOCK:
        df = load_data()
        new_record = record.model_dump()
        new_record["id"] = next_id(df)
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        save_data(df)
    return new_record


@app.delete("/records/{record_id}")
def delete_record(record_id: int):
    with DATA_LOCK:
        df = load_data()
        if record_id not in set(df["id"].tolist()):
            raise HTTPException(
                status_code=404,
                detail=f"Запись с id={record_id} не найдена.",
            )
        df = df[df["id"] != record_id]
        save_data(df)
    return {"status": "ok", "deleted_id": record_id}
