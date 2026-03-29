"""
Evaluation framework for the Prerequisite & Course Planning Assistant.

Runs 25 test queries across 4 categories and reports:
- Citation Coverage Rate
- Abstention Accuracy
- Eligibility Correctness
- 3 detailed example transcripts
"""
import os
import json
import time
from datetime import datetime

import config


# ─── Test Queries ────────────────────────────────────────────────────────────

TEST_QUERIES = {
    "prerequisite_checks": [
        {
            "id": "P1",
            "query": "Can I take CS161 if I have completed CS106A and CS106B?",
            "expected": "not_eligible",
            "reason": "CS161 requires CS109 AND CS103, not just CS106A/CS106B."
        },
        {
            "id": "P2",
            "query": "Can I take CS106B if I have completed CS106A?",
            "expected": "eligible",
            "reason": "CS106B requires only CS106A."
        },
        {
            "id": "P3",
            "query": "Can I take CS221 if I have completed CS161 and CS109?",
            "expected": "eligible",
            "reason": "CS221 requires CS161 AND CS109."
        },
        {
            "id": "P4",
            "query": "Can I take CS111 if I have only completed CS106A?",
            "expected": "not_eligible",
            "reason": "CS111 requires CS107, which requires CS106B."
        },
        {
            "id": "P5",
            "query": "Can I take CS229 if I have completed CS109 but not MATH51?",
            "expected": "not_eligible",
            "reason": "CS229 requires both CS109 AND MATH51."
        },
        {
            "id": "P6",
            "query": "Can I take CS103 if I have completed CS106A?",
            "expected": "eligible",
            "reason": "CS103 requires only CS106A."
        },
        {
            "id": "P7",
            "query": "Can I take CS145 if I have completed CS106B and CS103?",
            "expected": "eligible",
            "reason": "CS145 requires CS103 AND CS106B."
        },
        {
            "id": "P8",
            "query": "Can I take CS224N if I have only completed CS161?",
            "expected": "not_eligible",
            "reason": "CS224N requires CS221, which the student hasn't completed."
        },
        {
            "id": "P9",
            "query": "Can I take CS246 if I have completed CS107 and CS161?",
            "expected": "eligible",
            "reason": "CS246 requires CS107 AND CS161."
        },
        {
            "id": "P10",
            "query": "Can I take CS109 if I have completed CS106B and MATH51?",
            "expected": "eligible",
            "reason": "CS109 requires CS106B AND MATH51."
        },
    ],
    "multi_hop_chains": [
        {
            "id": "M1",
            "query": "What is the full prerequisite chain to take CS221 starting from scratch?",
            "expected_courses": ["CS106A", "CS106B", "CS103", "MATH51", "CS109", "CS161", "CS221"],
            "reason": "CS221 requires CS161+CS109. CS161 requires CS109+CS103. CS109 requires CS106B+MATH51. CS103 requires CS106A. CS106B requires CS106A."
        },
        {
            "id": "M2",
            "query": "What courses do I need before I can take CS224N?",
            "expected_courses": ["CS106A", "CS106B", "CS103", "MATH51", "CS109", "CS161", "CS221", "CS224N"],
            "reason": "CS224N requires CS221, which chains back through CS161, CS109, CS103, CS106B, CS106A, MATH51."
        },
        {
            "id": "M3",
            "query": "I want to take CS231N. What is the full path of prerequisites?",
            "expected_courses": ["CS106B", "MATH51", "CS109", "CS229", "CS231N"],
            "reason": "CS231N requires CS229. CS229 requires CS109+MATH51. CS109 requires CS106B+MATH51."
        },
        {
            "id": "M4",
            "query": "What do I need to complete before taking CS248A?",
            "expected_courses": ["CS106B", "CS107", "CS148", "CS248A"],
            "reason": "CS248A requires CS148. CS148 requires CS107. CS107 requires CS106B."
        },
        {
            "id": "M5",
            "query": "Trace the prerequisite chain for CS144.",
            "expected_courses": ["CS106A", "CS106B", "CS107", "CS111", "CS144"],
            "reason": "CS144 requires CS111. CS111 requires CS107. CS107 requires CS106B. CS106B requires CS106A."
        },
    ],
    "program_requirements": [
        {
            "id": "R1",
            "query": "What are the core requirements for the BS in Computer Science at Stanford?",
            "expected_keywords": ["CS106A", "CS106B", "CS103", "CS107", "CS109", "CS111", "CS161"],
            "reason": "The BS CS program lists these 7 courses as core requirements."
        },
        {
            "id": "R2",
            "query": "How many courses do I need for the Computer Science minor?",
            "expected_keywords": ["6", "CS106A", "CS106B", "CS103", "CS107", "elective"],
            "reason": "4 core + 2 electives = 6 courses."
        },
        {
            "id": "R3",
            "query": "What math courses are required for the BS in Computer Science?",
            "expected_keywords": ["MATH51"],
            "reason": "MATH51 is listed under Mathematics Requirements."
        },
        {
            "id": "R4",
            "query": "What is the minimum GPA requirement for the CS major?",
            "expected_keywords": ["2.0"],
            "reason": "The program requires a 2.0 cumulative GPA."
        },
        {
            "id": "R5",
            "query": "Can elective courses for the CS minor be taken CR/NC?",
            "expected_keywords": ["letter grade", "not CR/NC"],
            "reason": "Elective courses must be taken for a letter grade."
        },
    ],
    "not_in_docs": [
        {
            "id": "N1",
            "query": "Who teaches CS106A this quarter?",
            "expected": "abstain",
            "reason": "Instructor information is not in the catalog documents."
        },
        {
            "id": "N2",
            "query": "Is CS161 offered in Summer quarter?",
            "expected": "abstain",
            "reason": "While we have OFFERED field, CS161 says Fall/Winter/Spring — system should note Summer is not listed but real-time availability is not in docs."
        },
        {
            "id": "N3",
            "query": "Can I get a prerequisite waiver for CS107 with instructor permission?",
            "expected": "abstain",
            "reason": "Instructor waivers are not documented in the catalog data."
        },
        {
            "id": "N4",
            "query": "What is the average class size for CS229?",
            "expected": "abstain",
            "reason": "Class size information is not in the catalog documents."
        },
        {
            "id": "N5",
            "query": "Can I take CS courses at a community college and transfer them to Stanford?",
            "expected": "abstain",
            "reason": "Specific transfer articulation agreements are not in the catalog data."
        },
    ],
}


