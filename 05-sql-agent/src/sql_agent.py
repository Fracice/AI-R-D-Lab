
import re

from database import get_schema
from llm import chat


SYSTEM_PROMPT = """
Generate one valid SQLite SELECT query for the user's question.

Rules:
- Use only tables and columns in the provided schema.
- Use exact stored values for filters, including order status 'completed'.
- Use JOINs and aggregations when needed.
- Never modify data or database structure.
- Return only SQL, without explanations or Markdown.
- If the question cannot be answered, return exactly: -- CANNOT_ANSWER

Database schema:
"""


def generate_sql(question):
    """Generate a SQL query from a natural-language question."""
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    schema = get_schema()

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\n\nDatabase schema:\n" + schema
        },
        {
            "role": "user",
            "content": question.strip()
        }
    ]

    response = chat(messages, temperature=0)
    sql = response.strip()

    # Remove Markdown fences if the model returns them anyway.
    sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql).strip()

    if sql == "-- CANNOT_ANSWER":
        return None

    return sql


if __name__ == "__main__":
    question = "Calculate total completed order value for each customer. Join orders, customers, and order_items. Group by customer and sort by total value descending."
    query = generate_sql(question)

    print("Question:", question)
    print("Generated SQL:")
    print(query if query else "The question cannot be answered from the schema.")
