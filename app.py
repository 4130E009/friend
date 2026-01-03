import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import date, timedelta
import random

# --- 1. 設定頁面 ---
st.set_page_config(page_title="365存錢管家", layout="centered")

# --- 2. 建立 Google Sheets 連線 (手動穩固版) ---
def get_google_sheet_data():
    # 定義連線範圍
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # 讀取 Secrets (注意：這裡會去解析你那串 JSON 文字)
    json_info = json.loads(st.secrets["connections"]["gsheets"]["service_account_info"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_info, scope)
    
    # 連線
    client = gspread.authorize(creds)
    
    # 開啟試算表 (從 Secrets 讀取網址)
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet = client.open_by_url(sheet_url).sheet1
    return sheet

# 嘗試連線
try:
    sheet = get_google_sheet_data()
except Exception as e:
    st.error(f"連線失敗，請檢查 Secrets 設定: {e}")
    st.stop()

# --- 3. 讀寫資料函數 ---
def load_data():
    try:
        # 抓取所有紀錄 (get_all_records 會自動把第一行當標題)
        data = sheet.get_all_records()
        # 轉成字典格式 {'2024-01-01': '100'}
        data_dict = {}
        for item in data:
            # 確保轉成字串
            d = str(item['date'])
            a = str(item['amount'])
            if d and a:
                data_dict[d] = a
        return data_dict
    except Exception as e:
        return {}

def save_data(date_str, amount_str):
    # 寫入 Google Sheets (append_row 直接加在最後一行)
    # 為了避免重複，我們先讀取再判斷，或是簡單地直接 append (這裡示範 append)
    # 但為了符合你原本的邏輯(修改舊資料)，我們先用簡單的「重新整理」邏輯不好寫，
    # 所以我們改用：每次讀取 -> 在本地修改 -> 這裡只示範「新增」或簡單處理
    # *為了效能，我們這裡做一個簡單的寫入：直接附加到最後一行*
    # *如果你要修改舊資料，建議還是用原本的邏輯比較好，但 gspread 操作比較細*
    
    # 修正策略：因為 gspread 寫入較慢，我們用簡單的方式：
    # 每次存檔時，先刪除舊資料，再重寫 (資料量少時沒問題)
    
    try:
        # 清空工作表 (保留第一行標題)
        sheet.clear()
        sheet.append_row(["date", "amount"]) # 補回標題
        
        # 把 session_state 的資料轉成 list 寫入
        rows = []
        for k, v in st.session_state.data.items():
            rows.append([k, v])
        
        # 一次寫入多行 (比一行一行寫快)
        if rows:
            sheet.append_rows(rows)
            
    except Exception as e:
        st.error(f"存檔失敗: {e}")

# --- 4. 介面與邏輯 (與之前相同) ---
st.markdown("""
    <style>
    .stTextInput input { padding: 5px 10px !important; font-size: 16px !important; }
    .block-container { padding-top: 1.5rem !important; }
    .dice-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 1px dashed #999; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 365 存錢計畫 (雲端版)")

# 初始化資料
if 'data' not in st.session_state:
    with st.spinner('正在從 Google 雲端下載資料...'):
        st.session_state.data = load_data()

# 統計
today = date.today()
def get_used_amounts(year):
    used = []
    for date_key, amount in st.session_state.data.items():
        if date_key.startswith(str(year)) and str(amount).isdigit():
            used.append(int(amount))
    return used

used_this_year = get_used_amounts(today.year)
total_saved = sum(used_this_year)
st.metric("本年度累計金額", f"${total_saved:,}")

# 骰子功能
with st.expander("🎲 今天不知道存多少？點我擲骰子", expanded=False):
    all_possible = set(range(1, 366))
    remaining = sorted(list(all_possible - set(used_this_year)))
    if remaining:
        if st.button("🎲 擲骰子"):
            picked = random.choice(remaining)
            st.session_state.last_dice = picked
        if 'last_dice' in st.session_state:
            st.markdown(f"""<div class="dice-box"><span style='font-size: 14px; color: #666;'>建議今日金額</span><br><span style='font-size: 32px; font-weight: bold; color: #ff4b4b;'>${st.session_state.last_dice}</span></div>""", unsafe_allow_html=True)
    else:
        st.success("恭喜！完成今年目標！")

# 日期選單
view_mode = st.radio("顯示模式", ["最近 7 天", "按月查看"], horizontal=True)
if view_mode == "最近 7 天":
    display_days = [today - timedelta(days=i) for i in range(7)]
else:
    c1, c2 = st.columns(2)
    with c1: year = st.selectbox("年", range(2025, 2030), index=0)
    with c2: month = st.selectbox("月", range(1, 13), index=today.month - 1)
    import calendar
    cal = calendar.Calendar()
    display_days = [d for d in cal.itermonthdates(year, month) if d.month == month]

st.divider()

# 列表顯示
for day in display_days:
    key = day.isoformat()
    is_today = (day == today)
    current_val = str(st.session_state.data.get(key, ""))
    
    col_date, col_input = st.columns([2, 3])
    with col_date:
        date_str = day.strftime("%m/%d")
        weekday = ["一", "二", "三", "四", "五", "六", "日"][day.weekday()]
        label = f"**{date_str}** (週{weekday})"
        st.markdown(f"<span style='color:{'#ff4b4b' if is_today else '#333'};'>{'● ' if is_today else ''}{label}</span>", unsafe_allow_html=True)
    
    with col_input:
        input_val = st.text_input(label=f"in_{key}", value=current_val, key=f"v_{key}", placeholder="1~365", label_visibility="collapsed")
        
        if input_val != current_val:
            with st.spinner('正在同步到 Google 雲端...'):
                if input_val == "":
                    st.session_state.data.pop(key, None)
                elif input_val.isdigit():
                    val_int = int(input_val)
                    if not (1 <= val_int <= 365):
                        st.error("請輸入 1~365")
                    elif val_int in used_this_year and str(val_int) != current_val:
                        st.error(f"數字 {val_int} 今年已經存過囉！")
                    else:
                        st.session_state.data[key] = input_val
                        save_data(key, input_val) # 執行存檔
                        st.success("已儲存！")
                        st.rerun()
    st.markdown("---")
