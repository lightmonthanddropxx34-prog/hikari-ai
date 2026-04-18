import streamlit as st
import google.generativeai as genai
import os
import json
from datetime import datetime
from pathlib import Path

# ============================================================================
# ページ設定
# ============================================================================
st.set_page_config(
    page_title="秘書 AI 光",
    layout="centered",
    page_icon="📱",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS スタイル
# ============================================================================
st.markdown("""
    <style>
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    .error-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# ページタイトル
# ============================================================================
st.title("📱 秘書 AI 『光』")
st.caption("あなたの毎日をサポートする、知的でスマートな秘書です。")
# 55行目付近をこのように書き換えると自動認識します
api_key = api_key_input if api_key_input else "ここにあなたのAPIキーを貼り付ける"
# ============================================================================
# 設定とセッション状態の初期化
# ============================================================================

# チャット履歴の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key_set" not in st.session_state:
    st.session_state.api_key_set = False

# ============================================================================
# サイドバー設定
# ============================================================================
with st.sidebar:
    st.title("⚙️ 設定")
    
    st.markdown("""
    ### APIキーの設定
    このアプリを使用するには **Google Gemini APIキー** が必要です。
    """)
    
    # APIキーの入力
    api_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        help="https://aistudio.google.com/app/apikey で取得できます"
    )
    
    # 環境変数からのAPIキー取得
    env_api_key = os.getenv("GEMINI_API_KEY")
    
    # APIキーの優先順位: 入力 > 環境変数
    api_key = api_key_input if api_key_input else env_api_key
    
    if api_key:
        st.session_state.api_key_set = True
        st.markdown('<div class="success-box">✅ APIキーが設定されています</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="error-box">
        ⚠️ APIキーが設定されていません。<br>
        サイドバーから入力するか、環境変数 <code>GEMINI_API_KEY</code> を設定してください。
        </div>
        """, unsafe_allow_html=True)
    
    # チャット履歴の管理
    st.markdown("---")
    st.markdown("### チャット履歴")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 リセット", use_container_width=True):
            st.session_state.messages = []
            st.success("チャット履歴をリセットしました")
            st.rerun()
    
    with col2:
        if st.button("💾 保存", use_container_width=True):
            if st.session_state.messages:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_history_{timestamp}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
                st.success(f"チャット履歴を {filename} に保存しました")
            else:
                st.warning("保存するチャット履歴がありません")
    
    # メッセージ数の表示
    st.markdown(f"**メッセージ数**: {len(st.session_state.messages)}")
    
    # 情報
    st.markdown("---")
    st.markdown("""
    ### 使い方
    1. APIキーを設定
    2. 下のチャット欄に質問を入力
    3. 秘書『光』が知的に答えます
    
    ### 機能
    - 💬 リアルタイムチャット
    - 🧠 会話コンテキスト保持
    - 💾 チャット履歴の保存
    """)

# ============================================================================
# メインチャットエリア
# ============================================================================

# 過去のメッセージを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================================================
# ユーザー入力処理
# ============================================================================

if prompt := st.chat_input("何かお手伝いしましょうか？"):
    if not st.session_state.api_key_set or not api_key:
        st.error("❌ APIキーを設定してください。サイドバーから入力してください。")
    else:
        # ユーザーメッセージを表示・保存
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # アシスタントの応答を生成
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Gemini APIの設定
                genai.configure(api_key=api_key)
                
                # モデルの初期化
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction="""あなたは秘書『光』です。以下の特性を持っています：
- 知的で丁寧な対応
- 簡潔かつ分かりやすい説明
- ユーザーのサポートに徹する
- 必要に応じて詳細な情報を提供
- 敬語を使用した丁寧な言葉遣い
"""
                )
                
                # チャット履歴をコンテキストとして渡す
                chat_history = [
                    {
                        "role": "user" if m["role"] == "user" else "model",
                        "parts": [m["content"]]
                    }
                    for m in st.session_state.messages[:-1]
                ]
                
                chat = model.start_chat(history=chat_history)
                
                # 応答の生成（ストリーミング形式）
                response = chat.send_message(prompt, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                # 最終的な応答を表示
                message_placeholder.markdown(full_response)
                
                # 履歴に保存
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })
                
            except Exception as e:
                error_str = str(e)
                
                # エラーメッセージの分類と対応
                if "leaked" in error_str.lower():
                    error_msg = """
                    ⚠️ **APIキーが無効化されています**
                    
                    設定されているAPIキーは「漏洩」として報告されており、使用できません。
                    
                    **対処方法:**
                    1. [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス
                    2. 新しいAPIキーを生成
                    3. サイドバーから新しいキーを入力
                    """
                    st.error(error_msg)
                
                elif "quota" in error_str.lower():
                    error_msg = """
                    ⚠️ **APIの利用制限に達しました**
                    
                    無料枠の利用制限に達しています。
                    
                    **対処方法:**
                    - しばらく時間をおいてから再度お試しください
                    - または有料プランへのアップグレードを検討してください
                    """
                    st.error(error_msg)
                
                elif "403" in error_str or "permission" in error_str.lower():
                    error_msg = """
                    ⚠️ **認証エラー**
                    
                    APIキーが正しくないか、権限がありません。
                    
                    **対処方法:**
                    1. APIキーが正しく入力されているか確認
                    2. 新しいAPIキーを生成してお試しください
                    """
                    st.error(error_msg)
                
                elif "404" in error_str:
                    error_msg = """
                    ⚠️ **モデルが見つかりません**
                    
                    使用しようとしているモデルが利用できません。
                    
                    **対処方法:**
                    - 別のAPIキーをお試しください
                    - または時間をおいてから再度お試しください
                    """
                    st.error(error_msg)
                
                else:
                    error_msg = f"""
                    ⚠️ **エラーが発生しました**
                    
                    {error_str}
                    
                    **対処方法:**
                    - APIキーを確認してください
                    - ネットワーク接続を確認してください
                    - 時間をおいてから再度お試しください
                    """
                    st.error(error_msg)
                
                # ログに詳細を出力
                print(f"[ERROR] {datetime.now()}: {error_str}")

# ============================================================================
# フッター
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 12px;">
秘書 AI 『光』 | Powered by Google Gemini API | 
<a href="https://aistudio.google.com/app/apikey" target="_blank">Get API Key</a>
</div>
""", unsafe_allow_html=True)
