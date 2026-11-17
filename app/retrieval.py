from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from langchain_chroma import Chroma
from app.clients import get_embeddings, get_table_embeddings
from app.config import settings

def _store(name: str):
    if name == "researchiq_tables" or name.startswith("tables_"):
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

def retrieve_all(question: str, session_id: Optional[str] = None):
    """Parallelized multi-index retrieval using concurrent Bedrock embedding and vector lookup.
    Supports session-scoped private collections if session_id is provided.
    """
    text_col = f"text_{session_id}" if session_id else "researchiq_text"
    table_col = f"tables_{session_id}" if session_id else "researchiq_tables"
    fig_col = f"figures_{session_id}" if session_id else "researchiq_figures"

    try:
        # Generate Titan and Cohere embeddings simultaneously
        with ThreadPoolExecutor(max_workers=2) as executor:
            f_titan = executor.submit(lambda: get_embeddings().embed_query(question))
            f_cohere = executor.submit(lambda: get_table_embeddings().embed_query(question[:1500]))
            titan_vec = f_titan.result()
            cohere_vec = f_cohere.result()

        text_store = Chroma(collection_name=text_col, persist_directory=settings.chroma_dir)
        table_store = Chroma(collection_name=table_col, persist_directory=settings.chroma_dir)
        fig_store = Chroma(collection_name=fig_col, persist_directory=settings.chroma_dir)

        # Single Titan vector queries both text and multimodal figure collections
        text_docs = text_store.similarity_search_by_vector(titan_vec, k=6)
        table_docs = table_store.similarity_search_by_vector(cohere_vec, k=4)
        fig_docs = fig_store.similarity_search_by_vector(titan_vec, k=4)

        return {
            "text_evidence": [{"text": d.page_content, "metadata": d.metadata} for d in text_docs],
            "table_evidence": [{"text": d.page_content, "metadata": d.metadata} for d in table_docs],
            "figure_evidence": [{"text": d.page_content, "metadata": d.metadata} for d in fig_docs],
        }
    except Exception:
        # Graceful fallback
        return {
            "text_evidence": retrieve(question, text_col, 6),
            "table_evidence": retrieve(question, table_col, 4),
            "figure_evidence": retrieve(question, fig_col, 4),
        }
