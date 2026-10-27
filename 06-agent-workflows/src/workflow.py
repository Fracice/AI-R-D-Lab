
from analytics import (
    load_sales_data,
    calculate_product_metrics,
    rank_products,
    summarize_sales,
)
from planner import create_plan


def run_workflow(objective):
    """Plan first, then execute the approved business analysis steps."""

    state = {
        "objective": objective,
        "status": "running",
        "plan": [],
        "steps": [],
        "data": {},
        "errors": [],
    }

    try:
        # Step 1: Plan the task before loading the dataset
        plan = create_plan(objective)
        state["plan"] = plan["steps"]

        if not state["plan"]:
            state["status"] = "unsupported"
            return state

        state["steps"].append({
            "name": "create_plan",
            "status": "completed",
        })

        # Step 2: Load data only when the objective is supported
        data = load_sales_data()
        products = calculate_product_metrics(data)

        state["data"]["company"] = data["company"]
        state["data"]["products"] = products

        state["steps"].append({
            "name": "load_and_calculate_metrics",
            "status": "completed",
        })

        # Step 3: Execute only approved operations
        for step_name in state["plan"]:
            if step_name == "summarize_sales":
                state["data"]["summary"] = summarize_sales(data, products)

            elif step_name == "rank_by_revenue":
                state["data"]["revenue_ranking"] = rank_products(
                    products, metric="revenue"
                )

            elif step_name == "rank_by_profit":
                state["data"]["profit_ranking"] = rank_products(
                    products, metric="gross_profit"
                )

            elif step_name == "rank_by_units_sold":
                state["data"]["units_ranking"] = rank_products(
                    products, metric="units_sold"
                )

            elif step_name == "rank_by_margin":
                state["data"]["margin_ranking"] = rank_products(
                    products, metric="margin_percentage"
                )

            state["steps"].append({
                "name": step_name,
                "status": "completed",
            })

        state["status"] = "completed"

    except Exception as exc:
        state["status"] = "failed"
        state["errors"].append({
            "type": type(exc).__name__,
            "message": str(exc),
        })

    return state


def print_workflow_report(state):
    """Display the execution plan, status, and available results."""

    print("=" * 50)
    print("BUSINESS ANALYSIS WORKFLOW")
    print("=" * 50)
    print("Objective:", state["objective"])
    print("Status:", state["status"])

    print("\nPlanned steps:")
    for index, step in enumerate(state["plan"], start=1):
        print(f"{index}. {step}")

    print("\nExecution steps:")
    for step in state["steps"]:
        print(f'- {step["name"]}: {step["status"]}')

    if state["status"] == "completed":
        print("\nResults:")

        if "summary" in state["data"]:
            summary = state["data"]["summary"]
            print("Company:", summary["company"])
            print(
                f'Total revenue: {summary["currency"]} '
                f'{summary["total_revenue"]:.2f}'
            )
            print(
                f'Gross profit: {summary["currency"]} '
                f'{summary["total_gross_profit"]:.2f}'
            )
            print(
                "Overall margin:",
                f'{summary["overall_margin_percentage"]:.2f}%'
            )

        ranking_keys = {
            "revenue_ranking": ("Revenue", "revenue"),
            "profit_ranking": ("Gross profit", "gross_profit"),
            "units_ranking": ("Units sold", "units_sold"),
            "margin_ranking": ("Margin", "margin_percentage"),
        }

        for key, (label, metric) in ranking_keys.items():
            if key not in state["data"]:
                continue

            print(f"\nProducts ranked by {label.lower()}:")
            for product in state["data"][key]:
                value = product[metric]
                suffix = "%" if metric == "margin_percentage" else ""
                print(f'- {product["product"]}: {value:.2f}{suffix}')

    elif state["status"] == "unsupported":
        print("\nThe objective cannot be answered with available operations.")

    if state["errors"]:
        print("\nErrors:")
        for error in state["errors"]:
            print(f'- {error["type"]}: {error["message"]}')


if __name__ == "__main__":
    objective = (
        "Identify the most profitable products and summarize overall sales."
    )
    state = run_workflow(objective)
    print_workflow_report(state)
