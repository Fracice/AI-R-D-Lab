import json
from pathlib import Path

from mcp.server.mcpserver import MCPServer


BASE_DIR = Path(__file__).parent.parent
ORDERS_FILE = BASE_DIR / "data" / "orders.json"
CUSTOMERS_FILE = BASE_DIR / "data" / "customers.json"


mcp = MCPServer("AI R&D Lab")


@mcp.tool()
def get_order(order_id: int) -> dict:
    """Retrieve information about an order using its order ID."""
    with open(ORDERS_FILE, "r", encoding="utf-8") as file:
        orders = json.load(file)

    for order in orders:
        if order["order_id"] == order_id:
            return order

    return {"error": f"Order {order_id} not found"}


@mcp.tool()
def get_customer(customer_name: str) -> dict:
    """Retrieve information about a customer by name."""
    with open(CUSTOMERS_FILE, "r", encoding="utf-8") as file:
        customers = json.load(file)

    for customer in customers:
        if customer["customer"].lower() == customer_name.lower():
            return customer

    return {"error": f"Customer {customer_name} not found"}


if __name__ == "__main__":
    mcp.run()
