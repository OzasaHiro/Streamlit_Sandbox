import streamlit as st
from openai import OpenAI
import anthropic
import replicate
import os

def generate_meeting_minutes(text, language, llm, project_name, deadline, budget, customer_name, date):
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
    REPLICATE_API_TOKEN=st.secrets["REPLICATE_API_TOKEN"]

    if llm == "GPT4":
        LLM = 'gpt-4-0125-preview'
    elif llm == "GPT3.5":
        LLM = 'gpt-3.5-turbo-0125'
    elif llm == 'Claude3':
        LLM = 'claude-3-sonnet-20240229' #'claude-3-sonnet-20240229','claude-3-opus-20240229'

    summary_prompt = f"""
        Please create a meeting minutes based on the following information:\
        Project Information:\
        Project Name: {project_name}\
        Deadline: {deadline}\
        Budget: {budget}\
        Customer Name: {customer_name}\
        Date: {date}\
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
    summary_prompt_j = f"""
        以下の情報に基づいて、会議の議事録を作成してください。\
        
        プロジェクト情報:\
        プロジェクト名: {project_name}\
        締め切り: {deadline}\
        予算: {budget}\
        顧客名: {customer_name} \
        日付: {date}\
        会議の文字起こし: {text}\
        
        議事録の構成:\
        
        1. 概要\
        - 会議の目的、日時、場所、出席者を簡潔にまとめてください。\
        - プロジェクト情報（プロジェクト名、締め切り、予算、顧客名）を整理して含めてください。\
        2. 議題と討議内容\
        - 会議で討議された主な議題を箇条書きで列挙してください。\
        - 各議題の討議内容を要約してください。\
        - 重要な決定事項や合意事項は明確に記載してください。\
        3. 課題と懸念事項\
        - 会議で提起された課題や懸念事項を整理して文書化してください。\
        - プロジェクトの締め切りや予算に関する課題があれば、具体的に言及してください。\
        4. アクションアイテム\
        - 会議で決定されたアクションアイテムを列挙してください。\
        - 各アクションアイテムについて、担当者と期限を明記してください。\
        5. 次回会議\
        - 次回会議の日時、場所、議題を記載してください。\
        
        議事録を作成する際は、以下の点に留意してください:\
        - 会議の全体的な流れと結論が明確にまとめられていること。\
        - 重要な発言や決定事項については、発言者を記載すること。\
        - 言葉を簡潔かつ正確に使い、あいまいな表現を避けること。\
        - プロジェクト情報と会議内容を関連付けて、議事録の内容を充実させること。\
        それでは、議事録の作成を進めてください。\
        """


    
    if language == "日本語":
        prompt = summary_prompt+"日本語で記入してください。"
        prompt_gemma = summary_prompt_j
        user_request = {'role': 'assistant', 'content': prompt}
    else:
        prompt = summary_prompt+"Write in English."
        prompt_gemma = summary_prompt
        user_request = {'role': 'assistant', 'content': prompt}

    if llm == 'Claude3':
        client = anthropic.Anthropic()
        summary_result = client.messages.create(
                    model=LLM,
                    max_tokens=1000,
                    temperature=0.0,
                    system="あなたは優秀なAIアシスタントです。",
                    messages=[{'role': 'user', 'content': prompt}]
                )
        summary = summary_result.content[0].text

    elif llm == 'Gemma-7B':
        summary_result = replicate.run(
                    "google-deepmind/gemma-7b-it:2790a695e5dcae15506138cc4718d1106d0d475e6dca4b1d43f42414647993d5",
                    input={
                        "top_k": 50,
                        "top_p": 0.95,
                        "prompt": prompt_gemma,
                        "temperature": 0.01,
                        "max_new_tokens":1000,
                        "min_new_tokens": 10,
                        "repetition_penalty": 1
                    }
                )
        output_list = []
        for item in summary_result:
            output_list.append(item)
        
        summary = "".join(output_list)
        
    else:
        client = OpenAI()
        summary_result = client.chat.completions.create(model=LLM, messages=[user_request], max_tokens=1000)
        summary = summary_result.choices[0].message.content.strip()
    return summary
