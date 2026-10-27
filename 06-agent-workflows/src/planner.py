
import json

from llm import chat


ALLOWED_STEPS = [
    "summarize_sales",
    "rank_by_revenue",
    "rank_by_profit",
    "rank_by_units_sold",
    "rank_by_margin",
]


SYSTEM_PROMPT = """
You are the planning component of a business analysis agent.

Your task is to convert the user's business objective into an ordered
list of analysis steps.

Available steps:
- summarize_sales: calculate overall sales and profitability metrics.
- rank_by_revenue: rank products by total revenue, highest first.
- rank_by_profit: rank products by gross profit, highest first.
- rank_by_units_sold: rank products by units sold, highest first.
- rank_by_margin: rank products by gross margin percentage, highest first.

Rules:
- Select only steps that help answer the user's objective.
- Return steps in the order they should be executed.
- Do not invent step names.
- Do not generate Python code or SQL.
- Return only a valid JSON object in this format:
  {"steps": ["summarize_sales", "rank_by_profit"]}
- If the objective is unrelated to the available data, return:
  {"steps": []}
"""


def create_plan(objective):
    """Generate and validate a workflow plan from a user objective."""

    if not objective or not objective.strip():
        raise ValueError("Objective cannot be empty.")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": objective.strip()},
    ]

    response = chat(messages, temperature=0)

    try:
        plan = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"The model did not return valid JSON: {response}"
        ) from exc

    if not isinstance(plan, dict):
        raise ValueError("The plan must be a JSON object.")

    steps = plan.get("steps")

    if not isinstance(steps, list):
        raise ValueError("The plan must contain a list called 'steps'.")

    if not all(isinstance(step, str) for step in steps):
        raise ValueError("Every workflow step must be a string.")

    invalid_steps = [
        step for step in steps if step not in ALLOWED_STEPS
    ]

    if invalid_steps:
        raise ValueError(f"Unsupported workflow steps: {invalid_steps}")

    if len(steps) != len(set(steps)):
        raise ValueError("The plan contains duplicate steps.")

    return {"objective": objective.strip(), "steps": steps}


if __name__ == "__main__":
    objective = (
        "Identify the most profitable products and summarize overall sales."
    )

    plan = create_plan(objective)

    print("Objective:", plan["objective"])
    print("Planned steps:")
    for index, step in enumerate(plan["steps"], start=1):
        print(f"{index}. {step}")
