
import json

from agents.analyst import analyze_business_data
from agents.strategist import develop_strategy
from agents.reviewer import review_recommendations
from tools.analytics import (
    load_sales_data,
    calculate_product_metrics,
    summarize_sales,
    build_verified_facts,
)
from tools.validator import validate_recommendations


MAX_REVISION_ATTEMPTS = 2


def run_multi_agent_workflow(objective):
    state = {
        "objective": objective,
        "status": "running",
        "summary": {},
        "analysis": "",
        "recommendations": {},
        "review": {},
        "validation_issues": [],
        "revision_attempts": 0,
        "errors": [],
    }

    try:
        if not objective or not objective.strip():
            raise ValueError("Business objective cannot be empty.")

        # 1. Load source data and calculate verified metrics.
        data = load_sales_data()
        products = calculate_product_metrics(data)
        summary = summarize_sales(data, products)
        verified_facts = build_verified_facts(summary, products)

        state["summary"] = summary

        # 2. Analyst interprets verified metrics and Python-calculated rankings.
        analysis = analyze_business_data(summary, products)
        state["analysis"] = analysis

        # 3. Strategist generates structured JSON recommendations.
        recommendations = develop_strategy(
            analysis,
            objective,
            verified_facts,
        )

        # 4. Review and validate recommendations.
        while True:
            review = review_recommendations(
                objective,
                analysis,
                recommendations,
                verified_facts,
            )

            validation_issues = validate_recommendations(
                recommendations,
                verified_facts,
            )

            state["review"] = review
            state["validation_issues"] = validation_issues

            # Approval requires reviewer approval and valid metric references.
            if review["approved"] and not validation_issues:
                break

            if state["revision_attempts"] >= MAX_REVISION_ATTEMPTS:
                break

            # 5. Ask the Strategist to revise its recommendations.
            state["revision_attempts"] += 1

            feedback_parts = [
                review.get("feedback", ""),
                *review.get("issues", []),
                *validation_issues,
            ]

            revision_context = (
                analysis
                + "\n\nReviewer feedback and validation issues:\n"
                + "\n".join(feedback_parts)
                + "\n\nRevise the recommendations to address every issue. "
                "Use only product names and metric values from the verified "
                "reference data. Return the required JSON structure."
            )

            recommendations = develop_strategy(
                revision_context,
                objective,
                verified_facts,
            )

        state["recommendations"] = recommendations

        if state["validation_issues"]:
            state["status"] = "needs_review"
        elif state["review"].get("approved"):
            state["status"] = "completed"
        else:
            state["status"] = "needs_review"

    except Exception as exc:
        state["status"] = "failed"
        state["errors"].append({
            "type": type(exc).__name__,
            "message": str(exc),
        })

    return state


def print_report(state):
    print("=" * 60)
    print("MULTI-AGENT BUSINESS INTELLIGENCE REPORT")
    print("=" * 60)
    print("Objective:", state["objective"])
    print("Status:", state["status"])

    if state["summary"]:
        summary = state["summary"]
        currency = summary["currency"]

        print("\nVERIFIED METRICS")
        print("Company:", summary["company"])
        print("Period:", summary["period"])
        print(f"Revenue: {currency} {summary['total_revenue']:.2f}")
        print(
            f"Gross profit: "
            f"{currency} {summary['total_gross_profit']:.2f}"
        )
        print(
            f"Overall margin: "
            f"{summary['overall_margin_percentage']:.2f}%"
        )

    if state["analysis"]:
        print("\nANALYST FINDINGS")
        print(state["analysis"])

    if state["recommendations"]:
        print("\nSTRATEGIST RECOMMENDATIONS")

        items = state["recommendations"].get("recommendations", [])

        for item in items:
            print(f"\nPriority {item.get('priority', '?')}")
            print(item.get("recommendation", ""))
            print("Rationale:", item.get("rationale", ""))

            assumptions = item.get("assumptions", [])
            if assumptions:
                print("Assumptions:")
                for assumption in assumptions:
                    print(f"- {assumption}")

            supporting_metrics = item.get("supporting_metrics", [])
            if supporting_metrics:
                print("Supporting metrics:")
                for metric in supporting_metrics:
                    print(
                        f"- {metric.get('product', '?')}: "
                        f"{metric.get('metric', '?')} = "
                        f"{metric.get('value', '?')}"
                    )

    if state["review"]:
        print("\nREVIEWER")
        print("Approved:", state["review"].get("approved"))
        print("Feedback:", state["review"].get("feedback", ""))

        for issue in state["review"].get("issues", []):
            print("-", issue)

    if state["validation_issues"]:
        print("\nDETERMINISTIC VALIDATION ISSUES")
        for issue in state["validation_issues"]:
            print("-", issue)
    elif state["recommendations"]:
        print("\nDeterministic validation: no metric inconsistencies detected.")

    print("\nRevision attempts:", state["revision_attempts"])

    if state["errors"]:
        print("\nERRORS")
        for error in state["errors"]:
            print(f"- {error['type']}: {error['message']}")


if __name__ == "__main__":
    objective = (
        "Identify the most profitable products and recommend "
        "actions to improve business profitability."
    )

    result = run_multi_agent_workflow(objective)
    print_report(result)
