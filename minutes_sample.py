import streamlit as st
import os
from meeting_minutes_generator import generate_meeting_minutes
from meeting_report import generate_meeting_reports

def main():
    st.title("議事録作成アプリ")
    uploaded_file = st.file_uploader("テキストファイルをアップロードしてください", type="txt")
    st.sidebar.title("設定")
    language = st.sidebar.selectbox("言語を選択してください", ("日本語", "English"))
    llm = st.sidebar.selectbox("LLMを選択してください", ("GPT4", "GPT3.5"))
    project_number = st.sidebar.selectbox("工事番号を選択してください", ("123A1234", "456B4321"))
    report_type = st.sidebar.selectbox("書き方を選択してください", ("週報", "議事録"))

    if project_number == '123A1234':
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
        text = uploaded_file.read().decode("utf-8")
        if st.button("作成"):
            openai_api_key = st.secrets["OPENAI_API_KEY"]
            if report_type == '議事録':
                summary = generate_meeting_minutes(text, language, llm, project_name, deadline, budget, customer_name, openai_api_key)
                st.header("議事録")
                st.write(summary)
            else:
                summary = generate_meeting_reports(text, language, llm, project_name, deadline, budget, customer_name, openai_api_key)
                st.header("週報")
                st.write(summary)
    elif uploaded_file is not None and not project_number:
        st.sidebar.warning("工事番号が記入されていません。")

if __name__ == "__main__":
    main()