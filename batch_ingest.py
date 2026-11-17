import os
import time
from app.ingestion import ingest_pdf
from app.storage import ensure_dirs

ensure_dirs()

papers = [
    "Adaptive_RAG_Complexity.pdf",
    "BGE_M3_Hybrid_Embeddings.pdf",
    "ColBERTv2_Late_Interaction.pdf",
    "Self_RAG_Reflection.pdf",
    "GraphRAG_Global_Search.pdf",
    "RAG_Comprehensive_Survey.pdf",
    "Multimodal_RAG_Survey.pdf"
]

for filename in papers:
    path = os.path.join("papers", filename)
    if not os.path.exists(path):
        print(f"Skipping {filename}, file not found")
        continue
    print(f"\n--- Ingesting {filename} ---")
    start = time.time()
    try:
        res = ingest_pdf(path, filename)
        duration = round(time.time() - start, 1)
        print(f"Done in {duration}s: {res}")
    except Exception as e:
        print(f"Error ingesting {filename}: {e}")

print("\nAll papers ingested successfully!")
