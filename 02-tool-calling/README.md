# 02 — Tool Calling

## 🎯 Objective

The objective of this experiment is to understand how a Large Language Model can interact with external functions through tool calling.

The experiment focuses on:

- Defining tools that can be used by an LLM
- Allowing the model to select the appropriate tool
- Passing structured arguments to external functions
- Returning tool results to the model
- Understanding the difference between tool selection and tool execution
- Testing how the model handles missing or unavailable information

---

## 🛠️ Environment

| Component | Configuration |
|---|---|
| Hardware | MacBook Air M4 (2025) |
| Memory | 16 GB unified memory |
| Runtime | Ollama |
| Model | Qwen3 8B |
| Inference | Local |
| Programming language | Python |
| Data format | JSON |
| Data | Synthetic business data |

---

## 🧪 Experiment 01 — Order Lookup

### Prompt

> What is the status of order 1002?

### Observation

The model identified that information about a specific order was required and selected the `get_order` tool.

The model generated the following structured request:

```json
{
  "order_id": 1002
}
```

Python executed the function and retrieved the corresponding order from the controlled dataset.

The result indicated that order 1002 was in `Processing` status.

### Result

The model successfully selected the appropriate tool, generated the correct parameter, and used the returned data to formulate the final response.

---

## 🧪 Experiment 02 — Customer Lookup

### Prompt

> What information do you have about Beta S.p.A.?

### Observation

The model identified that the request concerned a customer rather than an order and selected the `get_customer` tool.

The model generated:

```json
{
  "customer_name": "Beta S.p.A."
}
```

The function returned the corresponding customer information from the controlled dataset.

### Result

The model successfully selected between multiple available tools according to the user's request.

---

## 🧪 Experiment 03 — Tool Selection

### Prompt

> What is the total value of order 1004?

### Observation

The model correctly selected `get_order` and provided:

```json
{
  "order_id": 1004
}
```

The function returned an order with a total value of `8000`.

### Result

The model correctly identified the relevant tool even when multiple tools were available.

---

## 🧪 Experiment 04 — No Tool Required

### Prompt

> What is 25 multiplied by 4?

### Observation

The available tools were not relevant to the request.

The model therefore did not generate a tool call and answered directly:

```text
100
```

### Result

The model can determine that no available tool is required for a request.

---

## 🧪 Experiment 05 — Missing Information

### Prompt

> Tell me the phone number of Beta S.p.A.

### Observation

The model selected `get_customer` and retrieved the customer record.

However, the dataset did not contain a phone number.

The model correctly stated that the phone number was not available instead of inventing one.

### Result

The model successfully handled information that was not present in the tool result.

---

## 🧪 Experiment 06 — Unknown Customer

### Prompt

> What information do you have about Omega S.p.A.?

### Observation

The model selected `get_customer`.

The function returned:

```json
{
  "error": "Customer Omega S.p.A. not found"
}
```

The model correctly reported that no information about the customer was available.

### Result

The model successfully handled an error returned by an external tool without inventing a customer record.

---

## 🔎 Key Findings

Tool Calling allows an LLM to interact with external functions without giving the model direct access to their implementation.

The model can:

- Select an appropriate tool
- Generate structured arguments
- Decide when no tool is required
- Use external results as context
- Handle missing information
- Handle errors returned by tools

However, the model does not directly execute the functions.

The Python application controls tool execution through an explicit allowlist.

### Core Principle

> The LLM can request a capability, but the application controls whether and how that capability is executed.

---

## 🔐 Security Consideration

The model was not given unrestricted access to the user's computer.

The available tools operate only on controlled synthetic datasets.

The application explicitly defines which functions can be executed.

The model cannot directly:

- Execute arbitrary Python code
- Execute shell commands
- Read arbitrary files
- Access the operating system
- Execute an undefined tool

This follows a least-privilege approach.

---

## ⚠️ macOS Access Permission Issue

During the development of this experiment, macOS unexpectedly displayed permission requests from Visual Studio Code related to:

- Desktop files
- Data from other applications
- Files managed by iCloud Drive

This was investigated because the experiment was designed specifically to prevent the LLM from having unrestricted access to the local computer.

### Observation

The Python application only accesses the synthetic datasets used by the experiment:

```text
02-tool-calling/orders.json
02-tool-calling/customers.json
```

Ollama communicates locally through:

```text
http://localhost:11434
```

No tool was implemented for arbitrary filesystem access.

### Controlled Test

The same program was executed directly from Terminal while Visual Studio Code was completely closed.

The program executed successfully and no macOS permission popup appeared.

This suggested that the behavior was related to the Visual Studio Code execution environment rather than the Tool Calling implementation itself.

### TCC Investigation

macOS TCC logs showed an access request associated with the Visual Studio Code code identity:

```text
com.microsoft.VSCode
```

The request referenced an Apple File Provider domain.

Shortly afterwards, macOS resolved:

```text
com.apple.filesystems.netfs.PlugInLibraryService
```

as an XPC service associated with Visual Studio Code.

No evidence was found in the relevant logs linking the request specifically to Copilot, Ollama, or Qwen.

The exact operation that triggered the user-facing macOS popup was not conclusively identified.

The issue will therefore remain under observation during subsequent experiments.

---

## 🚀 Next Step

The next experiment will introduce **Model Context Protocol (MCP)**.

Instead of manually defining and orchestrating tools inside the Python application, we will investigate how tools and context can be exposed through a standardized protocol.

The goal will be to move from:

```text
LLM
 ↓
Python Application
 ↓
Tool
 ↓
Controlled Data
 ↓
Result
 ↓
LLM
 ↓
Response
```

to a more standardized architecture based on:

```text
LLM
 ↓
MCP Client
 ↓
MCP Server
 ↓
Tool / Resource
 ↓
Result
 ↓
LLM
 ↓
Response
```