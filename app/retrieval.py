from langchain_chroma import Chroma
from app.clients import get_embeddings, get_table_embeddings
from app.config import settings

def _store(name):
    if name == "researchiq_tables":
        embed_fn = get_table_embeddings()
    else:
        embed_fn = get_embeddings()
    return Chroma(collection_name=name, persist_directory=settings.chroma_dir,
                  embedding_function=embed_fn)

def retrieve(question: str, collection: str, k: int = 5):
    try:
        docs = _store(collection).similarity_search(question, k=k)
    except Exception:
        return []
    return [{"text": d.page_content, "metadata": d.metadata} for d in docs]

def retrieve_all(question: str):
    return {
        "text_evidence": retrieve(question, "researchiq_text", 6),
        "table_evidence": retrieve(question, "researchiq_tables", 4),
        "figure_evidence": retrieve(question, "researchiq_figures", 4),
    }
