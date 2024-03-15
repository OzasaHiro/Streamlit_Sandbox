import streamlit as st
from openai import OpenAI
import os

OpenAI.set_api_key(st.secrets["OPENAI_API_KEY"])
client = OpenAI()


def generate_meeting_minutes(text, language, llm, project_name, deadline, budget, customer_name):
    if llm == "GPT4":
        LLM = 'gpt-4-0125-preview'
    else:
        LLM = 'gpt-3.5-turbo-0125'

    summary_prompt = f"""\
        Please create a meeting minutes based on the following information:\

        Project Information:\
        Project Name: {project_name}\
        Deadline: {deadline}\
        Budget: {budget}\
        Customer Name: {customer_name}\
        Meeting Transcription: {text}\

        Structure of the Meeting Minutes:\
        1. Overview\
        - Summarize the purpose, date, location, and attendees of the meeting concisely.\
        - Organize and include the project information (project name, deadline, budget, customer name).\

        2. Agenda and Discussion Points\
        - List the main agenda items discussed during the meeting in bullet points.\
        - Summarize the content of the discussion for each agenda item.\
        - Clearly state any important decisions or agreements made.\

        3. Issues and Concerns\
        - Organize and document the issues and concerns raised during the meeting.\
        - If there are any issues related to the project's deadline or budget, mention them specifically.\

        4. Action Items\
        - List the action items decided upon during the meeting.\
        - For each action item, specify the person responsible and the deadline.\

        5. Next Meeting\
        - Note the date, location, and agenda for the next meeting.\

        When creating the meeting minutes, please keep the following points in mind:\
        - Ensure that the overall flow and conclusion of the meeting are clearly summarized.\
        - Mention the speaker for important statements or decisions made.\
        - Keep the language concise and accurate, avoiding ambiguous expressions.\
        - Enrich the content of the meeting minutes by relating the project information to the meeting content.\

        Please proceed with creating the meeting minutes.\
        """
    
    if language == "日本語":
        user_request = {'role': 'assistant', 'content': summary_prompt+"日本語で記入してください。"}
    else:
        user_request = {'role': 'assistant', 'content': summary_prompt+"Write in English."}

    summary_result = client.chat.completions.create(model=LLM, messages=[user_request], max_tokens=1000)
    summary = summary_result.choices[0].message.content.strip()
    
    return summary

def main():
    st.title("議事録作成アプリ")
    
    uploaded_file = st.file_uploader("テキストファイルをアップロードしてください", type="txt")

    st.sidebar.title("設定")
    language = st.sidebar.selectbox("言語を選択してください", ("日本語", "English"))
    llm = st.sidebar.selectbox("LLMを選択してください", ("GPT4", "GPT3.5"))
    project_number = st.sidebar.selectbox("工事番号を選択してください", ("123A1234", "456B4321"))
    
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
        
        if st.button("議事録を作成"):
            summary = generate_meeting_minutes(text, language, llm, project_name, deadline, budget, customer_name)
            
            st.header("議事録")
            st.write(summary)


    elif uploaded_file is not None and not project_number:
        st.sidebar.warning("工事番号が記入されていません。")

if __name__ == "__main__":
    main()
