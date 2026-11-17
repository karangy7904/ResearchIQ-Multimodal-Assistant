from concurrent.futures import ThreadPoolExecutor
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
    """Parallelized multi-index retrieval using concurrent Bedrock embedding and vector lookup."""
    try:
        # Generate Titan and Cohere embeddings simultaneously
        with ThreadPoolExecutor(max_workers=2) as executor:
            f_titan = executor.submit(lambda: get_embeddings().embed_query(question))
            f_cohere = executor.submit(lambda: get_table_embeddings().embed_query(question[:1500]))
            titan_vec = f_titan.result()
            cohere_vec = f_cohere.result()

        text_store = Chroma(collection_name="researchiq_text", persist_directory=settings.chroma_dir)
        table_store = Chroma(collection_name="researchiq_tables", persist_directory=settings.chroma_dir)
        fig_store = Chroma(collection_name="researchiq_figures", persist_directory=settings.chroma_dir)

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
            "text_evidence": retrieve(question, "researchiq_text", 6),
            "table_evidence": retrieve(question, "researchiq_tables", 4),
            "figure_evidence": retrieve(question, "researchiq_figures", 4),
        }
