# ResearchIQ — Paper Catalogue

**Selected Research Topic:** 1. Advanced Retrieval-Augmented Generation (RAG)  
**Total Ingested Papers:** 8  
**Total Chunks Indexed:** 773  
**Extracted Tables:** 42  
**Extracted Figures & Diagrams in S3:** 57  
**Object Storage:** AWS S3 (`s3://firstrag/visuals/`)  
**Multimodal / LLM Engine:** Amazon Bedrock (`apac.amazon.nova-pro-v1:0`)  
**Text Embedding Engine:** Amazon Titan Text v2 (`amazon.titan-embed-text-v2:0`)  
**Table & Chart Embedding Engine:** Cohere Embed English v3 (`cohere.embed-english-v3`)  
**Visual & Diagram Embedding Engine:** Amazon Nova Multimodal (`apac.amazon.nova-pro-v1:0`) + Bedrock Vector Representation  

---

## 1. Paper Collection Summary

| # | Title | Authors | Year | Venue / Source | Identifier / URL | Local Filename | Visuals / Type |
|---|---|---|---|---|---|---|---|
| 1 | **Corrective Retrieval Augmented Generation (CRAG)** | Shi-Qi Yan, Jia-Chen Gu, Yun Zhu, Zhen-Hua Ling | 2024 | Findings of ACL 2024 | [arXiv:2401.15884](https://arxiv.org/abs/2401.15884) | `CRAG_Corrective_RAG.pdf` | ✅ Architecture diagram (Fig 2), retrieval evaluator, ablation tables |
| 2 | **Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection** | Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, Hannaneh Hajishirzi | 2024 | ICLR 2024 | [arXiv:2310.11511](https://arxiv.org/abs/2310.11511) | `Self_RAG_Reflection.pdf` | ✅ Framework diagram (Fig 1), reflection token tree, benchmark comparison tables |
| 3 | **From Local to Global Information Extraction with LLM-Directed Knowledge Graph Construction (GraphRAG)** | Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, Jonathan Larson | 2024 | Microsoft Research / arXiv | [arXiv:2404.16130](https://arxiv.org/abs/2404.16130) | `GraphRAG_Global_Search.pdf` | ✅ Graph construction pipeline (Fig 1), Leiden community detection diagram, comprehensive results |
| 4 | **Adaptive-RAG: Learning to Adapt Retrieval-Augmented LLMs through Question Complexity** | Soyeong Jeong, Jinheon Baek, Sukmin Cho, Sung Ju Hwang, Jong C. Park | 2024 | NAACL 2024 | [arXiv:2403.14403](https://arxiv.org/abs/2403.14403) | `Adaptive_RAG_Complexity.pdf` | ✅ Adaptive routing architecture diagram (Fig 2), classifier strategy plots, QA multi-hop tables |
| 5 | **Retrieval-Augmented Generation for Large Language Models: A Survey** | Yunfan Gao, Yun Xiong, Xinyu Gao, Kangxiang Jia, Jinliu Pan, et al. | 2024 | arXiv | [arXiv:2312.10997](https://arxiv.org/abs/2312.10997) | `RAG_Comprehensive_Survey.pdf` | ✅ Naive vs Advanced vs Modular RAG architecture figures (Fig 2, 3, 4), taxonomy tree |
| 6 | **BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation** | Jianlv Chen, Shitao Xiao, Peitian Zhang, Kun Luo, Defu Lian, Zheng Liu | 2024 | BAAI / arXiv | [arXiv:2402.03216](https://arxiv.org/abs/2402.03216) | `BGE_M3_Hybrid_Embeddings.pdf` | ✅ Dense + Sparse + Multi-Vector hybrid architecture diagram (Fig 2), MIRACL benchmark plots |
| 7 | **ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction** | Keshav Santhanam, Omar Khattab, Christopher Potts, Matei Zaharia | 2022 | NAACL 2022 | [arXiv:2112.01488](https://arxiv.org/abs/2112.01488) | `ColBERTv2_Late_Interaction.pdf` | ✅ Token-level late interaction diagram (Fig 1), residual compression plot, passage ranking tables |
| 8 | **Multimodal Retrieval-Augmented Generation: A Survey** | Haoran Wei, Shuo Liu, et al. | 2024 | arXiv | [arXiv:2407.01449](https://arxiv.org/abs/2407.01449) | `Multimodal_RAG_Survey.pdf` | ✅ Multimodal RAG taxonomy (Fig 2), cross-modality alignment figures, visual QA benchmark tables |

---

## 2. Ingestion & Storage Details

- **Text Chunks:** Partitioned using `RecursiveCharacterTextSplitter` (chunk size: 1100 characters, overlap: 160 characters).
- **Table Extraction:** Extracted via `pdfplumber` retaining page numbers and table structure.
- **Figure Extraction:** Extracted via `pymupdf` (fitz PixMap rendering at native DPI), uploaded to `s3://firstrag/visuals/<paper_id>/<visual_id>.png`.
- **ChromaDB Vector Store:** 3 isolated modality collections:
  - `researchiq_text`: 773 documents (embedded with Amazon Titan Text Embeddings v2)
  - `researchiq_tables`: 42 documents (embedded with Cohere Embed English v3)
  - `researchiq_figures`: 42 diagrams (analyzed and embedded with Amazon Nova Multimodal)
