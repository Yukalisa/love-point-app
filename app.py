import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

# Google Sheets 認証設定（secretsから取得）
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gspread"]
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
client = gspread.authorize(CREDS)

# スプレッドシートの読み込み関数
def load_sheet():
    return client.open_by_url("https://docs.google.com/spreadsheets/d/1It2O3TFIM64p2wKaYhraukLk0uEAsHWssfdlz_jsnBI/edit").sheet1

# 各ユーザーのログ保存ディレクトリ（ここはローカルのまま）
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# スプレッドシートからユーザーを読み込む
def load_users():
    users = {}
    try:
        sheet = load_sheet()
        data = sheet.get_all_records()
        for row in data:
            users[row["email"]] = {
                "password": row["password"],
                "nickname": row["nickname"],
                "points": int(row["points"])
            }
    except Exception as e:
        st.error("ユーザーデータの読み込みに失敗しました。しばらくしてから再度お試しください。")
        st.stop()
    return users

# ユーザー情報を保存（全データを書き換える方式）
def save_users(users):
    try:
        sheet = load_sheet()
        sheet.clear()
        sheet.append_row(["email", "password", "nickname", "points"])
        for email, info in users.items():
            sheet.append_row([email, info["password"], info["nickname"], info["points"]])
    except Exception as e:
        st.error("ユーザーデータの保存に失敗しました。")

# ログイン状態を管理する
if "user" not in st.session_state:
    st.session_state.user = None

# ページ記憶がなければログインに初期化
if "page" not in st.session_state:
    st.session_state.page = "ログイン"

# ページ一覧と現在ページ選択
pages = ["ログイン", "新規登録", "愛してるyoポイント", "ログを見る", "設定"]
menu = st.sidebar.selectbox("メニューを選んでね", pages, index=pages.index(st.session_state.page))

users = load_users()

# 新規登録
if menu == "新規登録":
    st.header("📝 新規登録")
    email = st.text_input("メールアドレス")
    password = st.text_input("パスワード", type="password")
    nickname = st.text_input("ニックネーム")
    if st.button("登録する"):
        if not email.strip():
            st.warning("メールアドレスを入力してください")
        elif not password.strip():
            st.warning("パスワードを入力してください")
        elif email in users:
            st.warning("そのメールアドレスはすでに登録されています")
        else:
            users[email] = {"password": password, "nickname": nickname, "points": 0}
            save_users(users)
            st.success("登録が完了しました！ログインしてください")

# ログイン
elif menu == "ログイン":
    st.header("🔐 ログイン")
    email = st.text_input("メールアドレス")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        if email in users and users[email]["password"] == password:
            st.session_state.user = email
            st.session_state.page = "愛してるyoポイント"
            st.success(f"{users[email]['nickname']}さん、ようこそ💖")
            st.rerun()
        else:
            st.error("メールアドレスまたはパスワードが違います")

# 愛してるyoポイントページ
elif menu == "愛してるyoポイント":
    if st.session_state.user is None:
        st.warning("ログインしてください")
    else:
        user = users[st.session_state.user]
        st.header(f"💖 {user['nickname']}の愛してるyoポイント")
        if st.button("愛してるyo💘"):
            user["points"] += 1
            save_users(users)
            with open(os.path.join(LOG_DIR, f"{st.session_state.user}.txt"), "a") as f:
                f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - 愛してるyo\n")
            st.success("1 愛してるyoポイント加算されました！")
        st.markdown(f"### 現在の愛してるyoポイント：{user['points']}")

# ログページ
elif menu == "ログを見る":
    if st.session_state.user is None:
        st.warning("ログインしてください")
    else:
        st.header("📜 あなたの愛ログ")
        log_path = os.path.join(LOG_DIR, f"{st.session_state.user}.txt")
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                logs = f.readlines()
                for log in logs[-10:][::-1]:
                    st.write(log.strip())
        else:
            st.info("まだ愛してるyoを押してないみたい…")

# 設定ページ（アカウント削除）
elif menu == "設定":
    if st.session_state.user:
        st.header("⚙️ アカウント設定")
        st.warning("この操作は取り消せません。アカウントを削除するにはパスワードを入力してください。")
        password = st.text_input("パスワード", type="password")
        if st.button("アカウントを削除する"):
            current_email = st.session_state.user
            if users[current_email]["password"] == password:
                users.pop(current_email)
                save_users(users)
                with open(os.path.join(LOG_DIR, "delete_log.txt"), "a") as f:
                    f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + f" - {current_email} アカウント削除\n")
                st.session_state.user = None
                st.session_state.page = "ログイン"
                st.success("アカウントを削除しました。またいつでも戻ってきてね！")
                st.rerun()
            else:
                st.error("パスワードが間違っています")
