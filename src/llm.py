import os
from langchain_groq import ChatGroq


def get_llm():
    return ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )