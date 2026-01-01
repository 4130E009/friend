import streamlit as st
from datetime import date, timedelta
import json
import os

DATA_FILE = "savings_data.json"

# --- 1. 資料處理 ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- 2. 手機版樣式優化 ---
st.set_page_config(page_title="存錢管家", layout="centered") # 使用 centered 更適合手機

st.markdown("""
    <style>
    /* 讓輸入框更矮一點，並加大字體方便觸控 */
    .stTextInput input {
        padding: 5px 10px !important;
        font-size: 16px !important;
    }
    /* 隱藏 Streamlit 預設的上邊距 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 標題與統計 ---
st.title("💰 365 存錢計畫")

total_saved = sum(int(v) for v in st.session_state.data.values() if str(v).isdigit())
st.metric("目前累計金額", f"${total_saved:,}")

# --- 4. 日期區段選擇 ---
# 手機版不適合顯示整個月，我們改用「切換週」或「直接選日期」
today = date.today()
view_mode = st.radio("顯示模式", ["最近 7 天", "按月查看"], horizontal=True)

display_days = []

if view_mode == "最近 7 天":
    # 顯示今天及前六天，最適合手機快速輸入
    display_days = [today - timedelta(days=i) for i in range(7)]
else:
    # 按月查看
    c1, c2 = st.columns(2)
    with c1:
        year = st.selectbox("年", range(2024, 2030), index=0)
    with c2:
        month = st.selectbox("月", range(1, 13), index=today.month - 1)
    
    import calendar
    cal = calendar.Calendar()
    # 只抓取該月有日期的部分
    display_days = [d for d in cal.itermonthdates(year, month) if d.month == month]

# --- 5. 渲染列表 (清單式在手機上最好操作) ---
st.divider()

for day in display_days:
    key = day.isoformat()
    is_today = (day == today)
    
    # 使用容器包裝每一行
    with st.container():
        # 用 2:3 的比例分配日期與輸入框
        col_date, col_input = st.columns([2, 3])
        
        with col_date:
            date_str = day.strftime("%m/%d")
            weekday = ["一", "二", "三", "四", "五", "六", "日"][day.weekday()]
            label = f"**{date_str}** (週{weekday})"
            if is_today:
                st.markdown(f"<span style='color:#ff4b4b;'>● {label}</span>", unsafe_allow_html=True)
            else:
                st.markdown(label)
        
        with col_input:
            current_val = st.session_state.data.get(key, "")
            input_val = st.text_input(
                label=f"input_{key}",
                value=current_val,
                key=f"in_{key}",
                placeholder="輸入金額",
                label_visibility="collapsed"
            )
            
            # 存檔邏輯
            if input_val != current_val:
                if input_val == "" or (input_val.isdigit() and 1 <= int(input_val) <= 365):
                    if input_val == "":
                        st.session_state.data.pop(key, None)
                    else:
                        st.session_state.data[key] = input_val
                    save_data(st.session_state.data)
                    st.rerun()
    st.markdown("---") # 分隔線增加辨識度
