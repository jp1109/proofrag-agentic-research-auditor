import streamlit as st

from src.pdf_loader import load_pdf
from src.retriever import build_vector_store
from src.workflow import build_workflow


st.set_page_config(
    page_title="ProofRAG",
    page_icon="📚",
    layout="wide"
)

st.title("📚 ProofRAG — Agentic Research Answer Auditor")

st.caption(
    "Upload a research paper, ask a question, and let ProofRAG "
    "generate and audit the answer against the paper evidence."
)

st.info(
    "ProofRAG answers questions from research papers and audits whether "
    "the answer is actually supported by retrieved evidence."
)

uploaded_file = st.file_uploader(
    "Upload Research Paper (PDF)",
    type=["pdf"]
)

if uploaded_file is not None:

    with st.spinner("Reading research paper..."):
        pages = load_pdf(uploaded_file)

    st.success(
        f"Paper loaded successfully — {len(pages)} pages extracted."
    )

    with st.spinner("Building vector search index..."):
        vector_store = build_vector_store(pages)

    st.success("Research paper indexed successfully.")

    question = st.text_input(
        "Ask a question about the paper"
    )

    if st.button("Run ProofRAG Audit", type="primary"):

        if not question.strip():
            st.warning("Please enter a question.")

        else:
            with st.spinner(
                "Retrieving evidence, generating answer, and auditing..."
            ):

                workflow = build_workflow()

                result = workflow.invoke({
                    "question": question,
                    "vector_store": vector_store,
                    "retry_count": 0
                })

        st.divider()
        answer = result["answer"]
        audit = result["audit"]
        confidence = result.get("confidence", 0)
        retry_count = result.get("retry_count", 0)

        supported_status = "Unknown"

        for line in audit.splitlines():
            if line.startswith("SUPPORTED:"):
               supported_status = line.split("SUPPORTED:")[1].strip()
            break


        st.subheader("🧠 ProofRAG Result")

        col1, col2, col3 = st.columns(3)

        with col1:
           if supported_status == "Yes":
             st.success("✅ Evidence Supported")
           elif supported_status == "Partially":
             st.warning("⚠️ Partially Supported")
           else:
             st.error("❌ Evidence Insufficient")

        with col2:
          st.metric(
        "Confidence",
        f"{confidence}%"
    )

        with col3:
           st.metric(
        "Retry Attempts",
        retry_count
    )
           
        st.caption(
         "Low-confidence answers are automatically routed through the LangGraph workflow "
         "for another retrieval-and-audit pass."
    )


        st.subheader("🤖 Verified Answer")
        st.write(answer)


        st.subheader("🔎 Auditor Analysis")

        with st.container(border=True):
           st.write(audit)


        st.subheader("📄 Retrieved Evidence")

        for i, doc in enumerate(result["context"], start=1):
            page_number = doc.metadata.get("page", "Unknown")

            with st.expander(
                f"Evidence {i} — Page {page_number}"
            ):
                st.write(doc.page_content)

        