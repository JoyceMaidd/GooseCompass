# GooseCompass — Technical Architecture

## Overview

GooseCompass is a domain-specific Retrieval-Augmented Generation (RAG) system designed for University of Waterloo outbound exchange students.

The system provides grounded, citation-backed responses by retrieving relevant information from curated institutional sources and synthesizing responses strictly from retrieved context.

---

# System Design Principles

## 1. Strict Grounding

All generated responses must be derived exclusively from retrieved context.

If sufficient context is unavailable, GooseCompass must explicitly state that it cannot answer based on indexed sources.

No external model knowledge is permitted in MVP generation.

---

## 2. Hybrid Retrieval

The retrieval system combines:

* Semantic vector similarity search
* Keyword search

Results are fused using Reciprocal Rank Fusion (RRF).

This improves recall and precision for institutional documentation where exact terminology is often critical.

---

## 3. Retrieval-First Development

The project prioritizes retrieval correctness before UI development.

Development order:

1. CLI validation environment
2. Backend API layer
3. Streaming frontend interface

This ensures retrieval quality is validated before interface polish.

---

# High-Level Architecture

```text
React Frontend
     ↓
FastAPI Backend
     ↓
Query Processor
     ↓
Parallel Retrieval
  ├── MongoDB Vector Search
  ├── MongoDB Atlas Full-Text Search
     ↓
Reciprocal Rank Fusion
     ↓
Context Selector
     ↓
PydanticAI Response Generator
     ↓
Structured Grounded Response + Citations
```

---

# Technology Stack

## Frontend

### React + TypeScript

Purpose:

* Chat interface
* Token streaming response rendering
* Citation display

Implementation timing:
Later development phase after backend validation.

---

## Backend

### FastAPI

Responsibilities:

* Request handling
* Retrieval orchestration
* Query rewriting
* Prompt construction
* Streaming response delivery

Reasoning:

* Strong Python ecosystem integration
* Async support
* Clean API design
* Excellent compatibility with AI tooling

---

## Database

### MongoDB Atlas

MongoDB Atlas is the unified storage layer.

Responsibilities:

### Vector Search

Semantic similarity retrieval

### Atlas Search

Text search with keyword/fuzzy matching

### Metadata Storage

Stores:

* Documents
* Chunks
* Source metadata
* Ingestion state

Reasoning:

* Native hybrid retrieval support
* Operational simplicity
* Single-system architecture
* Strong production relevance

---

## Document Processing

### Docling

Docling is used for:

* Hybrid chunking
* Structured extraction

Reasoning:

Provides consistent document normalization across heterogeneous source types.

---

## Embeddings

### OpenAI text-embedding-3-small

Used for:

* Query embeddings
* Chunk embeddings

Reasoning:

* Strong quality/cost balance
* Reliable production performance

---

## LLM Access

### OpenRouter

Purpose:

* Flexible model experimentation
* Provider abstraction
* Cost optimization

Model selection will be stabilized after evaluation.

---

## Response Orchestration

### PydanticAI

PydanticAI is used narrowly for:

* Structured answer generation
* Response schema validation
* Citation formatting

PydanticAI does **not** control retrieval.

Retrieval remains deterministic backend logic.

Reasoning:

This preserves architectural transparency while enabling structured response guarantees.

---

# Retrieval Pipeline

## Step 1: Query Intake

User submits natural language query.

---

## Step 2: Lightweight Query Rewriting

The query is rewritten to improve retrieval precision.

Example:

Original:

> Can I go to ETH if my grades are average?

Rewritten:

> ETH Zurich exchange eligibility GPA requirements University of Waterloo

Purpose:

Improve retrieval recall across institutional documentation.

---

## Step 3: Parallel Retrieval

### Semantic Retrieval

MongoDB vector similarity search

Candidate count: 20

---

### Lexical Retrieval

MongoDB Atlas full-text search

Candidate count: 20

---

## Step 4: Reciprocal Rank Fusion (RRF)

Semantic and lexical results are merged via RRF.

Purpose:

* Preserve exact-match institutional terminology
* Preserve semantic relevance
* Improve hybrid retrieval robustness

---

## Step 5: Context Selection

Default final context:

* Top 10 fused chunks

Configurable via function parameter.

---

## Step 6: Prompt Construction

Prompt includes:

* Strict grounding instructions
* Retrieved context
* User query

The model is explicitly prohibited from using external knowledge.

---

## Step 7: Structured Response Generation

PydanticAI produces:

* Paragraph-based answer
* End-of-paragraph citations
* Grounded response schema validation

---

# Chunking Strategy

Docling Hybrid Chunking

GooseCompass uses Docling's built-in hybrid chunking through direct function calls.

This delegates chunk boundary optimization to Docling's document-aware chunking pipeline.

## Reasoning:

Preserves document structure automatically

Reduces manual chunk tuning complexity

Provides strong default performance across institutional documents

Maintains consistency across heterogeneous source formats

Chunk sizing and overlap are therefore managed internally by Docling rather than manually configured.

---

# Source Ingestion Architecture

## Unified Document Ingestion Pipeline

Docling serves as the unified ingestion layer for all supported source types.

Pipeline:

```text
Source Input
→ Fetch / Load Document
→ Docling Processing
→ Structured Extraction
→ Hybrid Chunking
→ Embedding
→ MongoDB Storage
```

Supported source types are handled transparently by Docling through a consistent processing interface.

---

## Metadata Stored Per Chunk

Each chunk stores:

* Content
* Source URL
* Document title
* Section title
* Document type
* Chunk index

This enables precise citation rendering.

---

# Session Management

## MVP Decision

Session-only conversation state.

No persistent chat history storage.

Reasoning:

Reduces infrastructure complexity while preserving sufficient conversational continuity for testing.

---

# Response Streaming

## Final Product

Token-by-token streaming response delivery.

---

## Development Priority

Deferred until retrieval pipeline validation is complete.

Initial testing occurs through CLI interaction.