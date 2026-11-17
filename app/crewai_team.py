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
    """Sequential 4-agent persona execution on Amazon Bedrock."""
    llm = get_llm()
    
    # 1. Researcher Persona
    p1 = (
        "You are the Researcher agent. Academic research analyst.\n"
        f"Question: {question}\n"
        f"Evidence:\n{evidence}\n"
        "Extract claims, methods, results and limitations. Cite paper/page metadata. Never invent facts."
    )
    r1 = llm.invoke(p1).content
    t1_out = " ".join(str(x) for x in r1) if isinstance(r1, list) else str(r1)
    
    # 2. Visual Analyst Persona
    p2 = (
        "You are the Visual Analyst agent. You distinguish extracted text from uncertain visual interpretation.\n"
        f"Question: {question}\n"
        f"Evidence:\n{evidence}\n"
        f"Researcher findings:\n{t1_out}\n"
        "Analyze tables/figures and note uncertainty. Do not infer unreadable values. Note what needs original-image inspection."
    )
    r2 = llm.invoke(p2).content
    t2_out = " ".join(str(x) for x in r2) if isinstance(r2, list) else str(r2)

    # 3. Comparative Analyst Persona
    p3 = (
        "You are the Comparative Analyst agent. Normalize metrics, datasets and settings before comparing.\n"
        f"Question: {question}\n"
        f"Researcher findings:\n{t1_out}\n"
        f"Visual findings:\n{t2_out}\n"
        "Compare supported findings across papers only where evidence supports a fair comparison."
    )
    r3 = llm.invoke(p3).content
    t3_out = " ".join(str(x) for x in r3) if isinstance(r3, list) else str(r3)

    # 4. Research Synthesizer Persona
    p4 = (
        "You are the Research Synthesizer agent. Literature review specialist.\n"
        f"Question: {question}\n"
        f"Researcher findings:\n{t1_out}\n"
        f"Visual findings:\n{t2_out}\n"
        f"Comparative findings:\n{t3_out}\n"
        "Produce a concise synthesis; clearly separate supported findings from hypotheses and future directions."
    )
    r4 = llm.invoke(p4).content
    t4_out = " ".join(str(x) for x in r4) if isinstance(r4, list) else str(r4)

    return f"### Research Synthesis (Multi-Agent Team)\n\n{t4_out}\n\n**Agent Breakdown:**\n- **Researcher:** {t1_out[:300]}...\n- **Comparative Analyst:** {t3_out[:300]}..."

def run_research_crew(question: str, evidence: str) -> str:
    try:
        import crewai
        return _run_crewai_native(question, evidence)
    except Exception as e:
        logger.info(f"Using direct Bedrock multi-agent research pipeline: {e}")
        return _run_crew_direct_bedrock(question, evidence)
