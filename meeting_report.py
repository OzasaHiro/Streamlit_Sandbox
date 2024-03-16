import streamlit as st
from openai import OpenAI
import anthropic
import replicate
import os

def generate_meeting_reports(text, language, llm, project_name, deadline, budget, customer_name):
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
    REPLICATE_API_TOKEN=st.secrets["REPLICATE_API_TOKEN"]

    if llm == "GPT4":
        LLM = 'gpt-4-0125-preview'
    elif llm == "GPTGPT3.5":
        LLM = 'gpt-3.5-turbo-0125'
    elif llm == 'Claude3':
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
        prompt = summary_prompt+"日本語で記入してください。"
        user_request = {'role': 'assistant', 'content': prompt}
    else:
        prompt = summary_prompt+"Write in English."
        user_request = {'role': 'assistant', 'content': prompt}

    if llm == 'Claude3':
        client = anthropic.Anthropic()
        summary_result = client.messages.create(
                    model=LLM,
                    max_tokens=500,
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
                        "min_new_tokens": 100,
                        "repetition_penalty": 1
                    }
                )
        for item in output:
            # https://replicate.com/google-deepmind/gemma-7b-it/api#output-schema
            st.write(item, end="")
        summary = next(summary_result)

    else:
        client = OpenAI()
        summary_result = client.chat.completions.create(model=LLM, messages=[user_request], max_tokens=500)
        summary = summary_result.choices[0].message.content.strip()
    return summary
