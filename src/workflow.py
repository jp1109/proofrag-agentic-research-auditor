from src.llm import get_llm
from typing import TypedDict, List, Any

from langgraph.graph import StateGraph, END

from src.retriever import retrieve_context
from src.answer_agent import build_answer_prompt
from src.evidence_auditor import build_audit_prompt


class ProofRAGState(TypedDict, total=False):
    question: str
    vector_store: Any
    context: List[Any]
    answer: str
    audit: str
    confidence: int
    retry_count: int


def retrieve_node(state: ProofRAGState):
    context = retrieve_context(
        state["vector_store"],
        state["question"],
        k=4
    )

    return {
        "context": context
    }


def answer_node(state: ProofRAGState):
    llm = get_llm()

    prompt = build_answer_prompt(
        state["question"],
        state["context"]
    )

    response = llm.invoke(prompt)

    return {
        "answer": response.content
    }


def audit_node(state: ProofRAGState):
    llm = get_llm()

    prompt = build_audit_prompt(
        state["question"],
        state["answer"],
        state["context"]
    )

    response = llm.invoke(prompt)
    audit_text = response.content

    confidence = 0

    for line in audit_text.splitlines():
        if "CONFIDENCE_SCORE:" in line:
            try:
                confidence = int(
                    line.split("CONFIDENCE_SCORE:")[1].strip()
                )
            except ValueError:
                confidence = 0

    return {
        "audit": audit_text,
        "confidence": confidence
    }

def should_retry(state: ProofRAGState):
    confidence = state.get("confidence", 0)
    retry_count = state.get("retry_count", 0)

    if confidence < 70 and retry_count < 1:
        return "retry"

    return "finish"

def retry_node(state: ProofRAGState):
    return {
        "retry_count": state.get("retry_count", 0) + 1
    }


def build_workflow():
    graph = StateGraph(ProofRAGState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("answer", answer_node)
    graph.add_node("audit", audit_node)
    graph.add_node("retry", retry_node)

    graph.set_entry_point("retrieve")

    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", "audit")

    graph.add_conditional_edges(
        "audit",
        should_retry,
        {
            "retry": "retry",
            "finish": END
        }
    )

    graph.add_edge("retry", "retrieve")

    return graph.compile()