import streamlit as st
from openai import OpenAI
import anthropic
import os

def generate_meeting_minutes(text, language, llm, project_name, deadline, budget, customer_name):
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

    if llm == "GPT4":
        LLM = 'gpt-4-0125-preview'
    elif llm == "GPT3.5":
        LLM = 'gpt-3.5-turbo-0125'
    else:
        LLM = 'claude-3-sonnet-20240229'

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
    (1) ...\
    
    (2) ...\
    
    2. Agenda and Discussion Points\
    (1) ...\
    
    (a) ...\
    
    (b) ...\
    
    (2) ...\
    
    (a) ...\
    
    (b) ...\
    
    3. Issues and Concerns\
    (1) ...\
    
    (2) ...\
    
    4. Action Items\
    (1) ...\
    
    (a) ...\
    
    (b) ...\
    
    (2) ...\
    
    (a) ...\
    
    (b) ...\
    
    5. Next Meeting\
    (1) ...\
    
    (2) ...\
    
    When creating the meeting minutes, please keep the following points in mind:\
    - Ensure that the overall flow and conclusion of the meeting are clearly summarized.\
    - Mention the speaker for important statements or decisions made.\
    - Keep the language concise and accurate, avoiding ambiguous expressions.\
    - Enrich the content of the meeting minutes by relating the project information to the meeting content.\
    Be sure to break line when going to the next item.\
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

    else:
        client = OpenAI()
        summary_result = client.chat.completions.create(model=LLM, messages=[user_request], max_tokens=1000)
        summary = summary_result.choices[0].message.content.strip()
    return summary
