# 03 — Model Context Protocol (MCP) 🔌

## 🎯 Objective

The objective of this experiment is to understand and implement the **Model Context Protocol (MCP)** using a local LLM.

The experiment extends the previous **Tool Calling** implementation by introducing MCP as a standardized communication layer between an AI application and external tools.

The goal is to understand:

- what MCP is
- how an MCP server exposes tools
- how an MCP client discovers available tools
- how tools can be invoked through MCP
- how MCP can decouple tool implementations from the AI application
- how an LLM can use tools exposed through MCP
- how this architecture differs from directly importing and executing Python functions

The experiment uses a local **Qwen3 8B** model running through **Ollama**.

No access to the host filesystem, hardware, or operating system is provided to the model.

All business data used in the experiment is synthetic.

---

## 💻 Environment

### Hardware

- MacBook Air M4
- 16 GB unified memory
- macOS

### Software

- Python 3.14
- Ollama 0.33.3
- Qwen3 8B
- MCP Python SDK 2.2.0
- `requests`

### Local LLM

The model used in this experiment is:

```text
qwen3:8b
```

The model runs locally through Ollama:

```text
http://localhost:11434
```

### MCP SDK

The official Python MCP SDK is used:

```bash
python -m pip install "mcp[cli]"
```

The experiment uses MCP SDK 2.x.

The server implementation uses:

```python
from mcp.server.mcpserver import MCPServer
```

---

## 📁 Project Structure

```text
03-mcp/
├── README.md
├── data/
│   ├── orders.json
│   └── customers.json
├── server/
│   └── server.py
├── client/
│   └── client.py
└── experiments/
```

The `data/` directory contains synthetic business data.

The `server/` directory contains the MCP server and its tools.

The `client/` directory contains the MCP client and the integration with Ollama/Qwen.

The `experiments/` directory is used to document individual tests.

---

## 🏗️ Architecture

The experiment is divided into three main components:

```text
                    ┌──────────────────┐
                    │     Qwen3 8B     │
                    │   Local LLM      │
                    └────────┬─────────┘
                             │
                             │ Tool definitions
                             │ + tool calls
                             ▼
                    ┌──────────────────┐
                    │   Python Client  │
                    │                  │
                    │  MCP Client      │
                    │  + Ollama bridge │
                    └────────┬─────────┘
                             │
                             │ MCP
                             ▼
                    ┌──────────────────┐
                    │   MCP Server     │
                    │                  │
                    │  get_order()     │
                    │  get_customer()  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Synthetic Data  │
                    │                  │
                    │ orders.json      │
                    │ customers.json   │
                    └──────────────────┘
```

An important architectural detail is that **Qwen is not directly communicating with the MCP server**.

The Python application acts as the bridge:

1. The MCP client connects to the MCP server.
2. The client discovers the available tools.
3. The Python application converts the MCP tool definitions into Ollama-compatible tool definitions.
4. The definitions are provided to Qwen.
5. Qwen decides whether a tool is required.
6. The Python client receives the tool call.
7. The MCP client invokes the requested tool.
8. The MCP server executes the tool.
9. The result is returned to the Python client.
10. The result is provided back to Qwen.
11. Qwen generates the final response.

---

## 🖥️ MCP Server

The MCP server is implemented using the official Python SDK.

```python
from mcp.server.mcpserver import MCPServer


mcp = MCPServer("AI R&D Lab")
```

The server exposes tools using the `@mcp.tool()` decorator.

---

### 🔧 Tool 1 — get_order

The first tool retrieves an order from the synthetic `orders.json` dataset.

```python
@mcp.tool()
def get_order(order_id: int) -> dict:
    """Retrieve information about an order using its order ID."""
```

The tool accepts:

```text
order_id: integer
```

Example:

```text
1002
```

The corresponding record is:

```json
{
  "order_id": 1002,
  "customer": "Beta S.p.A.",
  "product": "Monitor 27\"",
  "quantity": 12,
  "total": 3600,
  "status": "Processing"
}
```

---

### 👤 Tool 2 — get_customer

The second tool retrieves a customer from the synthetic `customers.json` dataset.

```python
@mcp.tool()
def get_customer(customer_name: str) -> dict:
    """Retrieve information about a customer by name."""
```

The tool accepts:

```text
customer_name: string
```

Example:

```text
Beta S.p.A.
```

The corresponding record is:

```json
{
  "customer": "Beta S.p.A.",
  "industry": "Manufacturing",
  "city": "Turin",
  "contact": "beta@example.com"
}
```

---

## 💻 MCP Client

The MCP client uses the server as a subprocess through standard input/output.

```python
from mcp import Client, StdioServerParameters
```

The server is defined as:

```python
server = StdioServerParameters(
    command="python",
    args=["03-mcp/server/server.py"],
)
```

The client then establishes the MCP connection:

```python
async with Client(server) as client:
```

This allows the client to communicate with the MCP server without directly importing the server's Python functions.

---

## 🔎 Tool Discovery

One of the main purposes of MCP is standardized tool discovery.

