import streamlit as st
import google.generativeai as genai

# システム設定
genai.configure(api_key="AIzaSyCInixR-c-RNV1coAz3r1JaQRdvpALUx6g")
model = genai.GenerativeModel('gemini-1.5-flash-latest')
# アプリの見た目設定
st.set_page_config(page_title="秘書 AI 光", layout="centered")
st.title("📱 秘書 AI 『光』")

                              
# チャット履歴を保持
if "history" not in st.session_state:
    st.session_state.history = []

# 命令入力欄
if prompt := st.chat_input("何かお手伝いしましょうか？"):
    st.session_state.history.append({"role": "user", "content": prompt})
    response = model.generate_content(f"あなたは秘書『光』です。知的に短く答えて。\nユーザー：{prompt}")
    st.session_state.history.append({"role": "assistant", "content": response.text})

# 会話を表示
for chat in st.session_state.history:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])
