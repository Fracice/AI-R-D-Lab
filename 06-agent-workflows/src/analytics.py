
import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data.json"


def load_sales_data():
    """Load the sales dataset from the JSON file."""
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_product_metrics(data):
    """Calculate revenue, cost, and gross profit for each product."""
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


def rank_products(products, metric="revenue", descending=True):
    """Rank products by a numeric metric."""
    allowed_metrics = {
        "units_sold",
        "revenue",
        "total_cost",
        "gross_profit",
        "margin_percentage",
    }

    if metric not in allowed_metrics:
        raise ValueError(f"Unsupported ranking metric: {metric}")

    return sorted(
        products,
        key=lambda product: product[metric],
        reverse=descending,
    )


def summarize_sales(data, products):
    """Calculate overall sales and profitability metrics."""
    total_units = sum(product["units_sold"] for product in products)
    total_revenue = sum(product["revenue"] for product in products)
    total_cost = sum(product["total_cost"] for product in products)
    total_profit = sum(product["gross_profit"] for product in products)

    return {
        "company": data["company"],
        "currency": data["currency"],
        "number_of_products": len(products),
        "total_units_sold": total_units,
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "total_gross_profit": round(total_profit, 2),
        "overall_margin_percentage": round(
            total_profit / total_revenue * 100
            if total_revenue > 0 else 0,
            2,
        ),
    }


if __name__ == "__main__":
    data = load_sales_data()
    products = calculate_product_metrics(data)
    summary = summarize_sales(data, products)

    print("Company:", summary["company"])
    print("Total revenue:", summary["currency"], summary["total_revenue"])
    print("Total gross profit:", summary["currency"], summary["total_gross_profit"])
    print("Overall margin:", f'{summary["overall_margin_percentage"]}%')

    print("\nProducts ranked by revenue:")
    for product in rank_products(products, metric="revenue"):
        print(
            f'{product["product"]}: '
            f'{summary["currency"]} {product["revenue"]:.2f}'
        )