The client requests the tools exposed by the server:

```python
mcp_tools = await client.list_tools()
```

The returned definitions contain information such as:

- tool name
- description
- input schema

Example:

```text
Tool: get_order
Description: Retrieve information about an order using its order ID.
Input schema:
{
    'type': 'object',
    'properties': {
        'order_id': {
            'title': 'Order Id',
            'type': 'integer'
        }
    },
    'required': ['order_id']
}
```

The customer tool is discovered in the same way.

This means that the client does not need to manually define the MCP tools beforehand.

The server exposes them and the client discovers them.

---

## ⚡ Calling MCP Tools

Once a tool has been discovered, the MCP client can invoke it using:

```python
result = await client.call_tool(
    "get_order",
    {"order_id": 1002}
)
```

The server executes the function and returns the result through MCP.

Example result:

```json
{
  "order_id": 1002,
  "customer": "Beta S.p.A.",
  "product": "Monitor 27\"",
  "quantity": 12,
  "total": 3600,
  "status": "Processing"
}
```

The same mechanism is used for the customer tool:

```python
result = await client.call_tool(
    "get_customer",
    {"customer_name": "Beta S.p.A."}
)
```

---

## 🤖 Qwen + MCP Integration

The final implementation connects the local Qwen model with the MCP client.

The architecture is:

```text
User
 │
 ▼
Python Application
 │
 ├── MCP Client ──────► MCP Server ──────► Tool
 │
 └── Ollama ──────────► Qwen3 8B
```

The MCP tools are dynamically converted into Ollama-compatible tool definitions.

```python
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
```

Qwen receives these tools and decides whether one is required.

If a tool is required, the model produces a structured tool call.

Example:

```json
{
  "name": "get_order",
  "arguments": {
    "order_id": 1002
  }
}
```

The Python application then sends the request to the MCP server:

```python
result = await client.call_tool(
    function_name,
    arguments,
)
```

The returned information is then added to the conversation and sent back to Qwen.

Qwen can therefore formulate the final response using the actual tool result.

---

## 🧪 Experiments

### 🧪 Experiment 01 — MCP Tool Discovery

#### Question

The first test was performed without Qwen.

The client connected directly to the MCP server and requested the available tools.

#### Result

The server exposed:

```text
get_order
get_customer
```

The client also received their descriptions and input schemas.

#### Observation

The MCP client can discover the server's capabilities dynamically.

The client does not need to directly import the Python functions implemented by the server.

---

### 🧪 Experiment 02 — Direct MCP Tool Execution

#### Test

The client directly called:

```text
get_order(1002)
```

#### Result

```json
{
  "order_id": 1002,
  "customer": "Beta S.p.A.",
  "product": "Monitor 27\"",
  "quantity": 12,
  "total": 3600,
  "status": "Processing"
}
```

The client then called:

```text
get_customer("Beta S.p.A.")
```

#### Result

```json
{
  "customer": "Beta S.p.A.",
  "industry": "Manufacturing",
  "city": "Turin",
  "contact": "beta@example.com"
}
```

#### Observation

The MCP server correctly executes tools and returns structured information to the client.

---

### 🧪 Experiment 03 — Qwen Selects an MCP Tool

#### Question

```text
What is the status of order 1002?
```

#### Qwen decision

Qwen selected:

```text
get_order
```

with:

```json
{
  "order_id": 1002
}
```

#### MCP execution

The MCP server returned:

```json
{
  "order_id": 1002,
  "customer": "Beta S.p.A.",
  "product": "Monitor 27\"",
  "quantity": 12,
  "total": 3600,
  "status": "Processing"
}
```

#### Final answer

```text
The status of order 1002 is Processing.
```

#### Observation

The complete chain worked:

```text
User
→ Qwen
→ Tool selection
→ MCP Client
→ MCP Server
→ get_order
→ Result
→ Qwen
→ Final answer
```

---

### 🧪 Experiment 04 — Customer Lookup

#### Question

```text
What information do you have about Beta S.p.A.?
```

#### Qwen decision

Qwen selected:

```text
get_customer
```

with:

```json
{
  "customer_name": "Beta S.p.A."
}
```

#### MCP result

```json
{
  "customer": "Beta S.p.A.",
  "industry": "Manufacturing",
  "city": "Turin",
  "contact": "beta@example.com"
}
```

#### Observation

Qwen correctly selected the appropriate MCP tool based on the user's request.

---

### 🧪 Experiment 05 — No Tool Required

#### Question

```text
What is 25 multiplied by 4?
```

#### Result

Qwen answered:

```text
100
```

No MCP tool was called.

#### Observation

The model can distinguish between requests that require access to external data and requests that can be answered directly.

---

### 🧪 Experiment 06 — Unknown Customer

#### Question

```text
What information do you have about Omega S.p.A.?
```

#### Qwen decision

Qwen selected:

```text
get_customer
```

with:

```json
{
  "customer_name": "Omega S.p.A."
}
```

#### MCP result

The server returned:

```json
{
  "error": "Customer Omega S.p.A. not found"
}
```

