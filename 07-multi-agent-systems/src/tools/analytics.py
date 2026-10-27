
import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[2] / "data.json"


def load_sales_data():
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_product_metrics(data):
    products = []

    for sale in data["sales"]:
        revenue = sale["units_sold"] * sale["unit_price"]
        total_cost = sale["units_sold"] * sale["unit_cost"]
        gross_profit = revenue - total_cost
        margin_percentage = (
            gross_profit / revenue * 100 if revenue > 0 else 0
        )

        products.append({
            "product": sale["product"],
            "category": sale["category"],
            "units_sold": sale["units_sold"],
            "revenue": round(revenue, 2),
            "total_cost": round(total_cost, 2),
            "gross_profit": round(gross_profit, 2),
            "margin_percentage": round(margin_percentage, 2),
        })

    return products


def summarize_sales(data, products):
    total_units = sum(product["units_sold"] for product in products)
    total_revenue = sum(product["revenue"] for product in products)
    total_cost = sum(product["total_cost"] for product in products)
    total_profit = sum(product["gross_profit"] for product in products)

    return {
        "company": data["company"],
        "period": data["period"],
        "currency": data["currency"],
        "number_of_products": len(products),
        "total_units_sold": total_units,
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "total_gross_profit": round(total_profit, 2),
        "overall_margin_percentage": round(
            total_profit / total_revenue * 100 if total_revenue > 0 else 0,
            2,
        ),
    }


def build_verified_facts(summary, products):
    """Build a deterministic reference of verified business facts."""
    facts = {
        "company": summary["company"],
        "period": summary["period"],
        "currency": summary["currency"],
        "total_revenue": summary["total_revenue"],
        "total_gross_profit": summary["total_gross_profit"],
        "overall_margin_percentage": summary["overall_margin_percentage"],
        "total_units_sold": summary["total_units_sold"],
        "number_of_products": summary["number_of_products"],
        "products": {},
    }

    for product in products:
        facts["products"][product["product"]] = {
            "category": product["category"],
            "units_sold": product["units_sold"],
            "revenue": product["revenue"],
            "total_cost": product["total_cost"],
            "gross_profit": product["gross_profit"],
            "margin_percentage": product["margin_percentage"],
        }

    return facts


def build_product_rankings(products):
    """
    Build deterministic product rankings from calculated metrics.

    Rank 1 always represents the highest value for each metric.
    """
    ranking_definitions = {
        "revenue": "revenue",
        "gross_profit": "gross_profit",
        "margin_percentage": "margin_percentage",
        "units_sold": "units_sold",
    }

    rankings = {}

    for ranking_name, metric_name in ranking_definitions.items():
        ordered_products = sorted(
            products,
            key=lambda product: product[metric_name],
            reverse=True,
        )

        rankings[ranking_name] = [
            {
                "rank": rank,
                "product": product["product"],
                "value": product[metric_name],
            }
            for rank, product in enumerate(ordered_products, start=1)
        ]

    return rankings


def build_analyst_context(summary, products):
    """
    Prepare calculated metrics and rankings for the Analyst.

    All numerical facts and product rankings are computed by Python.
    The LLM is responsible for interpretation, not calculation.
    """
    return {
        "summary": summary,
        "products": products,
        "rankings": build_product_rankings(products),
        "analysis_constraints": [
            "Treat the supplied metrics and rankings as the source of truth.",
            "Do not recalculate or reorder numerical rankings.",
            "Distinguish total gross profit from margin percentage.",
            "Do not associate a product with another product's metrics.",
            "Do not infer causes from sales data alone.",
            "State limitations when the data is insufficient.",
        ],
    }


if __name__ == "__main__":
    data = load_sales_data()
    products = calculate_product_metrics(data)
    summary = summarize_sales(data, products)
    rankings = build_product_rankings(products)

    print("Company:", summary["company"])
    print("Period:", summary["period"])
    print("Total revenue:", summary["currency"], summary["total_revenue"])
    print("Gross profit:", summary["currency"], summary["total_gross_profit"])
    print("Overall margin:", f'{summary["overall_margin_percentage"]:.2f}%')

    for metric, ranking in rankings.items():
        print(f"\nRanking by {metric}:")
        for item in ranking:
            print(
                f"{item['rank']}. {item['product']}: {item['value']}"
            )
