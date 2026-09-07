import json
import requests

from get_order import get_order
from get_customer import get_customer


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b"


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "Retrieve information about an order using its order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "The ID of the order to retrieve."
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer",
            "description": "Retrieve information about a customer using the customer name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "The name of the customer to retrieve."
                    }
                },
                "required": ["customer_name"]
            }
        }
    }
]


def call_llm(messages):
    """Send a conversation to Ollama and return the assistant message."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "tools": tools,
            "stream": False
        }
    )

    response.raise_for_status()

    return response.json()["message"]


def execute_tool(tool_call):
    """Execute an explicitly allowed tool."""

    function_name = tool_call["function"]["name"]
    arguments = tool_call["function"]["arguments"]

    if function_name == "get_order":
        return get_order(arguments["order_id"])

    elif function_name == "get_customer":
        return get_customer(arguments["customer_name"])

    else:
        return {"error": f"Unknown tool: {function_name}"}


def main():

    user_input = input("Ask Qwen a question: ")

    messages = [
        {
            "role": "user",
            "content": user_input
        }
    ]

    assistant_message = call_llm(messages)

    print("\nLLM response:")
    print(json.dumps(assistant_message, indent=2))

    if "tool_calls" in assistant_message:

        messages.append(assistant_message)

        for tool_call in assistant_message["tool_calls"]:

            tool_result = execute_tool(tool_call)

            print("\nTool result:")
            print(json.dumps(tool_result, indent=2))

            messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(tool_result)
                }
            )

        final_message = call_llm(messages)

        print("\nFinal answer:")
        print(final_message["content"])

    else:

        print("\nFinal answer:")
        print(assistant_message["content"])


if __name__ == "__main__":
    main()