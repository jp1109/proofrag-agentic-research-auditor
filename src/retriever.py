from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

def build_vector_store(pages):
    documents = []

    for page in pages:
        documents.append(
    Document(
        page_content=page["text"],
        metadata={"page": page["page"]}
    )
)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    return vector_store


def retrieve_context(vector_store, question, k=4):
    results = vector_store.similarity_search(
        question,
        k=k
    )

    return results