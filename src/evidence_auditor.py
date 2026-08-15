def build_audit_prompt(question, answer, context):
    """
    Creates a prompt that checks whether the generated answer
    is actually supported by the retrieved research-paper evidence.
    """

    context_text = "\n\n".join(
        [doc.page_content for doc in context]
    )

    prompt = f"""
You are an evidence auditor for research-paper answers.

Your job is to determine whether the answer is supported by
the evidence retrieved from the research paper.

QUESTION:
{question}

GENERATED ANSWER:
{answer}

PAPER EVIDENCE:
{context_text}

Check for:
1. Claims supported by the evidence
2. Claims not supported by the evidence
3. Missing or weak evidence
4. Possible hallucinations

Return your evaluation in this format:

SUPPORTED: Yes / Partially / No

CONFIDENCE_SCORE: number from 0 to 100

UNSUPPORTED_CLAIMS:
- list any unsupported claims
- write "None" if there are none

AUDITOR_NOTE:
Briefly explain whether the answer can be trusted.
"""

    return prompt