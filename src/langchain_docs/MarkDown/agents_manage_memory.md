# Question

How does AI agents manage memory?

# Response

AI agents manage memory through layered architectures that borrow heavily from both computer science and cognitive science. Here's a breakdown based on current research and industry practice:

## 1. The Core Taxonomy: Four Types of Memory

The field has largely formalized around the **CoALA framework** (Cognitive Architectures for Language Agents, Princeton, arXiv:2309.02427), which maps four memory types from cognitive science onto LLM agents:

| Type | What it stores | Analogy |
|---|---|---|
| **In-context (working) memory** | The live context window — the agent's "scratchpad" during a task | RAM |
| **Episodic memory** | Past events and interactions (specific conversation history, past task outcomes) | Autobiographical memory |
| **Semantic memory** | Factual knowledge — both world knowledge (largely from LLM pre-training) and learned facts about users/domains | Knowledge base |
| **Procedural memory** | Behavioural rules — system prompts, learned skills, how-to knowledge | Muscle memory |

## 2. Short-Term vs. Long-Term Architecture

Practically, implementations split along these lines:

**Short-term memory** lives in the context window. It's fast but limited — it resets when a session ends. Because context windows are finite, agents use strategies like:
- **Summarization/compression** of older conversation turns
- **Sliding windows** that keep recent messages and drop or archive older ones
- **Scratchpads** for intermediate reasoning state

**Long-term memory** persists across sessions, surviving restarts. The typical architecture includes:
- **Extraction pipelines** that identify what information from a conversation is worth saving
- **Consolidation processes** that refine and deduplicate stored data
- **Intelligent retrieval** — usually via **vector databases** performing semantic similarity search (finding content with similar meaning even when phrased differently), sometimes combined with **knowledge graphs** for structured, entity-based retrieval

## 3. Retrieval-Augmented Generation (RAG)

Retrieval is the mechanism that bridges long-term storage and the context window. Relevant memories are fetched (via embedding similarity or graph queries) and injected into the prompt before the LLM generates a response. The trade-off between vector search and knowledge-graph retrieval is a key design decision in memory system selection.

## 4. Two Competing Philosophies: Passive vs. Self-Editing Memory

Real-world systems illustrate a major architectural fork:

- **Mem0** (passive/memory-layer approach): An add-on SDK that works with any framework (LangChain, CrewAI, AutoGen, etc.). Its extraction pipeline *decides for you* what facts to store when you call `add()`. This is predictable and keeps memory operations out of the agent's inference budget.
- **Letta / MemGPT** (self-editing / OS-inspired approach): Based on the MemGPT paper's idea of *treating the LLM context window like virtual memory* (paging information in and out like an operating system). The **agent itself decides** what's worth remembering by calling memory functions during its reasoning loop, writing to a tiered hierarchy (core → recall → archival memory) and searching its own memory tiers when it needs context.

## 5. Active Research Frontiers

According to a December 2025 survey ("Memory in the Age of AI Agents," arXiv:2512.13564), the field is still fragmenting and evolving. Active areas include:
- **Consolidation pathways** — how episodic memories get distilled into semantic knowledge over time
- **In-weights implicit knowledge** — moving memory into model parameters themselves (e.g., via fine-tuning) rather than external storage
- **Multi-agent memory governance** — how shared memories are managed across agent teams
- **Enterprise/governed context memory** — some argue enterprise agents need additional memory types beyond the standard four, e.g., certified business definitions and lineage surfaced at inference time

**In short:** AI agents manage memory by combining a limited working context window with persistent external stores (vector databases, knowledge graphs), using extraction pipelines or agent self-editing to decide what to save, and retrieval mechanisms (RAG) to pull relevant memories back in when needed — with the field actively experimenting on consolidation, in-weights memory, and multi-agent sharing.
