# 06 — Agent Workflows

## 🎯 Objective

The objective of this experiment is to understand how an LLM can dynamically plan and coordinate multiple operations to complete a business analysis task.

Unlike a fixed workflow, this experiment introduces an LLM-based planner that selects analysis steps according to the user's objective.

The experiment focuses on:

- Translating natural-language objectives into structured plans
- Using an LLM to select from predefined operations
- Validating model-generated plans before execution
- Coordinating multiple Python functions through a workflow engine
- Maintaining shared state across execution steps
- Handling unsupported requests and execution errors
- Measuring local LLM response time

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
| Dataset | Synthetic sales data |
| Dependencies | Python standard library |

The LLM communicates with Ollama through its local HTTP API. No external LLM API is required.

---

## 🏗️ Architecture

The experiment separates planning, execution, and data analysis into independent components.

```text
User
 ↓
main.py
 ↓
workflow.py
 ├── planner.py
 │    ↓
 │   llm.py
 │    ↓
 │   Ollama / Qwen3 8B
 │
 └── analytics.py
      ↓
     data.json
 ↓
Business Analysis Report
```

### Components

#### LLM Client

`llm.py` provides a local client for Ollama.

It handles:

- HTTP requests to the Ollama chat API
- Model selection
- Response parsing
- Response-time measurement
- Connection error handling

The client uses `qwen3:8b` with thinking disabled for this structured planning task.

#### Planner

`planner.py` translates a business objective into an ordered list of predefined operations.

The planner requests JSON output from the model and validates the response before returning it to the workflow engine.

Available operations:

- `summarize_sales`
- `rank_by_revenue`
- `rank_by_profit`
- `rank_by_units_sold`
- `rank_by_margin`

Only operations included in the allowlist are accepted.

#### Workflow Engine

`workflow.py` coordinates the execution.

It:

1. Requests a plan from the planner.
2. Rejects objectives that produce an empty plan.
3. Loads the dataset when a supported plan is available.
4. Calculates product metrics.
5. Executes the selected operations.
6. Records execution status, results, and errors.
7. Produces a report.

The execution logic remains controlled by Python. The LLM selects operations but cannot execute arbitrary Python code.

#### Analytics Engine

`analytics.py` contains deterministic business calculations.

It calculates:

- Revenue per product
- Total cost per product
- Gross profit per product
- Gross margin percentage
- Overall revenue and profitability
- Product rankings by selected metrics

The analytics engine is independent of the LLM and can be tested separately.

#### Dataset

`data.json` contains a synthetic sales dataset for TechStore.

It includes six products, with information about categories, units sold, unit prices, and unit costs.

The dataset is used exclusively for experimentation.

#### Interactive Interface

`main.py` provides a terminal interface that accepts multiple objectives during the same session.

The user can submit questions in natural language and inspect the generated plan and execution results.

---

## 🔧 Implementation

### 1. Dataset and Analytics

The dataset contains six products:

- Laptop
- Smartphone
- Monitor
- Headphones
- Keyboard
- Mouse

The analytics engine calculates revenue as:

```text
Revenue = Units Sold × Unit Price
```

Gross profit is calculated as:

```text
Gross Profit = Revenue − Total Cost
```

Gross margin percentage is calculated as:

```text
Gross Margin = Gross Profit / Revenue × 100
```

All numerical calculations are performed by Python rather than estimated by the LLM.

### 2. Dynamic Planning

The planner receives the user's objective and selects the relevant operations.

For example:

```text
Objective:
Identify the most profitable products and summarize overall sales.
```

The model generated:

```json
{
  "steps": [
    "summarize_sales",
    "rank_by_profit"
  ]
}
```

The workflow engine validates and executes the selected operations.

### 3. Controlled Execution

The workflow uses a shared state containing:

- The original objective
- The generated plan
- Execution status
- Completed steps
- Intermediate data and results
- Errors

The state makes the workflow easier to inspect and debug.

Unsupported objectives return an `unsupported` status rather than being executed with an invented analysis.

### 4. Running the Experiment

Run the interactive agent from the repository root:

```bash
python3 06-agent-workflows/src/main.py
```

The user can enter business questions such as:

```text
Which products have the highest gross margin percentage?
```

To terminate the session, enter:

```text
exit
```

The LLM client and planner can also be tested independently:

```bash
python3 06-agent-workflows/src/llm.py
python3 06-agent-workflows/src/planner.py
```

