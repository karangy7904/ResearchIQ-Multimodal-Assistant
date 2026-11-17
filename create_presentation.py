import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path="ResearchIQ_Presentation.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Theme Colors
    BG_DARK = RGBColor(13, 17, 23)        # #0d1117
    PANEL_BG = RGBColor(22, 27, 34)       # #161b22
    BORDER_COLOR = RGBColor(48, 54, 61)   # #30363d
    ACCENT_ORANGE = RGBColor(234, 88, 12) # #ea580c
    ACCENT_BLUE = RGBColor(56, 189, 248)  # #38bdf8
    ACCENT_GREEN = RGBColor(34, 197, 94)  # #22c55e
    TEXT_WHITE = RGBColor(240, 246, 252)  # #f0f6fc
    TEXT_MUTED = RGBColor(139, 148, 158)  # #8b949e

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, title, subtitle, slide_num=""):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.1))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(13)
        p2.font.color.rgb = ACCENT_ORANGE

        # Footer
        ftb = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.7), Inches(0.4))
        ftf = ftb.text_frame
        ftf.margin_left = ftf.margin_top = ftf.margin_right = ftf.margin_bottom = 0
        fp = ftf.paragraphs[0]
        fp.text = f"ResearchIQ  |  Team Fine-Tuned Mind              {slide_num}"
        fp.font.size = Pt(10)
        fp.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Title card
    card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.0), Inches(11.333), Inches(5.5))
    card.fill.solid()
    card.fill.fore_color.rgb = PANEL_BG
    card.line.color.rgb = BORDER_COLOR

    tb = s1.shapes.add_textbox(Inches(1.5), Inches(1.4), Inches(10.333), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "ResearchIQ — Multimodal AI Research Assistant"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    p_sub = tf.add_paragraph()
    p_sub.text = "Enterprise-Grade Multimodal Synthesis, Multi-Agent Deliberation & Zero-Retention Privacy"
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = ACCENT_ORANGE
    p_sub.space_after = Pt(24)

    p_team = tf.add_paragraph()
    p_team.text = "Team FINE-TUNED MIND"
    p_team.font.size = Pt(18)
    p_team.font.bold = True
    p_team.font.color.rgb = ACCENT_BLUE

    p_members = tf.add_paragraph()
    p_members.text = "Vrindesh Pareek   •   Karunesh G Y   •   Kailash Choudhary   •   Akshat Mishra"
    p_members.font.size = Pt(14)
    p_members.font.color.rgb = TEXT_WHITE
    p_members.space_after = Pt(20)

    p_event = tf.add_paragraph()
    p_event.text = "Amazon Bedrock Multimodal AI Hackathon"
    p_event.font.size = Pt(14)
    p_event.font.color.rgb = TEXT_MUTED

    p_links = tf.add_paragraph()
    p_links.text = "🌐 Live Demo: http://32.236.81.253/researchiq/    •    📦 GitHub: github.com/karangy7904/ResearchIQ-Multimodal-Assistant"
    p_links.font.size = Pt(13)
    p_links.font.color.rgb = ACCENT_GREEN

    # =========================================================================
    # SLIDE 2: Problem Statement Definition (NEW / CHANGED PAGE)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Problem Statement Definition", "Why standard AI assistants fail on modern scientific research literature", "Slide 2")

    # 4 Problem Cards
    col_w = Inches(2.7)
    gap = Inches(0.25)
    start_x = Inches(0.8)
    top_y = Inches(1.8)
    h = Inches(3.2)

    problems = [
        ("1. Multimodal Blindspot", "Over 40% of actionable insights reside in architecture flows, ablation plots, and benchmark tables. Standard text-only RAG discards this crucial visual and structural evidence entirely."),
        ("2. Hallucination Crisis", "General LLMs confabulate benchmark numbers, mix up baseline results across papers, and fail to provide verifiable, page-level attribution, making ungrounded answers untrustworthy."),
        ("3. Synthesis Bottleneck", "Understanding emerging literature requires synthesizing differing methodologies, comparing baselines, and spotting inconsistencies across multiple papers—overwhelming manual effort."),
        ("4. Enterprise IP Leakage", "Uploading unpublished pre-prints or proprietary research to cloud vector databases risks permanent data retention and cross-tenant leakage with zero isolation guarantees.")
    ]

    for i, (title, desc) in enumerate(problems):
        x = start_x + i * (col_w + gap)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, top_y, col_w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = PANEL_BG
        card.line.color.rgb = BORDER_COLOR

        tb = s2.shapes.add_textbox(x + Inches(0.15), top_y + Inches(0.15), col_w - Inches(0.3), h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = ACCENT_ORANGE
        p.space_after = Pt(10)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_WHITE

    # Callout Quote Box at bottom
    callout = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.2), Inches(11.7), Inches(1.4))
    callout.fill.solid()
    callout.fill.fore_color.rgb = PANEL_BG
    callout.line.color.rgb = ACCENT_BLUE

    ctb = s2.shapes.add_textbox(Inches(1.0), Inches(5.3), Inches(11.3), Inches(1.2))
    ctf = ctb.text_frame
    ctf.word_wrap = True
    cp1 = ctf.paragraphs[0]
    cp1.text = "🎯 The Problem Definition Statement:"
    cp1.font.size = Pt(12)
    cp1.font.bold = True
    cp1.font.color.rgb = ACCENT_BLUE

    cp2 = ctf.add_paragraph()
    cp2.text = '"To engineer an autonomous, multimodal research assistant that concurrently parses, indexes, and reasons over text, tables, and visual architectures across a corpus of research papers—delivering strictly cited cross-paper synthesis with sub-3s interactive streaming, deep multi-agent consensus, and absolute zero-retention data privacy."'
    cp2.font.size = Pt(12)
    cp2.font.color.rgb = TEXT_WHITE

    # =========================================================================
    # SLIDE 3: Our Solution
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Our Solution: Multimodal, Grounded, Agent-Verified", "ResearchIQ bridges the gap between text, tables, diagrams, and verifiable reasoning", "Slide 3")

    # Left Column: Key Features
    left_card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.5), Inches(4.8))
    left_card.fill.solid()
    left_card.fill.fore_color.rgb = PANEL_BG
    left_card.line.color.rgb = BORDER_COLOR

    ltb = s3.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.1), Inches(4.4))
    ltf = ltb.text_frame
    ltf.word_wrap = True
    lp = ltf.paragraphs[0]
    lp.text = "Core Solution Capabilities:"
    lp.font.size = Pt(16)
    lp.font.bold = True
    lp.font.color.rgb = ACCENT_ORANGE
    lp.space_after = Pt(12)

    bullets = [
        "✅ Tri-Modal Indexing: Text (Titan v2), Tables (Cohere v3), Diagrams (Nova Vision)",
        "✅ Strict Inline Citations: Every claim cites [Paper Name, p. N, Table/Figure ID]",
        "✅ Cross-Paper Synthesis: Automatically compares differing methodologies & baselines",
        "✅ Dual Execution Modes: Sub-3s fast streaming or deep multi-agent consensus",
        "✅ Zero-Retention Guarantee: Ephemeral private sessions with 1-click total purge",
        "✅ MCP Agent Interoperability: Exposes research tools to external AI agent frameworks"
    ]
    for b in bullets:
        bp = ltf.add_paragraph()
        bp.text = b
        bp.font.size = Pt(12)
        bp.font.color.rgb = TEXT_WHITE
        bp.space_after = Pt(8)

    # Right Column: Comparison Table
    table_shape = s3.shapes.add_table(7, 3, Inches(6.6), Inches(1.8), Inches(5.9), Inches(4.8))
    table = table_shape.table
    table.columns[0].width = Inches(1.9)
    table.columns[1].width = Inches(1.8)
    table.columns[2].width = Inches(2.2)

    headers = ["Capability", "Basic PDF Chatbot", "ResearchIQ Assistant"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = ACCENT_BLUE if j == 2 else PANEL_BG
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE

    rows = [
        ("Text Reasoning", "Yes (Shallow)", "Titan v2 Semantic Search"),
        ("Tables & Metrics", "Limited / garbled", "Cohere v3 on Markdown Tables"),
        ("Charts & Figures", "Ignored", "Nova Pro Vision Descriptors"),
        ("Cross-Paper Comp.", "Often fails / confuses", "Structured Multi-Paper Synthesis"),
        ("Multi-Agent Review", "Absent (Single LLM)", "CrewAI + AutoGen Peer Review"),
        ("Data Retention", "Persistent / Risky", "Zero-Retention Ephemeral Sessions")
    ]
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.cell(i+1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = PANEL_BG
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.font.color.rgb = ACCENT_GREEN if j == 2 else TEXT_WHITE

    # =========================================================================
    # SLIDE 4: Multimodal RAG Ingestion Pipeline
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Multimodal RAG Pipeline", "PyMuPDF + pdfplumber parse PDFs on 8 parallel workers into three specialized collections", "Slide 4")

    # 3 Collections
    cards_data = [
        ("Collection 1: Text Passages", "Amazon Titan Text Embeddings v2", "• 1100-character semantic chunks with sliding overlap\n• Dense 1024-dimensional normalized vector indexing\n• Deep semantic retrieval across all 8 ingested papers\n• Sub-second vector lookup via ChromaDB"),
        ("Collection 2: Tabular Metrics", "Cohere Embed English v3", "• High-density Markdown serialization of tables\n• Preserves column headers, row relationships, and numeric units\n• Optimized for numerical comparisons & benchmark lookups\n• Indexed into dedicated session vector collection"),
        ("Collection 3: Figures & Diagrams", "Amazon Bedrock Nova Pro Vision", "• Native resolution PNG extraction and cropping\n• Nova Pro Vision multimodal descriptor parsing (flows, axes, legends)\n• Original high-res images uploaded to AWS S3\n• Visual evidence retrieval grounds architecture questions")
    ]

    for i, (title, model, desc) in enumerate(cards_data):
        x = Inches(0.8) + i * Inches(3.95)
        c = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(3.8), Inches(4.8))
        c.fill.solid()
        c.fill.fore_color.rgb = PANEL_BG
        c.line.color.rgb = BORDER_COLOR

        tb = s4.shapes.add_textbox(x + Inches(0.2), Inches(2.0), Inches(3.4), Inches(4.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = ACCENT_ORANGE
        p.space_after = Pt(4)

        pm = tf.add_paragraph()
        pm.text = model
        pm.font.size = Pt(11)
        pm.font.bold = True
        pm.font.color.rgb = ACCENT_BLUE
        pm.space_after = Pt(14)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = TEXT_WHITE

    # =========================================================================
    # SLIDE 5: Agentic AI Workflow (CrewAI + AutoGen + LangGraph)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Agentic AI Workflow & Multi-Agent Deliberation", "Two collaborating teams, coordinated by LangGraph, power Deep Multi-Agent Consensus", "Slide 5")

    steps = [
        ("1. Vision Analysis Node", "Nova Pro Multimodal reads retrieved diagram crops from S3, extracting architectural flows and trend takeaways."),
        ("2. CrewAI Research Team", "Researcher Agent structures multi-paper evidence; Fact-Checker Agent audits every technical claim against source records."),
        ("3. AutoGen Reviewer Team", "Adversarial Reviewer challenges hypotheses, verifies methodology differences, and audits citation fidelity."),
        ("4. Provenance & Citations", "Evidence Checker verifies exact [Paper, p. N, Table/Figure ID] coordinates before generating final report.")
    ]

    for i, (stitle, sdesc) in enumerate(steps):
        y = Inches(1.8) + i * Inches(1.2)
        c = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.7), Inches(1.05))
        c.fill.solid()
        c.fill.fore_color.rgb = PANEL_BG
        c.line.color.rgb = BORDER_COLOR

        tb = s5.shapes.add_textbox(Inches(1.0), y + Inches(0.12), Inches(11.3), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = stitle
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = ACCENT_ORANGE
        p.space_after = Pt(4)

        p2 = tf.add_paragraph()
        p2.text = sdesc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_WHITE

    # =========================================================================
    # SLIDE 6: Privacy, Security and Traceability
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Privacy, Security and Traceability", "Built for sensitive proprietary research and strict data governance", "Slide 6")

    sec_cards = [
        ("🔒 Isolated Ephemeral Sessions", "Each user receives a unique session_id. All vectors live in dedicated ChromaDB collections (text_{session_id}, tables_{session_id}, figures_{session_id}). Concurrent users have zero visibility into other sessions."),
        ("🧹 Instant Purge Lifecycle", "Clicking 'End Private Session & Purge' or calling DELETE /session/{id} immediately and irreversibly wipes ChromaDB collections, local uploads, and S3 paper copies."),
        ("🛡️ Prompt-Injection Defense", "Retrieved documents are treated as untrusted data and wrapped in [UNTRUSTED PAPER EVIDENCE] boundaries to neutralize adversarial jailbreaks embedded in PDFs."),
        ("📑 100% Traceable Citations", "Every technical claim is strictly attributed with [Paper, p. N, Table/Visual ID]. If evidence is missing, the system explicitly acknowledges it rather than hallucinating.")
    ]

    for i, (title, desc) in enumerate(sec_cards):
        row = i // 2
        col = i % 2
        x = Inches(0.8) + col * Inches(5.95)
        y = Inches(1.8) + row * Inches(2.45)
        c = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.75), Inches(2.25))
        c.fill.solid()
        c.fill.fore_color.rgb = PANEL_BG
        c.line.color.rgb = BORDER_COLOR

        tb = s6.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), Inches(5.35), Inches(1.85))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = ACCENT_BLUE
        p.space_after = Pt(8)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_WHITE

    # =========================================================================
    # SLIDE 7: Evaluation and Benchmark Results
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Evaluation & Benchmark Results", "End-to-end 16-question evaluation suite covering comparative, visual, tabular, and injection queries", "Slide 7")

    metrics = [
        ("100%", "Retrieval Recall@5", "Target: ≥ 80%", ACCENT_GREEN),
        ("0.917", "Mean Reciprocal Rank (MRR)", "Target: ≥ 0.70", ACCENT_GREEN),
        ("100%", "Citation Traceability", "Target: 100%", ACCENT_BLUE),
        ("100%", "Prompt-Injection Defense", "Target: 100%", ACCENT_BLUE),
        ("100%", "Out-of-Domain Detection", "Target: ≥ 80%", ACCENT_ORANGE),
        ("81.2%", "Benchmark Pass Rate (13/16)", "Target: ≥ 75%", ACCENT_GREEN)
    ]

    for i, (val, title, target, color) in enumerate(metrics):
        row = i // 3
        col = i % 3
        x = Inches(0.8) + col * Inches(3.95)
        y = Inches(1.8) + row * Inches(2.45)
        c = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.8), Inches(2.25))
        c.fill.solid()
        c.fill.fore_color.rgb = PANEL_BG
        c.line.color.rgb = BORDER_COLOR

        tb = s7.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), Inches(3.4), Inches(1.85))
        tf = tb.text_frame
        tf.word_wrap = True

        p_val = tf.paragraphs[0]
        p_val.text = val
        p_val.font.size = Pt(32)
        p_val.font.bold = True
        p_val.font.color.rgb = color
        p_val.space_after = Pt(4)

        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.size = Pt(13)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

        p_tgt = tf.add_paragraph()
        p_tgt.text = target
        p_tgt.font.size = Pt(11)
        p_tgt.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 8: Live Demo & Technical Defense
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Live Cloud Deployment & Demo Walkthrough", "Production deployment on AWS EC2 with automated CI/CD and NGINX reverse-proxying", "Slide 8")

    # Left: Deployment Info
    c1 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.75), Inches(4.8))
    c1.fill.solid()
    c1.fill.fore_color.rgb = PANEL_BG
    c1.line.color.rgb = BORDER_COLOR

    tb1 = s8.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.35), Inches(4.4))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "Production Infrastructure:"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ORANGE
    p.space_after = Pt(10)

    bullets1 = [
        "🌐 AWS EC2 (Sydney ap-southeast-2): Running Ubuntu 24.04 LTS",
        "⚡ NGINX Reverse Proxy: Ports 7861 (UI) & 8002 (API) unified",
        "🔄 Automated CI/CD: GitHub Actions pipeline with pytest verification",
        "🚀 Live Endpoints:",
        "    • Web App: http://32.236.81.253/researchiq/",
        "    • Swagger Docs: http://32.236.81.253/researchiq-api/docs"
    ]
    for b in bullets1:
        bp = tf1.add_paragraph()
        bp.text = b
        bp.font.size = Pt(11)
        bp.font.color.rgb = TEXT_WHITE
        bp.space_after = Pt(6)

    # Right: Live Demo Highlights
    c2 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.75), Inches(1.8), Inches(5.75), Inches(4.8))
    c2.fill.solid()
    c2.fill.fore_color.rgb = PANEL_BG
    c2.line.color.rgb = BORDER_COLOR

    tb2 = s8.shapes.add_textbox(Inches(6.95), Inches(2.0), Inches(5.35), Inches(4.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "Demo Highlights for Judges:"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(10)

    bullets2 = [
        "1. Parallel Multi-PDF Upload: 8 concurrent workers process 8 papers in <25s",
        "2. Private Ephemeral Session: Session ID visible with live zero-retention guarantee",
        "3. Fast Streaming Mode: Instant sub-3s token stream with real-time citations",
        "4. Deep Multi-Agent Consensus: CrewAI & AutoGen deliberation on complex trade-offs",
        "5. One-Click Session Purge: Instant wipe of all database vectors and local files"
    ]
    for b in bullets2:
        bp = tf2.add_paragraph()
        bp.text = b
        bp.font.size = Pt(11)
        bp.font.color.rgb = TEXT_WHITE
        bp.space_after = Pt(6)

    # =========================================================================
    # SLIDE 9: Conclusion
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)

    card9 = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.0), Inches(11.333), Inches(5.5))
    card9.fill.solid()
    card9.fill.fore_color.rgb = PANEL_BG
    card9.line.color.rgb = BORDER_COLOR

    tb9 = s9.shapes.add_textbox(Inches(1.5), Inches(1.4), Inches(10.333), Inches(4.7))
    tf9 = tb9.text_frame
    tf9.word_wrap = True

    p = tf9.paragraphs[0]
    p.text = "Conclusion & Hackathon Impact"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(16)

    takeaways = [
        "🏆 Production-Ready: Live on AWS EC2 with automated CI/CD and NGINX reverse-proxying",
        "👁️ True Multimodal Reasoning: Simultaneous text, tabular (Cohere), and diagram (Nova Pro) reasoning",
        "⚡ Dual-Engine Synthesizer: Sub-3s streaming for interactive speed + deep multi-agent consensus for rigor",
        "🛡️ Zero-Retention Privacy: Isolated ephemeral sessions with one-click cryptographic vector purge",
        "📑 100% Traceable Citations: Zero hallucination on benchmark tests with exact page-level attribution"
    ]
    for t in takeaways:
        tp = tf9.add_paragraph()
        tp.text = t
        tp.font.size = Pt(13)
        tp.font.color.rgb = TEXT_WHITE
        tp.space_after = Pt(10)

    p_end = tf9.add_paragraph()
    p_end.text = "Thank You! — Team FINE-TUNED MIND (Vrindesh Pareek, Karunesh G Y, Kailash Choudhary, Akshat Mishra)"
    p_end.font.size = Pt(14)
    p_end.font.bold = True
    p_end.font.color.rgb = ACCENT_ORANGE
    p_end.space_before = Pt(14)

    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    create_deck("ResearchIQ_Presentation.pptx")
