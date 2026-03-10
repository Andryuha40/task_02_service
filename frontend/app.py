import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")


st.set_page_config(page_title="Electricity Dashboard", layout="wide")
st.title("Мини-дашборд энергорынка")
st.caption(f"Backend API: {API_URL}")


def rerun_app() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def fetch_records() -> pd.DataFrame:
    try:
        response = requests.get(f"{API_URL}/records", timeout=20)
    except requests.RequestException as exc:
        st.error(f"Не удалось подключиться к API: {exc}")
        return pd.DataFrame()

    if response.status_code != 200:
        st.error(f"Ошибка API ({response.status_code}): {response.text}")
        return pd.DataFrame()

    data = response.json()
    if not data:
        return pd.DataFrame(columns=["id", "timestep", "consumption_eur", "consumption_sib", "price_eur", "price_sib"])

    return pd.DataFrame(data)


def add_record(payload: dict) -> None:
    try:
        response = requests.post(f"{API_URL}/records", json=payload, timeout=20)
    except requests.RequestException as exc:
        st.error(f"Ошибка отправки POST-запроса: {exc}")
        return

    if response.status_code == 201:
        st.success("Запись успешно добавлена.")
        rerun_app()
    else:
        st.error(f"Ошибка добавления ({response.status_code}): {response.text}")


def remove_record(record_id: int) -> None:
    try:
        response = requests.delete(f"{API_URL}/records/{record_id}", timeout=20)
    except requests.RequestException as exc:
        st.error(f"Ошибка отправки DELETE-запроса: {exc}")
        return

    if response.status_code == 200:
        st.success(f"Запись id={record_id} удалена.")
        rerun_app()
    else:
        st.error(f"Ошибка удаления ({response.status_code}): {response.text}")


df = fetch_records()

st.subheader("Таблица данных")
st.dataframe(df, use_container_width=True)

if not df.empty:
    chart_df = df.copy()
    chart_df["timestep"] = pd.to_datetime(chart_df["timestep"], errors="coerce")
    chart_df = chart_df.dropna(subset=["timestep"]).sort_values("timestep")

    consumption_long = chart_df.melt(
        id_vars=["timestep"],
        value_vars=["consumption_eur", "consumption_sib"],
        var_name="region",
        value_name="consumption",
    )
    fig_consumption = px.line(
        consumption_long,
        x="timestep",
        y="consumption",
        color="region",
        title="Потребление энергии",
    )
    st.plotly_chart(fig_consumption, use_container_width=True)

    price_long = chart_df.melt(
        id_vars=["timestep"],
        value_vars=["price_eur", "price_sib"],
        var_name="region",
        value_name="price",
    )
    fig_price = px.line(
        price_long,
        x="timestep",
        y="price",
        color="region",
        title="Цена энергии",
    )
    st.plotly_chart(fig_price, use_container_width=True)

st.subheader("Добавить новую запись")
with st.form("add_record_form"):
    timestep = st.text_input("Время (YYYY-MM-DD HH:MM)", value="2020-01-01 00:00")
    consumption_eur = st.number_input("Потребление EUR", min_value=0.0, value=1000.0, step=1.0)
    consumption_sib = st.number_input("Потребление SIB", min_value=0.0, value=1000.0, step=1.0)
    price_eur = st.number_input("Цена EUR", min_value=0.0, value=100.0, step=0.1)
    price_sib = st.number_input("Цена SIB", min_value=0.0, value=100.0, step=0.1)
    submit_add = st.form_submit_button("Добавить")

if submit_add:
    add_record(
        {
            "timestep": timestep,
            "consumption_eur": consumption_eur,
            "consumption_sib": consumption_sib,
            "price_eur": price_eur,
            "price_sib": price_sib,
        }
    )

st.subheader("Удалить запись по id")
with st.form("delete_record_form"):
    default_id = int(df["id"].max()) if not df.empty else 1
    record_id = st.number_input("ID записи", min_value=1, value=default_id, step=1)
    submit_delete = st.form_submit_button("Удалить")

if submit_delete:
    remove_record(int(record_id))
