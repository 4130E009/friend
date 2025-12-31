import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="365 日填寫", layout="wide")
st.title("🌱 365 天填寫表")

YEAR = date.today().year
start = date(YEAR, 1, 1)

# 初始化資料
if "data" not in st.session_state:
    days = [start + timedelta(days=i) for i in range(365)]
    st.session_state.data = pd.DataFrame({
        "Day": list(range(1, 366)),
        "Date": [d.strftime("%m/%d") for d in days],
        "Value": [None] * 365
    })

df = st.session_state.data

st.info("每格只能填 1~365，空白代表還沒寫。")

edited = st.data_editor(
    df,
    use_container_width=True,
    disabled=["Day", "Date"],
    column_config={
        "Value": st.column_config.NumberColumn(
            "填寫數字",
            min_value=1,
            max_value=365,
            step=1
        )
    }
)

st.session_state.data = edited

filled = edited["Value"].notna().sum()
st.progress(filled / 365)
st.write(f"已填 {filled} / 365 天")

