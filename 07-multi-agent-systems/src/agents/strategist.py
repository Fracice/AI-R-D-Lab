import json

from llm import chat


SYSTEM_PROMPT = """
You are the Strategist agent in a multi-agent business intelligence team.

Your responsibility is to turn the Analyst's findings into practical,
prioritized business recommendations.

Return valid JSON only, with no Markdown fences and no text outside the JSON.
Use exactly this structure:

{
  "recommendations": [
    {
      "recommendation": "A concrete business action",
      "priority": 1,
      "supporting_metrics": [
        {
          "product": "Exact product name from verified data",
          "metric": "margin_percentage",
          "value": 65.71
        }
      ],
      "rationale": "Why this action addresses the objective",
      "assumptions": []
    }
  ]
}

Rules:
- Base recommendations on the Analyst's findings and verified reference data.
- Do not invent products, numerical values, facts, causes, budgets, or forecasts.
- Product names, metric names, and metric values in supporting_metrics must
  exactly match the supplied verified reference data.
- Allowed product metrics are: units_sold, revenue, gross_profit,
  and margin_percentage.
- Only include supporting_metrics that directly support the recommendation.
- If a recommendation has no directly relevant metric, use an empty list.
- Clearly distinguish assumptions from verified facts.
- Put the most important recommendation first; priorities start at 1.
- Do not repeat the entire analysis.
- Return a concise, actionable answer in English.
"""


def develop_strategy(analysis, objective, verified_facts):
    payload = {
        "business_objective": objective,
        "analyst_findings": analysis,
        "verified_reference_data": verified_facts,
    }

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": json.dumps(payload, indent=2),
        },
    ]

    response = chat(messages, temperature=0)

    try:
        result = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Strategist did not return valid JSON: {response}"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError("Strategist response must be a JSON object.")

    if not isinstance(result.get("recommendations"), list):
        raise ValueError(
            "'recommendations' must be a list."
        )

    return result


if __name__ == "__main__":
    print(
        "Strategist agent updated to return structured JSON recommendations."
    )