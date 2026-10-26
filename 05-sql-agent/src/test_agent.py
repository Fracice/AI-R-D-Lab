
from sql_agent import generate_sql
from database import execute_query


def main():
    question = "What is the total value of completed orders for each customer, ordered from highest to lowest?"

    print(f"Question: {question}")

    sql = generate_sql(question)
    if sql is None:
        print("The question cannot be answered from the database schema.")
        return

    print("\nGenerated SQL:")
    print(sql)

    print("\nQuery results:")
    try:
        rows = execute_query(sql)
        for row in rows:
            print(row)
    except Exception as exc:
        print(f"Query execution failed: {exc}")


if __name__ == "__main__":
    main()
