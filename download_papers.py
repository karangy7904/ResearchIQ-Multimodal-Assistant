import os
import json
import urllib.request
import time

papers = [
    {
        "id": "2401.15884",
        "title": "Corrective Retrieval Augmented Generation",
        "authors": "Shi-Qi Yan, Jia-Chen Gu, Yun Zhu, Zhen-Hua Ling",
        "year": "2024",
        "venue": "Findings of ACL 2024",
        "filename": "CRAG_Corrective_RAG.pdf",
        "url": "https://arxiv.org/pdf/2401.15884.pdf",
        "has_visuals": True,
        "type": "Original Method"
    },
    {
        "id": "2310.11511",
        "title": "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection",
        "authors": "Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, Hannaneh Hajishirzi",
        "year": "2024",
        "venue": "ICLR 2024",
        "filename": "Self_RAG_Reflection.pdf",
        "url": "https://arxiv.org/pdf/2310.11511.pdf",
        "has_visuals": True,
        "type": "Original Method"
    },
    {
        "id": "2404.16130",
        "title": "From Local to Global Information Extraction with Large Language Model-Directed Knowledge Graph Construction",
        "authors": "Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, Jonathan Larson",
        "year": "2024",
        "venue": "arXiv / Microsoft Research",
        "filename": "GraphRAG_Global_Search.pdf",
        "url": "https://arxiv.org/pdf/2404.16130.pdf",
        "has_visuals": True,
        "type": "Original Method"
    },
    {
        "id": "2403.14403",
        "title": "Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity",
        "authors": "Soyeong Jeong, Jinheon Baek, Sukmin Cho, Sung Ju Hwang, Jong C. Park",
        "year": "2024",
        "venue": "NAACL 2024",
        "filename": "Adaptive_RAG_Complexity.pdf",
        "url": "https://arxiv.org/pdf/2403.14403.pdf",
        "has_visuals": True,
        "type": "Original Method"
    },
    {
        "id": "2312.10997",
        "title": "Retrieval-Augmented Generation for Large Language Models: A Survey",
        "authors": "Yunfan Gao, Yun Xiong, Xinyu Gao, Kangxiang Jia, Jinliu Pan, Yuxi Bi, Yi Dai, Jiawei Sun, Meng Wang, Haofen Wang",
        "year": "2024",
        "venue": "arXiv",
        "filename": "RAG_Comprehensive_Survey.pdf",
        "url": "https://arxiv.org/pdf/2312.10997.pdf",
        "has_visuals": True,
        "type": "Comprehensive Survey"
    },
    {
        "id": "2402.03216",
        "title": "BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation",
        "authors": "Jianlv Chen, Shitao Xiao, Peitian Zhang, Kun Luo, Defu Lian, Zheng Liu",
        "year": "2024",
        "venue": "arXiv",
        "filename": "BGE_M3_Hybrid_Embeddings.pdf",
        "url": "https://arxiv.org/pdf/2402.03216.pdf",
        "has_visuals": True,
        "type": "Original Method"
    },
    {
        "id": "2112.01488",
        "title": "ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction",
        "authors": "Keshav Santhanam, Omar Khattab, Christopher Potts, Matei Zaharia",
        "year": "2022",
        "venue": "NAACL 2022",
        "filename": "ColBERTv2_Late_Interaction.pdf",
        "url": "https://arxiv.org/pdf/2112.01488.pdf",
        "has_visuals": True,
        "type": "Original Method"
    },
    {
        "id": "2407.01449",
        "title": "Multimodal Retrieval-Augmented Generation: A Survey",
        "authors": "Haoran Wei, Shuo Liu, et al.",
        "year": "2024",
        "venue": "arXiv",
        "filename": "Multimodal_RAG_Survey.pdf",
        "url": "https://arxiv.org/pdf/2407.01449.pdf",
        "has_visuals": True,
        "type": "Comprehensive Survey"
    }
]

os.makedirs("papers", exist_ok=True)

with open("paper_catalogue.json", "w", encoding="utf-8") as f:
    json.dump(papers, f, indent=2)

print("Saved paper_catalogue.json")

for p in papers:
    dest = os.path.join("papers", p["filename"])
    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
        print(f"Already exists: {p['filename']} ({os.path.getsize(dest)} bytes)")
        continue
    print(f"Downloading: {p['title']} from {p['url']}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ResearchIQ-Bot/1.0"}
    req = urllib.request.Request(p["url"], headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
            with open(dest, "wb") as f:
                f.write(data)
            print(f"  -> Downloaded {p['filename']}: {len(data)} bytes")
        time.sleep(1.2)
    except Exception as e:
        print(f"  -> Failed {p['filename']}: {e}")
