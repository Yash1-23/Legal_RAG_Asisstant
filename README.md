🏛️ **Enterprise** **Legal** **RAG** **Assistant**

**Citation-Aware** **Queston** **Answering** **on** **Indian** **Law(IPC & CrPc)**

**Overview**

The **Enterprise Legal RAG Assistant** is a retrieval question-answering system for Indian

statutory law.

It answers legal question using the **Indian Penal Code (IPC)** and the **Code of Criminal

Procedure (CrPC)** byt retrieving verified legal section and generating answers strictly

grounded in those sections.

The system is desgined with a single guiding rule;

**The model only answers when a verified legal section is retrieved.**

**If retrieval fails, the system fails safely instead of guessing**


**Problem Statement**

Most Retrieval_Agurmented Generation (RAG) systems treat retrieval as a supporting step. 

In legal applications, retrieval is the answer:

Common issues in legal RAG systems:

- Arbitrary chunking breaks legal definitions

- Answers are generated without citations.

- Models hallucinate sections when retrieval is weak or empty.

This project address those failures by enforcing **section-level retrieval** , **strict 
grounding, and explicit citations**.

**System Architecture (End-to-End Flow)**
The system follows a strict sequential pipeline.

**Load -> Clean -> Chunk -> Embedding -> Retrieve -> Generate -> API -> UI**

**Pipeline Breakdown**
**1. Document Loading**
  - IPC and CrPC Pdf are loaded fromthe data/ directory
  - PDFs are parsed into a raw text
  - Section headers are preserved
  - Page numbers, footers, and formatting are removed
Convert PDFs into strcutred legal text.

**2. Text Cleaning**
  - Normalize whitespace and line breaks
  - Preserve section numbers and titles
  - Ensure consistent formatting across documents
Preprare text for reliable section based chunking.





