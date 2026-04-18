app.py
import streamlit as st
import google.generativeai as genai

# システム設定
genai.configure(api_key="AQ.Ab8RN6Lgd4S76wWOztx_samT6OLrfKP4D6fsET7zMFv5c8RaJQ")
model = genai.GenerativeModel('gemini-1.5-flash')

# アプリの見た目設定
st.set_page_config(page_title="秘書 AI 光", layout="centered")
st.title("📱 秘書 AI 『光』")

# チャット履歴を保持する仕組み
if "history" not in st.session_state:
    st.session_state.history = []

# 命令入力欄
if prompt := st.chat_input("Command..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    
    # 秘書「光」の応答生成
    response = model.generate_content(f"あなたは秘書『光』です。知的に短く答えて。\\nユーザー：{prompt}")
    st.session_state.history.append({"role": "assistant", "content": response.text})

# 画面に会話を表示
for chat in st.session_state.history:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])
