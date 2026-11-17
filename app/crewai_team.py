import logging
from app.config import settings 
from app.clients import get_llm

logger = logging.getLogger(__name__)

def _bedrock_available():
    return bool(settings.aws_region and settings.bedrock_chat_model)

def _run_crewai_native(question: str, evidence: str) -> str:
    from crewai import Agent, Task, Crew, Process
    model = f"bedrock/{settings.bedrock_chat_model}"
    researcher = Agent(
        role="Researcher",
        goal="Extract methodology, datasets, results and limitations from supplied evidence.",
        backstory="You are a careful academic research analyst. Never invent facts.",
        llm=model, verbose=False, allow_delegation=False,
    )
    visual = Agent(
        role="Visual Analyst",
        goal="Interpret retrieved table and figure descriptions; identify what needs original-image inspection.",
        backstory="You distinguish extracted text from uncertain visual interpretation.",
        llm=model, verbose=False, allow_delegation=False,
    )
    comparative = Agent(
        role="Comparative Analyst",
        goal="Compare papers only where the evidence supports a fair comparison.",
        backstory="You normalize metrics, datasets and experimental settings before comparing.",
        llm=model, verbose=False, allow_delegation=False,
    )
    synthesizer = Agent(
        role="Research Synthesizer",
        goal="Synthesize findings and label evidence-backed conclusions versus hypotheses.",
        backstory="You are a literature review specialist who does not fabricate citations.",
        llm=model, verbose=False, allow_delegation=False,
    )
    t1 = Task(description=f"Question: {question}\nEvidence:\n{evidence}\nExtract claims, methods, results and limitations. Cite paper/page metadata.", agent=researcher, expected_output="Evidence-grounded research notes with source metadata.")
    t2 = Task(description=f"Question: {question}\nEvidence:\n{evidence}\nAnalyze tables/figures and note uncertainty. Do not infer unreadable values.", agent=visual, expected_output="Visual findings and limitations.")
    t3 = Task(description=f"Question: {question}\nEvidence:\n{evidence}\nCompare supported findings across papers.", agent=comparative, expected_output="Structured comparison with source metadata.")
    t4 = Task(description=f"Question: {question}\nUse the prior task outputs. Produce concise synthesis; separate supported findings from hypotheses.", agent=synthesizer, expected_output="Research synthesis.")
    crew = Crew(agents=[researcher, visual, comparative, synthesizer],
                tasks=[t1, t2, t3, t4], process=Process.sequential, verbose=False)
    return str(crew.kickoff())

def _run_crew_direct_bedrock(question: str, evidence: str) -> str:
    """Fast unified Multi-Persona Research Crew execution on Amazon Bedrock."""
    llm = get_llm()
    prompt = (
        "You are the ResearchIQ Multi-Agent Research Crew consisting of four collaborative personas:\n"
        "1. [Researcher]: Extracts core methodology, empirical results, and cited metrics.\n"
        "2. [Visual Analyst]: Analyzes table/diagram findings and notes visual limitations.\n"
        "3. [Comparative Analyst]: Compares supported findings across papers normalizing settings.\n"
        "4. [Research Synthesizer]: Synthesizes clear takeaways, distinguishing evidence from hypotheses.\n\n"
        f"Question: {question}\n\n"
        f"Retrieved Evidence Records:\n{evidence[:12000]}\n\n"
        "Produce your collaborative analysis structured with these sections:\n"
        "### 1. Research Findings & Methodology\n"
        "### 2. Visual & Tabular Analysis\n"
        "### 3. Cross-Paper Comparison & Trade-offs\n"
        "### 4. Synthesis & Research Insights\n"
        "Cite every claim with [paper_name, p. N]. Be direct, precise, and factual."
    )
    r = llm.invoke(prompt).content
    crew_output = " ".join(str(x) for x in r) if isinstance(r, list) else str(r)
    return f"### Research Synthesis (Multi-Agent Team)\n\n{crew_output}"

def run_research_crew(question: str, evidence: str) -> str:
    try:
        import crewai
        return _run_crewai_native(question, evidence)
    except Exception as e:
        logger.info(f"Using direct Bedrock multi-agent research pipeline: {e}")
        return _run_crew_direct_bedrock(question, evidence)