# ─── Evaluation Logic ───────────────────────────────────────────────────────

def check_citations(response: str) -> bool:
    """Check if the response contains at least one URL citation."""
    return "http" in response.lower() or "https" in response.lower()


def check_abstention(response: str) -> bool:
    """Check if the response properly abstains (says it doesn't have the info)."""
    abstention_phrases = [
        "i don't have that information",
        "not in the provided catalog",
        "not available in the catalog",
        "not found in the documents",
        "not in the catalog",
        "cannot determine",
        "not documented",
        "no information available",
        "not included in the provided",
    ]
    lower = response.lower()
    return any(phrase in lower for phrase in abstention_phrases)


def run_evaluation():
    """Run the full 25-query evaluation and save results."""
    from crew import run

    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = {
        "timestamp": timestamp,
        "categories": {},
        "metrics": {},
        "example_transcripts": [],
    }

    total_queries = 0
    total_citations = 0
    total_abstain_correct = 0
    total_abstain_expected = 0
    total_eligible_correct = 0
    total_eligible_expected = 0

    for category, queries in TEST_QUERIES.items():
        print(f"\n{'='*70}")
        print(f"  Category: {category}")
        print(f"{'='*70}")

        category_results = []

        for q in queries:
            total_queries += 1
            print(f"\n  [{q['id']}] {q['query'][:60]}...")

            try:
                response = run(q["query"], verbose=False)
            except Exception as e:
                response = f"ERROR: {str(e)}"
                print(f"    ERROR: {e}")

            has_citation = check_citations(response)
            if has_citation:
                total_citations += 1

            result_entry = {
                "id": q["id"],
                "query": q["query"],
                "response": response,
                "has_citation": has_citation,
            }

            # Check category-specific correctness
            if category == "not_in_docs":
                total_abstain_expected += 1
                abstained = check_abstention(response)
                result_entry["abstained"] = abstained
                if abstained:
                    total_abstain_correct += 1
                print(f"    Abstained: {abstained}")

            elif category == "prerequisite_checks":
                total_eligible_expected += 1
                expected = q["expected"]
                # Simple heuristic: check if response matches expected decision
                lower_resp = response.lower()
                if expected == "eligible":
                    correct = "eligible" in lower_resp and "not eligible" not in lower_resp and "not_eligible" not in lower_resp
                else:
                    correct = "not eligible" in lower_resp or "not_eligible" in lower_resp or "cannot take" in lower_resp
                result_entry["expected"] = expected
                result_entry["correct"] = correct
                if correct:
                    total_eligible_correct += 1
                print(f"    Expected: {expected} | Correct: {correct}")

            print(f"    Has Citation: {has_citation}")
            category_results.append(result_entry)

            # Save example transcripts (first of each interesting type)
            if len(results["example_transcripts"]) < 3:
                if (category == "prerequisite_checks" and q["id"] == "P1") or \
                   (category == "multi_hop_chains" and q["id"] == "M1") or \
                   (category == "not_in_docs" and q["id"] == "N1"):
                    results["example_transcripts"].append({
                        "category": category,
                        "id": q["id"],
                        "query": q["query"],
                        "response": response,
                    })

            # Brief pause to respect rate limits
            time.sleep(1)

        results["categories"][category] = category_results

    # Calculate metrics
    citation_rate = (total_citations / total_queries * 100) if total_queries > 0 else 0
    abstention_accuracy = (total_abstain_correct / total_abstain_expected * 100) if total_abstain_expected > 0 else 0
    eligibility_accuracy = (total_eligible_correct / total_eligible_expected * 100) if total_eligible_expected > 0 else 0

    results["metrics"] = {
        "total_queries": total_queries,
        "citation_coverage_rate": f"{citation_rate:.1f}%",
        "abstention_accuracy": f"{abstention_accuracy:.1f}%",
        "eligibility_correctness": f"{eligibility_accuracy:.1f}%",
    }

    # Print summary
    print(f"\n{'='*70}")
    print("  EVALUATION SUMMARY")
    print(f"{'='*70}")
    print(f"  Total Queries:           {total_queries}")
    print(f"  Citation Coverage Rate:  {citation_rate:.1f}%")
    print(f"  Abstention Accuracy:     {abstention_accuracy:.1f}%")
    print(f"  Eligibility Correctness: {eligibility_accuracy:.1f}%")
    print(f"{'='*70}\n")

    # Save results to file
    results_path = os.path.join(config.RESULTS_DIR, f"evaluation_{timestamp}.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Results saved to: {results_path}\n")

    # Save example transcripts as readable text
    transcripts_path = os.path.join(config.RESULTS_DIR, f"transcripts_{timestamp}.txt")
    with open(transcripts_path, "w") as f:
        for i, t in enumerate(results["example_transcripts"]):
            f.write(f"{'='*70}\n")
            f.write(f"EXAMPLE TRANSCRIPT {i+1}: {t['category']}\n")
            f.write(f"{'='*70}\n")
            f.write(f"Query: {t['query']}\n\n")
            f.write(f"Response:\n{t['response']}\n\n")
    print(f"  Transcripts saved to: {transcripts_path}\n")

    return results


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_evaluation()
