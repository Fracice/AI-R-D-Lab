import json
from pathlib import Path


DATA_FILE = Path(__file__).parent.parent / "orders.json"


def get_order(order_id: int) -> dict:
    """Retrieve an order by its ID."""

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        orders = json.load(file)

    for order in orders:
        if order["order_id"] == order_id:
            return order

    return {"error": f"Order {order_id} not found"}


if __name__ == "__main__":
    result = get_order(1002)
    print(json.dumps(result, indent=2))