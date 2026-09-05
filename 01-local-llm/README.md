# 01 — Local LLM

## 🎯 Objective

The objective of this experiment is to understand how a Large Language Model behaves when running locally, without relying on a cloud-based AI API.

The experiment focuses on:

- Running an open-source LLM locally
- Interacting with the model through Ollama
- Testing multilingual capabilities
- Understanding the limitations of a standalone LLM
- Observing how the model handles information it cannot directly verify

---

## 🛠️ Environment

| Component | Configuration |
|---|---|
| Hardware | MacBook Air M4 (2025) |
| Memory | 16 GB unified memory |
| Runtime | Ollama |
| Model | Qwen3 8B |
| Inference | Local |
| Language tested | Italian |

---

## 🧪 Experiment 01 — Basic Interaction

### Prompt

> Explain who you are and where you are running.

### Observation

The model correctly identified itself as Qwen, but incorrectly stated that it was running on Alibaba's cloud infrastructure.

In reality, the model was running locally through Ollama on the user's Mac.

### Result

This demonstrates that an LLM does not necessarily have reliable knowledge about its own execution environment.

---

## 🧪 Experiment 02 — Access to System Information

### Prompt

> What information can you directly know about the computer you are currently running on? List the information you can actually know and the information you cannot know.

### Observation

The model correctly stated that it could not directly access the local computer, its files, hardware, or operating system.

However, it continued to incorrectly describe itself as a cloud-based model running on Alibaba's infrastructure.

### Result

An LLM can produce a plausible explanation about its environment without actually having access to verify that environment.

---

## 🧪 Experiment 03 — Preventing Assumptions

### Prompt

> Think through the following task: tell me how much RAM the computer you are currently running on has and which processor it uses. Do not make assumptions. If you cannot verify the information directly, state that you cannot.

### Observation

The model refused to provide specific hardware information and correctly stated that it could not verify the RAM or processor.

### Result

Explicit instructions can reduce unsupported claims, but the model still lacks direct access to external information.

---

## 🔎 Key Findings

A standalone LLM can:

- Understand natural language
- Generate coherent responses
- Follow instructions
- Reason about information contained in its context

However, it cannot automatically:

- Inspect the computer on which it is running
- Access external data
- Query databases
- Read arbitrary files
- Verify real-world information

unless an external mechanism provides that capability.

### Core Principle

> An LLM generates responses based on the information available to it. It does not automatically have access to the environment in which it is running.

---

## 🔐 Security Consideration

The next experiments will **not provide the AI with unrestricted access to the user's computer**.

Tools will operate inside controlled environments using synthetic datasets and explicitly defined permissions.

This follows a least-privilege approach: an AI system should only have access to the resources required for its task.

---

## 🚀 Next Step

The next experiment will introduce **Tool Calling**.

Instead of giving the model access to the user's computer, we will create a controlled business dataset and expose a small number of explicitly defined functions to the model.

The goal will be to move from:

```text
LLM → Response

to:

LLM
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