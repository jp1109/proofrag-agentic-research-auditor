def build_answer_prompt(question, context):
    """
    Creates a grounded prompt for the LLM.
    The model must answer using only the retrieved evidence.
    """

    context_text = "\n\n".join(
        [doc.page_content for doc in context]
    )

    prompt = f"""
You are a research assistant.

Answer the user's question using ONLY the evidence provided below.

If the evidence is insufficient, clearly say:
"I don't have enough evidence to answer this question."

QUESTION:
{question}

EVIDENCE:
{context_text}

Provide:
1. A clear answer
2. Supporting evidence
3. Any uncertainty or missing information
"""

    return prompt