#### Final answer

Qwen correctly reported that no record was available instead of inventing information about the customer.

#### Observation

The experiment demonstrates the importance of returning explicit errors from tools when requested information does not exist.

---

## 🔑 Key Findings

The experiment demonstrated several important concepts.

### 1. MCP provides a standardized interface

Tools can be exposed through a standardized protocol rather than being directly coupled to the application.

### 2. Tool discovery is dynamic

The client can request the tools available on the MCP server using:

```python
list_tools()
```

The client therefore does not need to hard-code every tool definition.

### 3. Tool execution is separated from the LLM

Qwen does not execute Python code directly.

The model proposes a tool call.

The Python MCP client performs the actual invocation.

### 4. MCP creates architectural decoupling

The tool implementation lives on the MCP server, while the AI application acts as a client.

This creates a separation between:

```text
AI / Application
```

and:

```text
Tools / Data / Services
```

### 5. MCP is not the LLM

MCP does not replace Qwen or Ollama.

It provides a protocol through which an AI application can interact with external capabilities.

### 6. MCP is not itself a tool

The tools are:

```text
get_order
get_customer
```

MCP defines how those capabilities are exposed, discovered and invoked.

---

## ⚖️ Comparison with Tool Calling

The previous experiment implemented tool calling directly inside the Python application.

The architecture was approximately:

```text
Qwen
 │
 ▼
Python application
 │
 ├── get_order()
 └── get_customer()
```

The application directly imported and executed the functions.

With MCP:

```text
Qwen
 │
 ▼
Python application
 │
 ▼
MCP Client
 │
 ▼
MCP Server
 │
 ├── get_order()
 └── get_customer()
```

The additional layer provides a standardized interface between the client and the tools.

This becomes particularly important when the number of tools and external services increases.

---

## 🔐 Security

Security remains an important requirement of the AI R&D Lab.

The model does not receive direct access to:

- the Mac filesystem
- the Mac hardware
- arbitrary shell commands
- arbitrary Python execution
- personal files
- operating system resources

The experiment uses only synthetic business data:

```text
orders.json
customers.json
```

The available capabilities are explicitly defined by the MCP server.

The model can request a tool, but it cannot arbitrarily execute an unknown function.

This follows the principle of **least privilege**.

---

## ⚠️ Important Architectural Limitation

This experiment should not yet be considered a fully autonomous AI agent.

The current architecture still contains explicit application logic controlling:

- communication with Ollama
- MCP client creation
- tool discovery
- conversion of MCP schemas into Ollama schemas
- execution of tool calls
- returning tool results to Qwen
- final response generation

The LLM is responsible for deciding **which tool to request**, but the surrounding Python application controls the execution workflow.

This distinction will become important in the next experiments involving agents and workflow orchestration.

---

## 🛡️ macOS Access Permission Issue

During the development of the previous Tool Calling experiment, macOS displayed several privacy permission prompts related to Visual Studio Code.

The prompts included access to:

- Desktop files
- data from other applications
- files managed by iCloud Drive

The exact operation responsible for these prompts was not conclusively identified.

The prompts were not reproduced consistently when restarting individual applications, and the available system logs did not provide conclusive evidence linking them to Qwen, Ollama, or the MCP implementation.

The issue therefore remains under observation.

No additional filesystem permissions are intentionally granted to the AI system as part of this experiment.

---

## 🔄 What MCP Changes Compared to Direct Tool Calling

The main conceptual difference is architectural.

With direct tool calling, the AI application owns the tools:

```text
Application
 ├── LLM
 ├── Tool definitions
 └── Tool implementations
```

With MCP, the application can interact with a separate standardized tool server:

```text
LLM
 │
Application / MCP Client
 │
MCP
 │
MCP Server
 │
Tools
```

This separation allows the same MCP server to potentially be used by different compatible clients.

The main value demonstrated by this experiment is therefore **standardization and decoupling**, rather than simply moving Python functions into another file.

---

## 📝 Conclusion

The MCP experiment successfully demonstrated:

- MCP server creation
- MCP tool definition
- MCP client creation
- dynamic tool discovery
- direct MCP tool execution
- integration between MCP and a local LLM
- LLM-based tool selection
- no-tool behavior
- error handling
- separation between model and tool execution
- controlled access to synthetic data

The experiment represents the transition from simple local LLM usage and direct Tool Calling toward a more modular AI architecture.

---

## 🚀 Next Step

The next experiment will focus on **Retrieval-Augmented Generation (RAG)**.

The objective will be to give the local LLM access to a controlled knowledge base and investigate how retrieval can provide relevant information to the model without embedding the entire knowledge base directly into the prompt.

Planned progression:

```text
01 — Local LLM
      ↓
02 — Tool Calling
      ↓
03 — MCP
      ↓
04 — RAG
      ↓
05 — SQL Agent
      ↓
06 — Agent Workflows / LangGraph
      ↓
07 — Multi-Agent Systems
      ↓
08 — AI Automation / n8n
      ↓
Final Project
```