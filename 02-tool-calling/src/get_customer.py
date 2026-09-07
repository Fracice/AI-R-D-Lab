import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "customers.json"


def get_customer(customer_name: str) -> dict:
    """Retrieve information about a customer by name."""
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        customers = json.load(file)

    for customer in customers:
        if customer["customer"].lower() == customer_name.lower():
            return customer

    return {"error": f"Customer {customer_name} not found"}


if __name__ == "__main__":
    result = get_customer("Beta S.p.A.")
    print(json.dumps(result, indent=2))