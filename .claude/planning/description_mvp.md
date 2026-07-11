## Product Name

**GooseCompass**

---

## Problem Statement

Students at the University of Waterloo participating in overseas exchange programs face challenges such as time-consuming information gathering and fragmented information channels when obtaining the key information needed to plan and complete their exchange applications.

Relevant information is distributed across:

* Waterloo International webpages
* Partner university websites
* PDF policy documents
* Application timelines and requirement pages

This leads to:

* repetitive searching across multiple sources
* difficulty verifying correctness
* time inefficiency in application planning
* frequent reliance on staff or peer clarification

---

## Solution Overview

**GooseCompass** is a retrieval-augmented AI assistant designed specifically for University of Waterloo outbound exchange students.

It enables users to ask natural-language questions and receive:

* factual answers grounded strictly in retrieved documents
* citations linked to source material
* consolidated responses across multiple official sources

The system does not generate freeform knowledge; it only answers based on retrieved content.

---

## Target Users

### Primary (MVP)

* University of Waterloo outbound exchange applicants

### Secondary (future expansion)

* Exchange advisors
* Incoming exchange students

---

## Core Value Proposition

GooseCompass centralizes fragmented exchange documentation into a single conversational interface that:

* reduces time spent searching across multiple sites
* improves information accessibility
* provides verifiable, source-backed answers
* improves confidence in decision-making during exchange planning

---

# MVP Scope

## Supported Query Domains

All handled through a unified RAG system:

* Partner university information
* Waterloo exchange policies
* Eligibility requirements
* Deadlines and timelines
* Application procedures
* Required documents
* Visa information (informational only)
* Housing guidance
* Course selection and equivalency information

---

## System Behavior Constraints

### Answering rule

* Answers must be **fully grounded in retrieved context**
* No external/general LLM knowledge allowed
* If context is insufficient → system must say so

---

## Source Strategy

### Data ingestion

* Manually curated dataset

### Composition

* ~80% web URLs (official pages)
* ~20% PDFs (policy documents, guides)

### Update frequency assumption

* ~6 months average change cycle

---

## Citation Format

* Citations appear at the **end of each paragraph**
* Each paragraph must clearly reference supporting sources
* Similar style to Google AI Overview / grounded summarization UI

---

## UX Scope

### MVP interface

* Single-page chat application
* Freeform natural language input
* No authentication required
* No structured navigation UI

---

## Deployment Goal

* Fully deployed web application
* Accessible to real users (friends/test users)
* Stable enough for demonstration use
