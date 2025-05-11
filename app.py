...
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
...
