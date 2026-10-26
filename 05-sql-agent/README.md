# 05 — SQL Agent

## 🎯 Objective

The objective of this experiment is to understand how a Large Language Model can interact with a structured database by translating natural-language questions into SQL queries.

The experiment focuses on:

- Connecting a local LLM to a relational database
- Providing the model with the database schema
- Translating natural-language questions into SQL
- Executing generated queries through a controlled Python application
- Testing joins, aggregations, filtering, and sorting
- Preventing unauthorized database modifications
- Observing the impact of extended thinking on generation latency

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
| Database | SQLite |
| Data | Synthetic sales dataset |

---

## 🏗️ Architecture

The experiment introduces an architecture in which an LLM generates SQL queries to retrieve information from a relational database.

The model does not directly access the database.

Instead, the Python application provides the database schema, receives the generated SQL, and passes it to a controlled query executor.

The architecture is composed of four main components:

```text
User
 ↓
LLM — Qwen3 8B
 ↓
SQL Generation
 ↓
Python Application
 ↓
Read-Only Query Executor
 ↓
SQLite Database
 ↓
Query Results
```

### Components

#### LLM

Qwen3 8B runs locally through Ollama.

Its role is to:

- Understand the user's question
- Interpret the database schema
- Generate an appropriate SQL query
- Use joins and aggregations when necessary

The model generates the query but does not execute it directly.

---

#### Python Application

The Python application orchestrates the interaction between the LLM and the database.

It:

- Sends requests to Ollama
- Provides the database schema to the model
- Receives the generated SQL
- Passes the query to the database module
- Displays the results
- Handles errors without necessarily terminating the interactive session

---

#### Database

The experiment uses SQLite and a synthetic sales dataset.

Four tables were created:

```text
customers
products
orders
order_items
```

The tables are connected through primary and foreign keys.

The dataset contains:

- 5 customers
- 5 products
- 8 orders
- 13 order items

The database is generated locally and is excluded from Git.

---

#### Read-Only Query Executor

The database module executes permitted queries and returns the results to the Python application.

The executor uses SQLite read-only mode and an authorization callback to block selected database-changing operations.

This follows the same principle introduced in previous experiments: the model can request a capability, but the application controls how it is executed.

---

## 🔧 Implementation

### Database Setup

The database is created using:

```text
05-sql-agent/src/setup_db.py
```

Run the script from the repository root:

```bash
python3 05-sql-agent/src/setup_db.py
```

The script creates the tables and populates them with synthetic sales data.

**Note:** running the script again resets the existing sample tables.

---

### SQL Generation

The SQL generation logic is implemented in:

```text
05-sql-agent/src/sql_agent.py
```

The model receives the user's question and the database schema.

It generates a SQLite query using the available tables and columns.

For example, the question:

> Which three products have the highest prices?

produces:

```sql
SELECT name, price
FROM products
ORDER BY price DESC
LIMIT 3;
```

The generated query is then passed to the database module.

---

### Database Execution

The database access logic is implemented in:

```text
05-sql-agent/src/database.py
```

The module provides functions to:

- Open a database connection
- Retrieve the database schema
- Execute a query in read-only mode

The executor applies several checks before returning query results.

The database remains separate from the LLM, allowing the application to control which operations can be executed.

---

### Interactive Interface

The interactive interface is implemented in:

```text
05-sql-agent/src/main.py
```

Run the application with:

```bash
python3 05-sql-agent/src/main.py
```

The user can enter questions directly into the terminal.

For example:

```text
List all products and their prices.
How many orders are pending?
What is the total value of completed orders for each customer?
```

The application displays the generated SQL and the returned results.

Typing `exit` terminates the session.

---

## 🧪 Experiment 01 — Product Lookup

### Prompt

> Which three products have the highest prices?

### Observation

The model generated a query that selected products, sorted them by price in descending order, and returned the first three results.

### Result

The database returned:

| Product | Price |
|---|---:|
| Laptop | 1200.00 |
| Smartphone | 800.00 |
| Monitor | 300.00 |

The model successfully translated a simple natural-language question into an executable SQL query.

---

## 🧪 Experiment 02 — Order Filtering

### Prompt

> How many orders are pending?

### Observation

