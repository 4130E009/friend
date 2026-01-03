import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, timedelta
import random

# --- 1. 初始化連線 (改用 Google Sheets) ---
st.set_page_config(page_title="365存錢管家", layout="centered")

# 建立連線物件
conn = st.connection("gsheets", type=GSheetsConnection)

# 讀取資料函數 (加上 TTL=0 確保每次都抓最新資料)
def load_data():
    try:
        # 讀取試算表，假設第一欄是 date, 第二欄是 amount
        df = conn.read(ttl=0)
        # 轉成字典格式方便我們原本的邏輯使用 {'2024-01-01': '100'}
        # 確保資料型態正確
        df['date'] = df['date'].astype(str)
        df['amount'] = df['amount'].astype(str)
        return dict(zip(df['date'], df['amount']))
    except Exception as e:
        # 如果試算表是空的或讀取失敗
        return {}

# 儲存資料函數 (寫回 Google Sheets)
def save_data(data_dict):
    # 把字典轉回 DataFrame
    df_new = pd.DataFrame(list(data_dict.items()), columns=['date', 'amount'])
    # 寫入 Google Sheets (這一步會真的存到雲端)
    conn.update(data=df_new)

# --- 2. 介面樣式優化 ---
st.markdown("""
    <style>
    .stTextInput input { padding: 5px 10px !important; font-size: 16px !important; }
    .block-container { padding-top: 1.5rem !important; }
    .dice-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 1px dashed #999; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 365 存錢計畫 (雲端版)")

# 載入資料
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- 3. 核心邏輯：檢查年份內已使用的金額 ---
def get_used_amounts(year):
    used = []
    for date_key, amount in st.session_state.data.items():
        if date_key.startswith(str(year)) and amount.strip().isdigit():
            used.append(int(amount))
    return used

today = date.today()
used_this_year = get_used_amounts(today.year)
total_saved = sum(used_this_year)

st.metric("本年度累計金額", f"${total_saved:,}")

# --- 4. 功能：隨機骰子 ---
with st.expander("🎲 今天不知道存多少？點我擲骰子", expanded=False):
    all_possible = set(range(1, 366))
    remaining = sorted(list(all_possible - set(used_this_year)))
    
    if remaining:
        if st.button("🎲 擲骰子"):
            picked = random.choice(remaining)
            st.session_state.last_dice = picked
        
        if 'last_dice' in st.session_state:
            st.markdown(f"""
                <div class="dice-box">
                    <span style='font-size: 14px; color: #666;'>建議今日金額</span><br>
                    <span style='font-size: 32px; font-weight: bold; color: #ff4b4b;'>${st.session_state.last_dice}</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("恭喜！你已經完成今年的所有存錢目標了！")

# --- 5. 日期區段選擇 ---
view_mode = st.radio("顯示模式", ["最近 7 天", "按月查看"], horizontal=True)

display_days = []
if view_mode == "最近 7 天":
    display_days = [today - timedelta(days=i) for i in range(7)]
else:
    c1, c2 = st.columns(2)
    with c1: year = st.selectbox("年", range(2025, 2030), index=0)
    with c2: month = st.selectbox("月", range(1, 13), index=today.month - 1)
    import calendar
    cal = calendar.Calendar()
    display_days = [d for d in cal.itermonthdates(year, month) if d.month == month]

# --- 6. 渲染列表與檢查邏輯 ---
st.divider()

for day in display_days:
    key = day.isoformat()
    is_today = (day == today)
    current_val = st.session_state.data.get(key, "")
    
    col_date, col_input = st.columns([2, 3])
    
    with col_date:
        date_str = day.strftime("%m/%d")
        weekday = ["一", "二", "三", "四", "五", "六", "日"][day.weekday()]
        label = f"**{date_str}** (週{weekday})"
        st.markdown(f"<span style='color:{'#ff4b4b' if is_today else '#333'};'>{'● ' if is_today else ''}{label}</span>", unsafe_allow_html=True)
    
    with col_input:
        input_val = st.text_input(label=f"in_{key}", value=current_val, key=f"v_{key}", placeholder="1~365", label_visibility="collapsed")
        
        if input_val != current_val:
            # 這裡增加一個載入中提示，因為連線 Google Sheets 需要約 1-2 秒
            with st.spinner('正在同步到 Google 雲端...'):
                if input_val == "":
                    st.session_state.data.pop(key, None)
                    save_data(st.session_state.data) # 存到雲端
                    st.rerun()
                elif input_val.isdigit():
                    val_int = int(input_val)
                    if not (1 <= val_int <= 365):
                        st.error("請輸入 1~365")
                    elif val_int in used_this_year and str(val_int) != current_val:
                        st.error(f"數字 {val_int} 今年已經存過囉！")
                    else:
                        st.session_state.data[key] = input_val
                        save_data(st.session_state.data) # 存到雲端
                        st.success("已儲存！")
                        st.rerun()
    st.markdown("---")
