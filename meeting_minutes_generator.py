import streamlit as st
from openai import OpenAI
import anthropic
import replicate
import os

def generate_meeting_minutes(text, language, llm, project_name, deadline, budget, customer_name):
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
    REPLICATE_API_TOKEN=st.secrets["REPLICATE_API_TOKEN"]

    if llm == "GPT4":
        LLM = 'gpt-4-0125-preview'
    elif llm == "GPTGPT3.5":
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
        prompt = summary_prompt+"日本語で記入してください。"
        user_request = {'role': 'assistant', 'content': prompt}
    else:
        prompt = summary_prompt+"Write in English."
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
                        "prompt": prompt,
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
