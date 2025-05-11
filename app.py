import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# --- Secrets and Sheets ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gspread"]
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
client = gspread.authorize(CREDS)

USER_SHEET_URL = st.secrets["gspread"]["user_sheet_url"]
POINT_LOG_SHEET_URL = st.secrets["gspread"]["point_log_sheet_url"]

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# --- Load Sheets ---
def load_user_sheet():
    return client.open_by_url(USER_SHEET_URL).sheet1

def load_point_log_sheet():
    return client.open_by_url(POINT_LOG_SHEET_URL).sheet1

# --- Load and Save Users ---
def load_users():
    users = {}
    try:
        sheet = load_user_sheet()
        data = sheet.get_all_records()
        for row in data:
            users[row["email"]] = {
                "password": row["password"],
                "nickname": row["nickname"],
                "points": int(row["points"] or 0)
            }
    except Exception as e:
        st.error("ユーザーデータの読み込みに失敗しました。")
        st.stop()
    return users

def save_users(users):
    try:
        sheet = load_user_sheet()
        sheet.clear()
        sheet.append_row(["email", "password", "nickname", "points"])
        for email, info in users.items():
            sheet.append_row([email, info["password"], info["nickname"], info["points"]])
    except Exception as e:
        st.error("ユーザーデータの保存に失敗しました。")

# --- Logging ---
def append_point_log(email):
    try:
        sheet = load_point_log_sheet()
        sheet.append_row([email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    except:
        st.warning("ポイントの記録に失敗しましたが、ポイントは加算されています")

# --- Authentication Setup ---

# 🔍 デバッグボタンでcredentials表示
if st.sidebar.button("🔎 デバッグ表示（ログインデータ）"):
    tmp_users = load_users()
    tmp_credentials = {
        email: {
            "email": email,
            "name": user_data["nickname"],
            "password": [user_data["password"]]
        } for email, user_data in tmp_users.items()
    }
    st.write(tmp_credentials)
users = load_users()
credentials = {
    "credentials": {
        "usernames": {
            email: {
                "email": email,
                "name": user_data["nickname"],
                "password": [user_data["password"]]
            } for email, user_data in users.items()
        }
    }
}

authenticator = stauth.Authenticate(
    credentials["credentials"],
    "love_point_app",
    "abcdef",  # cookie key
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login("ログイン", location="main")

# --- App Logic ---
if authentication_status:
    st.sidebar.success(f"{name} さんでログイン中")
    authenticator.logout("ログアウト", "sidebar")
    st.session_state.user = username

    # デフォルトページを愛してるyoポイントに設定
    if "menu" not in st.session_state:
        st.session_state.menu = "愛してるyoポイント"

    pages = ["愛してるyoポイント", "ログを見る", "設定"]
    menu = st.sidebar.selectbox("メニューを選んでね", pages, index=pages.index(st.session_state.menu))
    st.session_state.menu = menu

    # 愛してるyoポイント
    if menu == "愛してるyoポイント":
        user = users[username]
        st.header(f"💖 {user['nickname']}の愛してるyoポイント")
        if st.button("愛してるyo💘"):
            user["points"] += 1
            save_users(users)
            append_point_log(username)
            with open(os.path.join(LOG_DIR, f"{username}.txt"), "a") as f:
                f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - 愛してるyo\n")
            st.success("1 愛してるyoポイント加算されました！")
        st.markdown(f"### 現在の愛してるyoポイント：{user['points']}")

    # ログ
    elif menu == "ログを見る":
        st.header("📜 あなたの愛ログ")
        log_path = os.path.join(LOG_DIR, f"{username}.txt")
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                logs = f.readlines()
                for log in logs[-10:][::-1]:
                    st.write(log.strip())
        else:
            st.info("まだ愛してるyoを押してないみたい…")

    # 設定
    elif menu == "設定":
        st.header("⚙️ アカウント設定")
        st.warning("この操作は取り消せません。アカウントを削除するにはパスワードを入力してください。")
        password = st.text_input("パスワード", type="password")
        if st.button("アカウントを削除する"):
    import bcrypt
    if bcrypt.checkpw(password.encode(), users[username]["password"].encode()):
                users.pop(username)
                save_users(users)
                with open(os.path.join(LOG_DIR, "delete_log.txt"), "a") as f:
                    f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + f" - {username} アカウント削除\n")
                st.success("アカウントを削除しました！")
                st.rerun()
            else:
                st.error("パスワードが違います")

elif authentication_status is False:
    st.error("メールアドレスまたはパスワードが違います")

elif authentication_status is None:
    st.info("ログインしてください")
