
from database import execute_query
from sql_agent import generate_sql


def ask_agent(question):
    """Generate SQL, execute it safely, and return the results."""
    sql = generate_sql(question)

    if sql is None:
        return {
            "question": question,
            "sql": None,
            "results": None,
            "error": "The question cannot be answered from the database schema."
        }

    try:
        results = execute_query(sql)
        return {
            "question": question,
            "sql": sql,
            "results": results,
            "error": None
        }
    except Exception as exc:
        return {
            "question": question,
            "sql": sql,
            "results": None,
            "error": f"{type(exc).__name__}: {exc}"
        }


def main():
    print("=" * 50)
    print("SQL Agent — Experiment 05")
    print("Ask questions about the sales database.")
    print("Type 'exit' to quit.")
    print("=" * 50)

    while True:
        try:
            question = input("\nYour question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not question:
            continue

        try:
            response = ask_agent(question)
        except Exception as exc:
            print(f"\nAgent error: {type(exc).__name__}: {exc}")
            print("You can try asking again.")
            continue

        if response["error"]:
            print("\nError:", response["error"])
            continue

        print("\nGenerated SQL:")
        print(response["sql"])

        print("\nResults:")
        if response["results"]:
            for row in response["results"]:
                print(row)
        else:
            print("No rows returned.")


if __name__ == "__main__":
    main()
