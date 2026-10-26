# 🧠 Experiment 04 — Retrieval-Augmented Generation (RAG)

## 🎯 Objective

In this experiment, I explored Retrieval-Augmented Generation (RAG) and how an LLM can use external information to answer questions.

My goal was to build a working RAG pipeline locally, understand its main components, and test how it behaves when the knowledge base contains—or does not contain—the information required to answer a question.

I focused on understanding the complete workflow rather than spending too much time optimising a single component.

## 🏗️ Architecture

My RAG pipeline consists of four main steps:

1. **User query:** I submit a question in natural language.
2. **Retrieval:** I generate an embedding for the query and compare it with the document embeddings using cosine similarity.
3. **Context construction:** I select the most relevant documents and pass them to the language model.
4. **Generation:** The LLM generates an answer using the retrieved context.

### 🧰 Technologies

- **Ollama** — local model execution.
- **Qwen3:8B** — answer generation.
- **nomic-embed-text** — text embeddings.
- **Python** — retrieval and generation logic.
- **JSON** — knowledge base and embedding cache.
- **Cosine similarity** — semantic document ranking.

## 📁 Project Structure

```text
04-rag/
├── data/
│   ├── historical_events.json
│   └── embeddings_cache.json
└── src/
    ├── retrieve.py
    └── rag.py
```

- `historical_events.json`: my knowledge base, containing six historical-event documents dated between July 2024 and May 2025, with source URLs.
- `embeddings_cache.json`: stores document embeddings to avoid recomputing them on every execution.
- `retrieve.py`: implements document retrieval and similarity ranking.
- `rag.py`: connects retrieval to answer generation.

## 🔎 Retrieval Implementation

I use Ollama's `/api/embed` endpoint with `nomic-embed-text` to generate vector representations of documents and user queries.

I calculate cosine similarity, rank the documents, and return the top three results, with a configured minimum similarity score of `0.30`.

The retrieval function returns each result as a `(score, document)` pair.

### ⚡ Persistent Embedding Cache

I implemented a persistent cache to avoid regenerating document embeddings every time I run the experiment.

The cache fingerprint depends on the embedding model and document data. When the inputs remain unchanged, I reuse the existing embeddings. When they change, the cache is regenerated.

This reduces repeated computation, although it does not directly improve retrieval accuracy.

## 🤖 Generation

After retrieving the most relevant documents, I send the question and retrieved context to Qwen3:8B through Ollama's `/api/chat` endpoint.

I configured the system prompt to instruct the model to:

- Answer using the retrieved documents.
- Avoid inventing facts or sources.
- Acknowledge when the available information is insufficient.

These instructions guide the model's behaviour but do not guarantee that every answer will be correct.

## 🧪 Experiments and Results

### Test 1 — Semantic Retrieval

**Question:** `Quali cambiamenti economici ha vissuto il Messico?`

The retriever returned the following top results:

| Retrieved document | Similarity |
|---|---:|
| Mexican president | 0.655 |
| US election | 0.634 |
| Friedrich Merz | 0.581 |

This confirmed that the retrieval pipeline ranked documents by semantic similarity. It also revealed that a document can receive a relatively high score without directly answering the question.

### Test 2 — Question Outside the Knowledge Base

**Question:** `Qual è la popolazione di Città del Messico nel 2026?`

The system retrieved three documents, but they did not provide the requested population figure.

Qwen3:8B acknowledged that the available information was insufficient instead of inventing a number.

**Result:** The system behaved as expected in this test.

### Test 3 — Supported Question: Mexico

**Question:** `Chi è diventata presidente del Messico il 1 ottobre 2024?`

The relevant document ranked first with a similarity score of `0.825`.

The model correctly answered **Claudia Sheinbaum** and provided a source.

**Result:** Correct answer in this test.

### Test 4 — Supported Question: Pope Leo XIV

**Question:** `Quando è stato eletto papa Leone XIV?`

The relevant document ranked first with a similarity score of `0.857`.

The model correctly answered **8 May 2025** and provided a source.

**Result:** Correct answer in this test.

### 📊 Test Summary

| Test | Outcome |
|---|---|
| Semantic retrieval | Ranking worked, but relevance was imperfect |
| Unsupported question | The model acknowledged insufficient information |
| Mexican president | Correct answer with a source |
| Pope Leo XIV | Correct answer with a source |
| Embedding cache | Reused embeddings on subsequent executions |

These are qualitative results from a small number of manually selected questions, not a comprehensive evaluation of accuracy or reliability.

## ⚠️ Limitations

During the experiment, I identified several limitations:

1. **Retrieval relevance:** Some documents received relatively high similarity scores despite being only loosely related to the question.
2. **Small knowledge base:** The dataset contains only six documents.
3. **Similarity is not correctness:** A high score does not prove that a document contains the answer.
4. **Prompt-based grounding:** Instructions to avoid unsupported claims do not eliminate hallucinations in every situation.
5. **Limited evaluation:** I tested a