# ResearchIQ — Hackathon Slide Deck

## Slide 1: Title Slide
- **Title**: ResearchIQ — Multimodal AI Research Assistant
- **Subtitle**: Enterprise-grade multimodal synthesis, multi-agent deliberation and zero-retention privacy for complex scientific literature
- **Team**: FINE-TUNED MIND (Karunesh G Y, Akshat Mishra, Vrindesh Pareek, Kailash Chaudhary)
- **Event**: Amazon Bedrock Multimodal AI Hackathon
- **Live Demo**: http://32.236.81.253/researchiq/

---

## Slide 2: Problem Statement Definition

### **Header**: Problem Statement Definition
### **Sub-header**: *Why current AI systems fail researchers on complex scientific literature*

### **The Core Challenge (4 Critical Gaps)**:

1. **Multimodal Evidence Blindspot**
   - **40%+ of key findings** are trapped in architecture diagrams, experimental charts, and complex benchmark tables. Traditional text-only RAG discards this visual and structural evidence entirely.

2. **Hallucination & Provenance Vacuum**
   - General LLMs frequently confabulate benchmark numbers, mix up ablation results between papers, and fail to provide verifiable, page-level attribution.

3. **Cross-Paper Synthesis Bottleneck**
   - Researchers spend days manually cross-referencing differing baselines, contrasting architectural trade-offs, and mapping inconsistencies across multiple publications.

4. **Data Privacy & IP Retention Risks**
   - Uploading unpublished pre-prints or sensitive proprietary research to cloud vector stores creates permanent data retention and cross-tenant leakage vulnerabilities.

---

### **Official Problem Definition Statement (Callout Box)**:
> *"Develop an autonomous, multimodal AI research assistant that concurrently parses, indexes, and reasons over text, tables, and visual architectures across a corpus of research papers—delivering strictly cited cross-paper synthesis with sub-3s interactive streaming, deep multi-agent consensus, and absolute zero-retention data privacy."*

---

### **Scope & Target Capabilities**:
- **Target Modalities**: Text passages (Titan v2) + Benchmark tables (Cohere v3) + Architectural diagrams (Nova Pro Vision).
- **Reasoning Depth**: Multi-paper comparison, trend interpretation, and honest negative recognition.
- **Privacy Standard**: Ephemeral isolated sessions (`session_id`) with one-click cryptographic vector purge.
