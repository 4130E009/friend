import streamlit as st
import calendar
from datetime import date
import json
import os

DATA_FILE = "data.json"

# 讀資料
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {}

st.set_page_config(page_title="存錢行事曆", layout="wide")
st.title("📅 存錢行事曆")

today = date.today()
year = st.selectbox("年份", range(2020, 2035), index=range(2020,2035).index(today.year))
month = st.selectbox("月份", range(1, 13), index=today.month - 1)

cal = calendar.Calendar()
month_days = list(cal.itermonthdates(year, month))

# 每頁固定 5x7 = 35 格
month_days = month_days[:35]

cols = st.columns(7)

for i, day in enumerate(month_days):
    col = cols[i % 7]

    key = day.isoformat()

with col:
    st.markdown(
        f"""
        <div style="
            border:1px solid #ccc;
            border-radius:8px;
            padding:6px;
            height:90px;
            font-size:14px;
            text-align:center;
            background-color:{'#f0f8ff' if day == today else '#ffffff'};
        ">
        <b>{day.day}</b>
        """,
        unsafe_allow_html=True,
    )


        val = data.get(key, "")
        input_val = st.text_input("", val, key=key)

        # 驗證
        if input_val != "":
            if input_val.isdigit() and 1 <= int(input_val) <= 365:
                data[key] = input_val
            else:
                st.warning("只能輸入 1~365")

        st.markdown("</div>", unsafe_allow_html=True)

# 存檔
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

st.caption("💾 自動儲存完成")


