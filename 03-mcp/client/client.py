import asyncio
import json

import requests
from mcp import Client, StdioServerParameters


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b"


def call_qwen(messages, tools):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "tools": tools,
            "stream": False,
        },
    )

    response.raise_for_status()

    return response.json()["message"]


async def main():
    server = StdioServerParameters(
        command="python",
        args=["03-mcp/server/server.py"],
    )

    async with Client(server) as client:

        # Discover tools exposed by the MCP server
        mcp_tools = await client.list_tools()

        print("=== MCP Tools ===")

        for tool in mcp_tools.tools:
            print(f"- {tool.name}")
            print(f"  Description: {tool.description}")
            print(f"  Input schema: {tool.input_schema}")

        # Convert MCP tool definitions into Ollama tool definitions
        ollama_tools = []

        for tool in mcp_tools.tools:
            ollama_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema,
                    },
                }
            )

        user_input = input("\nAsk Qwen a question: ")

        messages = [
            {
                "role": "user",
                "content": user_input,
            }
        ]

        # Ask Qwen to decide whether a tool is required
        assistant_message = call_qwen(messages, ollama_tools)

        print("\n=== Qwen Decision ===")
        print(json.dumps(assistant_message, indent=2))

        # No tool required
        if "tool_calls" not in assistant_message:
            print("\n=== Final Answer ===")
            print(assistant_message["content"])
            return

        # Tool required
        messages.append(assistant_message)

        for tool_call in assistant_message["tool_calls"]:

            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            print("\n=== MCP Tool Call ===")
            print(f"Tool: {function_name}")
            print(f"Arguments: {arguments}")

            result = await client.call_tool(
                function_name,
                arguments,
            )

            tool_content = []

            for content in result.content:
                if hasattr(content, "text"):
                    tool_content.append(content.text)
                else:
                    tool_content.append(str(content))

            tool_result = "\n".join(tool_content)

            print("\n=== MCP Tool Result ===")
            print(tool_result)

            messages.append(
                {
                    "role": "tool",
                    "content": tool_result,
                }
            )

        # Ask Qwen to formulate the final response
        final_message = call_qwen(messages, ollama_tools)

        print("\n=== Final Answer ===")
        print(final_message["content"])


if __name__ == "__main__":
    asyncio.run(main())
