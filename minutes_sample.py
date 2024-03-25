import streamlit as st
import os
from meeting_minutes_generator import generate_meeting_minutes
from meeting_report import generate_meeting_reports
from openai import OpenAI
from datetime import datetime
import tempfile

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

def main():
    st.title("議事録作成アプリ")
    uploaded_file = st.file_uploader("音声またはテキストファイルをアップロードしてください", type=["mp3", "txt"])

    st.sidebar.title("設定")
    language = st.sidebar.selectbox("言語を選択してください", ("日本語", "English"))
    llm = st.sidebar.selectbox("LLMを選択してください", ("GPT4", "GPT3.5", "Claude3", "Gemma-7B"))
    report_type = st.sidebar.selectbox("書き方を選択してください", ("週報", "議事録", "出張レポート"))

    today = datetime.today().date()
    date = st.sidebar.date_input("日付を入力してください", value=today)
    
    project_number = st.sidebar.selectbox("工事番号を選択してください", ("-", "123A1234", "456B4321"))

    if project_number == '-':
        project_name = '-'
        deadline = '-'
        budget = '-'
        customer_name = '-'       
    elif project_number == '123A1234':
        project_name = "Engine No.7 Annual Inspection"
        deadline = "2024/06/10"
        budget = "5000000 JPY"
        customer_name = "XYZ airways"
    else:
        project_name = "Engine No.43 Periodic Inspection"
        deadline = "2025/02/28"
        budget = "15000000 JPY"
        customer_name = "AAA Company"

    if uploaded_file is not None and project_number:
        if uploaded_file.type == "text/plain":
            # テキストファイルの場合
            try:
                text = uploaded_file.read().decode("utf-8")
            except Exception as e:
                st.error(f"テキストファイルの読み込み中にエラーが発生しました: {e}")
                return
        else:
            # 音声ファイルの場合
            try:
                client = OpenAI()

                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
                    temp.write(uploaded_file.getvalue())
                    temp_file_name = temp.name

                audio_file = open(temp_file_name, "rb")
                transcription = client.audio.transcriptions.create(
                                model="whisper-1", 
                                file=audio_file,
                                response_format = 'text'
                                )
                text = transcription
            except Exception as e:
                st.error(f"音声ファイルの変換中にエラーが発生しました: {e}")
                return


        if st.button("作成"):
            if report_type == '議事録':
                summary = generate_meeting_minutes(text, language, llm, project_name, deadline, budget, customer_name, date)
                st.header("議事録")
                st.write(summary)
            elif report_type == '週報':
                summary = generate_meeting_reports(text, language, llm, project_name, deadline, budget, customer_name, date)
                st.header("週報")
                st.write(summary)
            else:
                summary = generate_event_reports(text, language, llm, project_name, deadline, budget, customer_name, date)
                st.header("出張レポート")
                st.write(summary)

    elif uploaded_file is not None and not project_number:
        st.sidebar.warning("工事番号が記入されていません。")

if __name__ == "__main__":
    main()