---

## 🧪 Experiment 01 — Business Summary and Profit Ranking

### Objective

Identify the most profitable products and summarize overall sales.

### Generated Plan

The model selected:

1. `summarize_sales`
2. `rank_by_profit`

### Results

| Metric | Result |
|---|---:|
| Total revenue | EUR 203,800.00 |
| Total cost | EUR 132,610.00 |
| Gross profit | EUR 71,190.00 |
| Overall gross margin | 34.93% |

Product ranking by gross profit:

| Product | Gross profit |
|---|---:|
| Smartphone | EUR 28,800.00 |
| Laptop | EUR 15,750.00 |
| Headphones | EUR 9,000.00 |
| Monitor | EUR 8,250.00 |
| Keyboard | EUR 5,250.00 |
| Mouse | EUR 4,140.00 |

### Observation

The model selected two operations relevant to the objective. Python executed the calculations and produced the report.

The LLM was responsible for planning, while the analytics engine was responsible for numerical correctness.

---

## 🧪 Experiment 02 — Product Margin Ranking

### Objective

Identify products with the highest gross margin percentage.

### Generated Plan

```text
rank_by_margin
```

### Results

| Product | Gross margin |
|---|---:|
| Mouse | 65.71% |
| Keyboard | 58.33% |
| Headphones | 56.25% |
| Monitor | 36.67% |
| Smartphone | 30.00% |
| Laptop | 29.17% |

### Observation

The model selected only the operation required to answer the question.

The workflow did not execute the general business summary or the revenue ranking.

This demonstrates objective-dependent operation selection.

---

## 🧪 Experiment 03 — Unsupported Objective

### Objective

```text
Which customers are most likely to buy next month?
```

### Expected Behavior

The dataset contains aggregated product sales but does not provide customer-level purchase histories or time-series information.

The planner should therefore return an empty list of steps.

### Result

```text
Status: unsupported
```

No analysis operations were executed.

The workflow was subsequently modified to request the plan before loading the dataset. The test confirmed that unsupported objectives no longer trigger unnecessary data loading and metric calculations.

### Observation

An agent should not attempt to answer every request. It should recognize when the available operations and data are insufficient.

---

## 🧪 Experiment 04 — Local Inference Latency

The following Ollama response times were observed during local tests:

| Test | Response time |
|---|---:|
| Initial LLM connectivity test | 0.45 seconds |
| Planner test | 2.04 seconds |
| Business analysis workflow | 0.77 seconds |
| Product margin ranking | 0.63 seconds |
| Unsupported objective | 0.34 seconds |

These measurements represent individual observed responses, not a formal benchmark. Results may vary depending on model state, hardware load, and request complexity.

---

## 🔎 Key Findings

This experiment demonstrates how an LLM can participate in a controlled workflow by selecting operations based on a natural-language objective.

The main findings are:

- Planning can be separated from execution.
- A model can select different operations for different objectives.
- Structured JSON makes the model's plan easier to validate.
- An allowlist limits execution to predefined operations.
- Python is better suited to deterministic numerical calculations.
- Shared state improves traceability across workflow steps.
- Unsupported objectives can be rejected before data processing.
- Local inference makes the entire experiment independent of external LLM APIs.

The resulting system is more flexible than a fixed sequence of operations, while retaining explicit execution controls.

---

## 🔐 Security and Reliability Considerations

The planner validates the model-generated JSON and rejects operations that are not in the predefined allowlist.

The workflow executes operations through explicit Python branches instead of evaluating arbitrary code generated by the model.

However, these controls do not guarantee that every accepted plan is semantically correct.

Further work should include:

- Testing ambiguous objectives
- Testing malformed or unexpected model responses
- Improving semantic validation of plans
- Adding retry policies where appropriate
- Testing failures at different workflow stages
- Measuring planning reliability across a larger test set

The current experiment demonstrates basic controlled execution, not a comprehensive security audit.

---

## ⚠️ Limitations

- The dataset is small and synthetic.
- The planner can select only from five predefined operations.
- The workflow executes the selected operations in sequence.
- The model does not dynamically invent or implement new tools.
- There is no persistent memory between user requests.
- The report is based on predefined Python output formatting.
- Testing covers a limited number of supported and unsupported objectives.

The current implementation is a controlled, LLM-planned workflow rather than a fully autonomous agent.

---

## 🚀 Next Step

The next stage can introduce more advanced orchestration patterns