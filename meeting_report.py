import streamlit as st
from openai import OpenAI
import anthropic
import os

def generate_meeting_reports(text, language, llm, project_name, deadline, budget, customer_name):
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

    if llm == "GPT4":
        LLM = 'gpt-4-0125-preview'
    elif llm == "GPTGPT3.5":
        LLM = 'gpt-3.5-turbo-0125'
    else:
        LLM = 'claude-3-sonnet-20240229'

    summary_prompt = f"""
        Please create a concise meeting minutes based on the following project information and meeting transcription.\
        Provide a brief overview of the project, followed by a summary of the meeting's key points, issues, and action items in a single, well-structured paragraph.\
        The intended audience may not have extensive knowledge about the project,\
        so ensure that the content is clear and easily understandable.\

        Project Information:
        Project Name: {project_name}
        Deadline: {deadline}
        Budget: {budget}
        Customer Name: {customer_name}
        Meeting Transcription: {text}
        """

    if language == "日本語":
        user_request = {'role': 'assistant', 'content': summary_prompt+"日本語で記入してください。"}
    else:
        user_request = {'role': 'assistant', 'content': summary_prompt+"Write in English."}

    if llm == 'Claude3':
        client = anthropic.Anthropic()
        summary_result = client.messages.create(model=LLM, messages=[user_request], max_tokens=500)
        summary = summary_result.content[0].text

    else:
        client = OpenAI()
        summary_result = client.chat.completions.create(model=LLM, messages=[user_request], max_tokens=500)
        summary = summary_result.choices[0].message.content.strip()
    return summary
