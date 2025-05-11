#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import json
import os
from datetime import datetime

# ユーザーデータを保存するファイル
USER_FILE = "users.json"

# 各ユーザーのログ保存ディレクトリ
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ユーザーデータの読み書き

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# ログイン状態を管理する
if "user" not in st.session_state:
    st.session_state.user = None

# ページ記憶がなければログインに初期化
if "page" not in st.session_state:
    st.session_state.page = "ログイン"

# ページ一覧と現在ページ選択
pages = ["ログイン", "新規登録", "愛ポイント", "ログを見る"]
menu = st.sidebar.selectbox("メニューを選んでね", pages, index=pages.index(st.session_state.page))

users = load_users()

# 新規登録
if menu == "新規登録":
    st.header("📝 新規登録")
    email = st.text_input("メールアドレス")
    password = st.text_input("パスワード", type="password")
    nickname = st.text_input("ニックネーム")
    if st.button("登録する"):
        if email in users:
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
            st.session_state.page = "愛ポイント"  # ★ 自動遷移設定
            st.success(f"{users[email]['nickname']}さん、ようこそ💖")
            st.rerun()  # ★ 再読み込みで自動遷移反映
        else:
            st.error("メールアドレスまたはパスワードが違います")

# 愛ポイントページ
elif menu == "愛ポイント":
    if st.session_state.user is None:
        st.warning("ログインしてください")
    else:
        user = users[st.session_state.user]
        st.header(f"💖 {user['nickname']}の愛ポイント")
        if st.button("愛してるyo💘"):
            user["points"] += 1
            save_users(users)
            # ログ保存
            with open(os.path.join(LOG_DIR, f"{st.session_state.user}.txt"), "a") as f:
                f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - 愛してるyo\n")
            st.success("1 愛ポイント加算されました！")
        st.markdown(f"### 現在の愛ポイント：{user['points']}")

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

