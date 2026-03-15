# Task 3: FastAPI + Streamlit

Простой сервис из двух частей:
- `backend` (FastAPI): хранит данные в CSV и отдает их через API.
- `frontend` (Streamlit): показывает таблицу/графики и работает только через API.

## Структура

- `backend/main.py` — API с `GET /records`, `POST /records`, `DELETE /records/{id}`
- `backend/data.csv` — данные
- `frontend/app.py` — UI
- `requirements.txt` — зависимости
- `Procfile` — команда старта для Railway

## 1) Локальный запуск

Откройте терминал в папке проекта:

```powershell
cd "D:\ВШЭ\МагоЛего Python\ДЗ 3\task_02_service"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Запуск backend:

```powershell
uvicorn backend.main:app --reload
```

Backend будет доступен на `http://127.0.0.1:8000`.

Запуск frontend (в другом терминале):

```powershell
cd "D:\ВШЭ\МагоЛего Python\ДЗ 3\task_02_service"
.\.venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```

## 2) Как работает API

- `GET /records` — получить все записи.
- `POST /records` — добавить запись (без `id`, id выдает сервер).
- `DELETE /records/{id}` — удалить запись по `id`.

Пример тела для `POST /records`:

```json
{
  "timestep": "2020-01-01 12:00",
  "consumption_eur": 60000,
  "consumption_sib": 17000,
  "price_eur": 300,
  "price_sib": 200
}
```

## 3) Деплой backend на Railway

Документация: <https://docs.railway.com/guides/fastapi>

Минимальные шаги:
1. Создайте проект на Railway и подключите репозиторий.
2. Root Directory укажите `task_02_service`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

## 4) Деплой backend на Render

Документация: <https://render.com/docs/deploy-fastapi>

Минимальные шаги:
1. Создайте `Web Service` и подключите репозиторий.
2. Root Directory укажите `task_02_service`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

## 5) Как подключить Streamlit к удаленному backend

Перед запуском Streamlit задайте переменную `API_URL`:

```powershell
$env:API_URL="https://your-backend-url"
streamlit run frontend/app.py
```

Если переменная не задана, используется `http://127.0.0.1:8000`.
## Deployment

- FastAPI: Railway backend
- Streamlit: Railway UI
