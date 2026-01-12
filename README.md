🏛️ **Enterprise** **Legal** **RAG** **Assistant**

**Citation-Aware** **Queston** **Answering** **on** **Indian** **Law(IPC & CrPc)**

**Overview**

The **Enterprise Legal RAG Assistant** is a retrieval question-answering system for Indian

statutory law.

It answers legal question using the **Indian Penal Code (IPC)** and the Code of Criminal

Procedure (CrPC) by retrieving verified legal section and generating answers strictly

grounded in those sections.

The system is designed with a single guiding rule;

**The model only answers when a verified legal section is retrieved.**

**If retrieval fails, the system fails safely instead of guessing**


**Problem Statement**

Most Retrieval Agurmented Generation (RAG) systems treat retrieval as a supporting step. 

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

**3.Section-Aware Chunking**
  Instead of token0based or size-based chunking, text is split only at legal section    
  boundaries.
  Each chunk represents exactlyy one legal section.
  Example:
  - IPC section 378 - Theft(full definition)
  - IPC section 379 - Punishment for Theft
  - IPC section 380 - Theft in Dwelling
  Each chunk includes metadata:
  - Act name (IPC/CrPc)
  - Section number
  - Section title
why this matters:
Legal meaning collapses when definition are split arbitrarily.
Section-level chunks preserve legal correctness and enbale accurate citation.

**4.Embedding**
  - Each section chunk is converted into vector embeddings.
  - Embeddings are stored in a vector databases.
  - Metadata also indexed alongside vectors for filtering and citation
Enable semantic retrieval at the legal-section level.

**5.Retrieval**

User Query → Embed → Retrieve Top-K Sections

If  no relevant section is retrieved:

Return: "Section is not found in the provided legal documents."

if retrieval fails, answer generation is blocked.

**6.Answer Generation (LLM)**
  - Retrieved sections are passed as the only context
  - The LLM is instructed to answer ONLY using retrieved sections
  - External knowledge and guessing are not allowed.
Output includes:
- A grounded answer
- Explicit section citations

**7.RAG Service Layer**
All RAG logic is wrapped in dedicated service layer that:
- Accepts user queries
- Excutes retrieval
- Executes generations
- Return structured responses
Decouple core RAG logic from API and UI layers.

**8.Chat Layer(chat.py)**
  - Accepts a user's natural language legal question
  - Invoke the RAG service pipeline
  - Enforce fail-safe behaviour when retrieval returns no results
  - Return a Structured response containing:
    - answer
    - citations

 **9.FastAPI Backend**
   - Exposes the RAG service via APIs
   - Handles request validation and error handling.

**10.Streamlit UI**
  - Client that consumes the FastAPI backend
  - Users can ask questions and view answers with citations


**Project Structure**




Example :Explain IPC sections Punishment. 

Answer
{
"answer":"Based on the provided legal context, there are three sections related to "Punishment":

1. IPC Section 311: This section states that whoever is a thug shall be punished with imprisonment for life and shall also be liable to fine.

2. IPC Section 166B: This section states that whoever, being in charge of a hospital, public or private, contravenes the provisions of section 357C shall be punished with imprisonment for a term which may extend to one year or with fine or with both.

3. IPC Section 302: This section states that whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.

These sections outline the punishments for being a thug, non-treatment of a victim, and murder, respectively."

"citations":[
0:{
"law":"IPC"

"section":"311"

"section_title":"Punishment.—Whoever is a thug, shall be punished with 1[imprisonment for life], and shall also"

"source_file":"ipc_page_076_cleaned.txt"

"chunk_id":534
}

1:{
"law":"IPC"

"section":"166B"

"section_title":"Punishment for non-treatment of victim.—Whoever, being in charge of a hospital, public or"

"source_file":"ipc_page_044_cleaned.txt"

"chunk_id":407
}

2:{
"law":"IPC"

"section":"302"

"section_title":"Punishment for murder .—Whoever commits murder shall be punished with death, or"

"source_file":"ipc_page_074_cleaned.txt"

"chunk_id":525
}

3:{
"law":"IPC"

"section":"358"

"section_title":"Assault or criminal force on grave provocation .—Whoever assaults or uses criminal force to"

"source_file":"ipc_page_086_cleaned.txt"

"chunk_id":577
}

4:{
"law":"IPC"

"section":"323"

"section_title":"Punishment for voluntarily causing hurt .—Whoever, except in the case provided for by"

"source_file":"ipc_page_078_cleaned.txt"

"chunk_id":545
}
]
}


  









