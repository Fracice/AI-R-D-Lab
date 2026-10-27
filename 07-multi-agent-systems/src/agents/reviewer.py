import json

from llm import chat


SYSTEM_PROMPT = """
You are the Reviewer agent in a multi-agent business intelligence team.

Your responsibility is to evaluate the quality and reliability of business
recommendations using the verified reference data supplied to you.

Check:
- Whether recommendations address the original business objective.
- Whether numerical claims match the verified reference data.
- Whether product names and metrics are valid.
- Whether factual claims are supported by the supplied analysis.
- Whether assumptions are clearly identified.
- Whether recommendations are actionable and logically justified.
- Whether the available data is sufficient for the conclusions.

Rules:
- Treat verified_reference_data as the source of truth for numerical facts.
- Never approve a numerical claim that contradicts the verified reference data.
- Identify unsupported claims and explain why they are unsupported.
- Suggest specific improvements when needed.
- Return valid JSON only, using this structure:
  {
    "approved": true,
    "issues": [],
    "feedback": "The recommendations are supported by the verified data."
  }
- Set "approved" to false if important issues need to be corrected.
- The "issues" field must be a list of strings.
- The "feedback" field must be a string.
"""


def review_recommendations(
    objective,
    analysis,
    recommendations,
    verified_facts,
):
    payload = {
        "objective": objective,
        "analyst_findings": analysis,
        "recommendations": recommendations,
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
        review = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Reviewer did not return valid JSON: {response}"
        ) from exc

    if not isinstance(review, dict):
        raise ValueError("Reviewer response must be a JSON object.")

    if not isinstance(review.get("approved"), bool):
        raise ValueError("'approved' must be a boolean.")

    if not isinstance(review.get("issues"), list) or not all(
        isinstance(issue, str) for issue in review["issues"]
    ):
        raise ValueError("'issues' must be a list of strings.")

    if not isinstance(review.get("feedback"), str):
        raise ValueError("'feedback' must be a string.")

    return review


if __name__ == "__main__":
    print(
        "Reviewer agent updated to use verified reference data."
    )