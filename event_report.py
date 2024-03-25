import streamlit as st
from openai import OpenAI
import anthropic
import replicate
import os

def generate_meeting_reports(text, language, llm, project_name, deadline, budget, customer_name, date):
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
    REPLICATE_API_TOKEN=st.secrets["REPLICATE_API_TOKEN"]

    if llm == "GPT4":
        LLM = 'gpt-4-0125-preview'
    elif llm == "GPT3.5":
        LLM = 'gpt-3.5-turbo-0125'
    elif llm == 'Claude3':
        LLM = 'claude-3-sonnet-20240229'

    summary_prompt = f"""
        Please create a concise meeting report based on the meeting transcription.\
        Provide a brief overview of the event, and then describe each item in detail.\
        The intended audience may not have extensive knowledge about the event,\
        so ensure that the content is clear and easily understandable.\
        
        Project Information:
        Date: {date}
        Meeting Transcription: {text}
        """
    summary_prompt_j = f"""
        以下の会議の文字起こしに基づいて、イベントに関する簡潔なレポートを作成してください。\
        全体概要を簡単に説明した後、各項目ごとに詳細をまとめてください。 \       
        対象読者はプロジェクトに関する幅広い知識を持っていない可能性があるため、内容がわかりやすく理解しやすいことを確認してください。\
        
        プロジェクト情報:
        日付: {date}
        会議の文字起こし: {text}
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
                    #"mistralai/mixtral-8x7b-instruct-v0.1:cf18decbf51c27fed6bbdc3492312c1c903222a56e3fe9ca02d6cbe5198afc10",
                    input={
                        "top_k": 50,
                        "top_p": 0.95,
                        "prompt": prompt_gemma,
                        "temperature": 0.01,
                        "max_new_tokens":1000,
                        "min_new_tokens": 100,
                        "repetition_penalty": 1,
                        #"prompt_template": "<s>[INST] {prompt} [/INST]"
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