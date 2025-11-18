import streamlit as st
import json
import os
import time
import pandas as pd

# =========================
# 設定
# =========================

# 管理密碼（可用環境變數覆蓋）
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "xinadmin")

SCORE_FILE = "scores.json"


# =========================
# 讀取 / 寫入 分數
# =========================

def load_scores():
    if not os.path.exists(SCORE_FILE):
        return []
    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_scores(data):
    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# 題目資料
# =========================

questions = [
    {
        "question": "1. 在以下選項中，你覺得我最在意的是？",
        "options": ["愛情", "友情", "金錢", "健康"],
        "answer": "金錢"
    },
    {
        "question": "2. 你覺得我會因為什麼最容易生氣？",
        "options": ["吵醒我", "不回訊息", "亂答非題", "說我矮"],
        "answer": "吵醒我"
    },
    {
        "question": "3. 我喜歡怎麼樣的人？",
        "options": ["直白", "溫柔", "活潑", "腹黑系"],
        "answer": "直白"
    },
    {
        "question": "4. 我最符合哪種生活步調？",
        "options": ["早起神清氣爽型", "熬夜靈感爆棚型", "隨便啦看心情型", "完全看朋友揪型"],
        "answer": "隨便啦看心情型"
    },
    {
        "question": "5. 如果要選一個一起吃飯的時間，我最可能選？",
        "options": ["中午", "晚上", "半夜", "下午茶"],
        "answer": "半夜"
    },
    {
        "question": "6. 我最常遲到的理由？",
        "options": ["找不到東西", "忘記", "睡過頭", "想買早餐"],
        "answer": "睡過頭"
    },
    {
        "question": "7. 如果今天來一場小旅行，我最可能提議去哪？",
        "options": ["夜市", "電影院", "麻將館", "看海"],
        "answer": "麻將館"
    },
    {
        "question": "8. 如果我中了一點小錢，我會？",
        "options": ["大吃一頓犒賞自己", "出去玩一趟", "先存起來", "買想買很久的東西"],
        "answer": "大吃一頓犒賞自己"
    },
    {
        "question": "9. 我最討厭哪種天氣？",
        "options": ["大太陽", "下雨", "陰天", "颱風"],
        "answer": "大太陽"
    },
    {
        "question": "10. 我最想學的技能？",
        "options": ["彈吉他", "跳舞", "煮飯", "畫畫"],
        "answer": "煮飯"
    }
]


# =========================
# UI 開始
# =========================

st.set_page_config(page_title="友誼測驗", page_icon="⭐", layout="centered")

st.title("🌕 友誼測驗試煉場")
st.write("來吧，看看你到底多懂我。每題一槍，打不中就當作我們重新認識。")


# =========================
# 名字登入
# =========================

if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.username:
    name = st.text_input("先報上名來：")
    if st.button("開始測驗"):
        if name.strip() == "":
            st.warning("欸？名字不用給喔？")
        else:
            st.session_state.username = name
            st.session_state.q_index = 0
            st.session_state.score = 0
    st.stop()


# =========================
# 管理者頁面入口
# =========================

st.sidebar.title("管理")
admin_try = st.sidebar.text_input("管理密碼：", type="password")
if st.sidebar.button("登入"):
    if admin_try == ADMIN_PASSWORD:
        st.sidebar.success("登入成功！去首頁看排行榜區段")
        st.session_state["admin"] = True
    else:
        st.sidebar.error("錯誤的密碼。")

is_admin = st.session_state.get("admin", False)


# =========================
# 題目流程
# =========================

index = st.session_state.q_index
score = st.session_state.score

if index < len(questions):

    q = questions[index]
    st.subheader(q["question"])

    choice = st.radio("你的答案是？", q["options"], index=None)

    if st.button("下一題"):
        if choice is None:
            st.warning("欸？你還沒選喔。")
        else:
            # 判斷答案
            if choice == q["answer"]:
                st.session_state.score += 1

            st.session_state.q_index += 1
            st.rerun()

else:
    # =========================
    # 結束測驗
    # =========================

    st.subheader("🎉 測驗結束！")

    st.write(f"{st.session_state.username}，你的分數是 **{st.session_state.score} / {len(questions)}**")

    # 存分數
    data = load_scores()
    data.append({
        "name": st.session_state.username,
        "score": st.session_state.score,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    save_scores(data)

    # 顯示排行榜
    df = pd.DataFrame(data)
    df = df.sort_values(by="score", ascending=False)

    st.write("## 🏆 排行榜")
    st.dataframe(df.reset_index(drop=True))

    # 重玩按鈕
    if st.button("再玩一次"):
        st.session_state.username = ""
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.rerun()

# =========================
# 管理者模式：瀏覽與清除
# =========================

if is_admin:
    st.write("---")
    st.write("## 🔧 管理者選單（僅你看得到）")

    scores = load_scores()
    st.write("目前資料：")
    st.dataframe(pd.DataFrame(scores))

    if st.button("清除所有紀錄"):
        save_scores([])
        st.success("已清空紀錄！")
