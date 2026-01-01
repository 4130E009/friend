import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os

st.set_page_config(page_title="365 時間盒", layout="wide")
st.title("🗓️ 365 天時間盒")

YEAR = date.today().year
start = date(YEAR, 1, 1)
DATA_FILE = "data_365.csv"

def create_initial():
    days = [start + timedelta(days=i) for i in range(365)]
    return pd.DataFrame({
        "Date": [d.strftime("%m/%d") for d in days],
        "Value": [None] * 365
    })

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = create_initial()

st.markdown("""
<style>
input[type="number"] {
    width: 60px !important;
    padding: 2px !important;
}
.box {
    text-align: center;
    font-size: 11px;
    color: #666;
}
</style>
""", unsafe_allow_html=True)

cols_per_row = 73
updated = []

for r in range(5):
    cols = st.columns(cols_per_row)
    for c in range(cols_per_row):
        idx = r * cols_per_row + c
        if idx >= 365:
            continue

        with cols[c]:
            st.markdown(f"<div class='box'>{df.loc[idx, 'Date']}</div>", unsafe_allow_html=True)
            new_val = st.number_input(
                label="",
                min_value=1,
                max_value=365,
                step=1,
                value=int(df.loc[idx, "Value"]) if pd.notna(df.loc[idx, "Value"]) else 1,
                key=f"v_{idx}"
            )
            updated.append(new_val)

df["Value"] = updated
df.to_csv(DATA_FILE, index=False)

filled = df["Value"].notna().sum()
st.progress(filled / 365)
st.write(f"已填 {filled} / 365 天")
