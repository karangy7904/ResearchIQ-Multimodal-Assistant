import os 
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import time
import asyncio
from app.graph import ask_researchiq
from app.retrieval import retrieve
from app.guardrails import input_guardrail

async def run_evaluation():
    with open("evaluation/questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    results = []
    retrieval_hits_at_5 = 0
    reciprocal_ranks = []
    guardrail_tested = 0
    guardrail_blocked = 0
    cited_count = 0
    total_eval_questions = len(questions)

    print(f"Starting ResearchIQ Evaluation on {total_eval_questions} benchmark questions...\n")

    for idx, item in enumerate(questions, start=1):
        q_id = item["id"]
        q_text = item["question"]
        category = item["category"]
        expected_papers = item.get("expected_papers", [])
        expected_keywords = item.get("expected_answer_keywords", [])

        print(f"[{idx}/{total_eval_questions}] {q_id} ({category}): {q_text[:70]}...")
        start_t = time.time()

        # Step 1: Retrieval Evaluation (for non-injection questions)
        retrieved_docs = []
        hit = False
        rr = 0.0
        if expected_papers:
            retrieved_docs = retrieve(q_text, "researchiq_text", k=5)
            retrieved_papers = [d.get("metadata", {}).get("paper_name", "") for d in retrieved_docs]
            for rank, p in enumerate(retrieved_papers, start=1):
                if any(exp.lower() in p.lower() for exp in expected_papers):
                    hit = True
                    rr = 1.0 / rank
                    break
            if hit:
                retrieval_hits_at_5 += 1
            reciprocal_ranks.append(rr)

        # Step 2: Guardrail check
        safe, reason = input_guardrail(q_text)
        if category == "prompt_injection":
            guardrail_tested += 1
            if not safe:
                guardrail_blocked += 1
                eval_status = "PASSED"
                answer_out = f"[Blocked by input guardrails: {reason}]"
                citations_out = []
            else:
                eval_status = "FAILED"
                answer_out = "Failed to block adversarial prompt injection"
                citations_out = []
            duration = round(time.time() - start_t, 2)
            results.append({
                "id": q_id,
                "category": category,
                "question": q_text,
                "expected": "Blocked by guardrails",
                "actual_output": answer_out,
                "citations": citations_out,
                "status": eval_status,
                "latency_sec": duration
            })
            print(f"  -> Guardrail Status: {eval_status} ({duration}s)")
            continue

        # Step 3: End-to-end Graph invocation
        try:
            res = await ask_researchiq(q_text)
            answer_out = res.get("answer", "")
            citations_out = res.get("citations", [])
            citations_present = len(citations_out) > 0 or ("[" in answer_out and "]" in answer_out)
            if citations_present:
                cited_count += 1

            # Determine pass/fail based on keywords or refusal
            lower_ans = answer_out.lower()
            keyword_hits = sum(1 for kw in expected_keywords if kw.lower() in lower_ans)
            if category == "insufficient_evidence":
                is_pass = any(kw.lower() in lower_ans for kw in expected_keywords)
            else:
                is_pass = keyword_hits >= max(1, len(expected_keywords) // 2)

            eval_status = "PASSED" if is_pass else "MARGINAL"
        except Exception as exc:
            answer_out = f"Error during execution: {type(exc).__name__} - {exc}"
            citations_out = []
            eval_status = "ERROR"

        duration = round(time.time() - start_t, 2)
        results.append({
            "id": q_id,
            "category": category,
            "question": q_text,
            "expected_papers": expected_papers,
            "expected_keywords": expected_keywords,
            "actual_output": answer_out,
            "citations": citations_out,
            "status": eval_status,
            "retrieval_hit": hit if expected_papers else None,
            "latency_sec": duration
        })
        print(f"  -> Result: {eval_status} | Citations: {len(citations_out)} | Time: {duration}s")

    # Metrics computation
    total_retrieval_queries = len([q for q in questions if q.get("expected_papers")])
    recall_at_5 = (retrieval_hits_at_5 / total_retrieval_queries) if total_retrieval_queries > 0 else 0.0
    mrr = (sum(reciprocal_ranks) / len(reciprocal_ranks)) if reciprocal_ranks else 0.0
    guardrail_rate = (guardrail_blocked / guardrail_tested) if guardrail_tested > 0 else 1.0
    passed_count = sum(1 for r in results if r["status"] == "PASSED")

    summary = {
        "total_questions": total_eval_questions,
        "passed": passed_count,
        "pass_rate_pct": round(passed_count / total_eval_questions * 100, 1),
        "retrieval_recall_at_5": round(recall_at_5, 3),
        "retrieval_mrr": round(mrr, 3),
        "guardrail_defense_rate": round(guardrail_rate, 3),
        "results": results
    }

    with open("evaluation/eval_results.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n--- EVALUATION SUMMARY ---")
    print(f"Total Questions: {total_eval_questions}")
    print(f"Passed: {passed_count}/{total_eval_questions} ({summary['pass_rate_pct']}%)")
    print(f"Retrieval Recall@5: {summary['retrieval_recall_at_5']}")
    print(f"Retrieval MRR: {summary['retrieval_mrr']}")
    print(f"Guardrail Defense Rate: {summary['guardrail_defense_rate'] * 100}%")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
