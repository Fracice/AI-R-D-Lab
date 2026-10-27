
from workflow import run_workflow, print_workflow_report


def main():
    print("=" * 50)
    print("BUSINESS ANALYSIS AGENT")
    print("Powered by Ollama + Qwen3 8B")
    print("Type 'exit' to quit.")
    print("=" * 50)

    while True:
        try:
            objective = input("\nWhat would you like to analyze? ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if objective.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not objective:
            continue

        try:
            state = run_workflow(objective)
            print_workflow_report(state)
        except Exception as exc:
            print(f"\nAgent error: {type(exc).__name__}: {exc}")
            print("Please try another objective.")


if __name__ == "__main__":
    main()
