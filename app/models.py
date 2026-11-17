from typing import Any, TypedDict

class ResearchState(TypedDict, total=False):
    question: str
    session_id: str
    intent: str
    plan: str
    paper_ids: list[str]
    text_evidence: list[dict[str, Any]]
    table_evidence: list[dict[str, Any]]
    figure_evidence: list[dict[str, Any]]
    visual_analysis: str
    crew_findings: str
    autogen_review: str
    evidence_check: str
    safe: bool
    answer: str
    citations: list[dict[str, Any]]
    errors: list[str]