The model generated a query using `COUNT(*)` and filtered orders by the `pending` status.

### Result

The query returned:

```text
1
```

The model successfully generated a query involving filtering and aggregation.

---

## 🧪 Experiment 03 — Customer Revenue Analysis

### Prompt

> What is the total value of completed orders for each customer, ordered from highest to lowest?

### Observation

The model generated a query involving:

- Multiple `JOIN` operations
- A `WHERE` condition
- The `SUM()` aggregation function
- `GROUP BY`
- `ORDER BY`

The query calculated each customer's total value from completed order items.

### Result

The database returned:

| Customer | Completed order value |
|---|---:|
| Marco Bianchi | 2560.00 |
| Alice Rossi | 2250.00 |
| James Smith | 1800.00 |
| Sofia Garcia | 390.00 |

The model successfully generated and executed a query involving three related tables and an aggregate calculation.

---

## 🧪 Experiment 04 — Preventing Database Modifications

### Test

The executor was directly given a `DELETE` statement:

```sql
DELETE FROM customers;
```

### Observation

The query was rejected because the executor only accepts statements beginning with `SELECT` or `WITH`.

A second test attempted to perform a deletion through a common table expression:

```sql
WITH x AS (SELECT 1) DELETE FROM customers;
```

SQLite rejected the statement with:

```text
DatabaseError: not authorized
```

A subsequent count query confirmed that all five customers remained in the database.

### Result

The tested write operations were blocked.

This demonstrates the importance of enforcing permissions at the database layer rather than relying exclusively on instructions given to the LLM.

---

## 🧪 Experiment 05 — Reducing Generation Latency

### Observation

The initial complex SQL-generation test took approximately 65.12 seconds.

The model was using extended thinking, which introduced significant latency for a task that primarily required generating a structured SQL query.

The Ollama chat request was modified to disable thinking using:

```python
"think": False
```

The same complex query was then generated in approximately 3.46 seconds.

### Result

| Configuration | Generation time |
|---|---:|
| Thinking enabled | 65.12 seconds |
| Thinking disabled | 3.46 seconds |

The observed reduction in generation time was approximately 94.7%.

A subsequent end-to-end test completed SQL generation in 3.44 seconds and returned the expected customer totals.

This demonstrates that extended reasoning is not always necessary for structured generation tasks.

---

## 🔎 Key Findings

A SQL Agent allows an LLM to interact with structured data through a controlled application.

The model can:

- Translate natural-language questions into SQL
- Use a database schema to identify tables and columns
- Generate queries involving joins and aggregations
- Retrieve information from a relational database
- Support basic analytical questions

However, the model does not automatically guarantee:

- Correct SQL for every question
- Semantically correct results
- Low latency for every request
- Protection against every possible malicious query

The application must retain control over database access and query execution.

### Core Principle

> An LLM can generate a query, but the application must control what is executed and which data can be accessed.

---

## 🔐 Security Consideration

The experiment uses a synthetic dataset and a read-only query executor.

The implementation includes:

- SQLite read-only connection mode
- `PRAGMA query_only`
- A SQLite authorization callback
- Basic checks on the generated SQL
- Error handling in the interactive interface

The tested write operations were rejected, and the database contents remained intact.

These protections are a first layer of defense, not a complete SQL security system. Additional validation and adversarial testing would be required before using the approach with sensitive or production databases.

---

## ⚠️ Limitations

The experiment has several limitations:

- The dataset is small and synthetic.
- Only a limited number of questions have been tested.
- The model can generate incorrect filters, joins, or aggregations.
- A valid SQL query does not necessarily produce the intended answer.
- Complex requests may require substantially more generation time.
- The current interface displays raw query results rather than a natural-language explanation.
- The database authorization rules require further security testing.

The observed latency improvement is based on local tests and is not a comprehensive performance benchmark.

---

## 🚀 Next Step

The next experiments can build on the capabilities developed so far.

Potential directions include combining structured database queries with document retrieval, improving the reliability of tool execution, and allowing the model to explain query results in natural language.

The overall progression is from:

```text
LLM
 ↓
Natural-Language Question
 ↓
SQL Query
 ↓
Controlled Database
 ↓
Structured Results
```

toward more capable AI systems that can select and use external tools to solve tasks.
