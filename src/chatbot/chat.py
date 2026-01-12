import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.documents import Document

from src.retrieval.retriever import hybrid_retrieve


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ------------------ LLM 

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    groq_api_key=GROQ_API_KEY,
    temperature=0.0   
)

# ------------------ SYSTEM PROMPT ------------------

SYSTEM_PROMPT = """
You are a legal information retrieval assistant.

STRICT RULES (NO EXCEPTIONS):
1. Use ONLY the legal text provided in the Context.
2. Do NOT use outside knowledge or assumptions.
3. Mention ONLY sections explicitly present in the context.
4. If the answer is not found, reply exactly:
   "Answer not found in the provided legal documents."
   If a specific section number is mentioned in the question, explain ONLY that section and ignore all others.

"""

# ------------------ HELPER: FILTER RELEVANT DOCS 

def filter_relevant_docs(query: str, docs: list[Document]) -> list[Document]:
    query_lower = query.lower()
    filtered = []

    for doc in docs:
        section = doc.metadata.get("section")
        title = (doc.metadata.get("section_title") or "").lower()

        if section and section.lower() in query_lower:
            filtered.append(doc)
            continue

        if any(word in title for word in query_lower.split()):
            filtered.append(doc)

    return filtered if filtered else docs[:1]

# ------------------ MAIN ASK FUNCTION ------------------

def ask(query: str, top_k: int = 5) -> dict:
    retrieved_docs = hybrid_retrieve(query, top_k=top_k)
    retrieved_docs = filter_relevant_docs(query, retrieved_docs)

    if not retrieved_docs:
        return {
            "answer": "Answer not found in the provided legal documents.",
            "citations": []
        }

    context_blocks = []
    citations = []
    seen_sections = set()

    for doc in retrieved_docs[:2]:  # 🔒 limit context
        citation = {
            "law": doc.metadata.get("law"),
            "section": doc.metadata.get("section"),
            "section_title": doc.metadata.get("section_title"),
            "source_file": doc.metadata.get("source_file"),
            "chunk_id": doc.metadata.get("chunk_id"),
        }

        key = (citation["law"], citation["section"])
        if citation["section"] and key not in seen_sections:
            citations.append(citation)
            seen_sections.add(key)

        context_blocks.append(
            f"[Law: {citation['law']}, Section: {citation['section']}]\n"
            f"{doc.page_content}"
        )

    context = "\n\n---\n\n".join(context_blocks)

    prompt = f"""
{SYSTEM_PROMPT}

WRITING STYLE:
- Use clear legal language.
- Highlight section numbers in bold.
- Follow this structure ONLY if information exists:
  1. Applicable Section
  2. What the Section Covers
  3. How it applies to the question

LEGAL CONTEXT:
{context}

USER QUESTION:
{query}

ANSWER:
"""

    response = llm.invoke(prompt)
    answer_text = response.content.strip()
    filtered_citations = [
        c for c in citations
        if c.get("section") and f"Section{c['section']}" in answer_text
    ]

    return {
        "answer": response.content.strip(),
        "citations": filtered_citations
    }

# ------------------ TEST ------------------

if __name__ == "__main__":
    result = ask("Explain Putting person in fear of injury in order to commit extortion. ", top_k=5)

    print("\nANSWER:\n", result["answer"])
    print("\nCITATIONS:")
    for c in result["citations"]:
        print(c)

