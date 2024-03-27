import streamlit as st
from openai import OpenAI
import os

def minutes_check(text):
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

    LLM = 'gpt-4-0125-preview'

    summary_prompt = f"""
        You are an AI designed to support text editing in the manufacturing industry. \
        Your task is to assess whether the content of a given text, referred to as Business material, is suitable as a business document. \
        Examples of business documents include transcripts of meetings, minutes, travel reports, notes from business-related events, and articles related to manufacturing or business. \
        Examples of unsuitable documents include personal notes and articles about entertainment. 
        
        Business material: {text}\

        If you determine the text is suitable as a business document, return "1". \
        If it is not suitable, return "0". \
        Do not include any text other than the number in your response.\

        """
    client = OpenAI()
    summary_result = client.chat.completions.create(model=LLM, messages=[user_request], max_tokens=1000)
    summary = summary_result.choices[0].message.content.strip()
    
    return summary