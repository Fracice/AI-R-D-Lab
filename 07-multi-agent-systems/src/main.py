from orchestrator import run_multi_agent_workflow, print_report


def main():
    print("=" * 60)
    print("MULTI-AGENT BUSINESS INTELLIGENCE")
    print("=" * 60)
    print("Enter a business objective for the AI agent team.")
    print("Type 'exit' to quit.")

    while True:
        print()
        objective = input("Business objective: ").strip()

        if objective.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not objective:
            print("Please enter a non-empty objective.")
            continue

        result = run_multi_agent_workflow(objective)
        print()
        print_report(result)


if __name__ == "__main__":
    main()