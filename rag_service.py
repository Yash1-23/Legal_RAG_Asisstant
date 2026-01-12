import re
from typing import Dict, Any, List

from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

from src.retrieval.retriever import hybrid_retrieve

load_dotenv()

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.0
)

SYSTEM_PROMPT = """
You are a legal information retrieval assistant.

STRICT RULES:
1. Use ONLY the legal text provided.
2. Do NOT use outside knowledge.
3. Mention ONLY sections present in context.
4. If not found, say:
   "Answer not found in the provided legal documents."
"""

def extract_section_from_query(query: str):
    import re
    match = re.search(r"section\s*(\d+[A-Z]*)", query.lower())
    return match.group(1).upper() if match else None


def clean_text(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def detect_section_law_mismatch(query: str, docs: list) -> str | None:
    """
    Detect if user asked for a section under the wrong law.
    Example: 'CrPC Section 474' → actually exists in IPC.
    """
    q = query.lower()

    asked_ipc = "ipc" in q
    asked_crpc = "crpc" in q

    available_laws = {d.metadata.get("law") for d in docs}

    if asked_crpc and "IPC" in available_laws and "CRPC" not in available_laws:
        return "IPC"

    if asked_ipc and "CRPC" in available_laws and "IPC" not in available_laws:
        return "CRPC"

    return None

def generate_answer(query: str, top_k:int = 5) -> Dict[str, Any]:
    docs = hybrid_retrieve(query, top_k=top_k)
    
    #detect IPC/ CRPC
    law_hint = detect_section_law_mismatch(query,docs)
    
    if law_hint:
        return {
            "answer":(
                  f"The requested section does not exist under the specified law. "
            f"However, this section exists under the {law_hint}. "
            f"Please confirm if you want the explanation under {law_hint}."
            ),
            "citations": []
        }
    if not docs:
        return {
            "answer": "Answer not found in the provided legal documents.",
            "citations": []
        }

    # Section-aware filtering
    section_asked = extract_section_from_query(query)
    docs = hybrid_retrieve(query, top_k=5)
    if section_asked:
        filtered = [
            d for d in docs
            if d.metadata.get("section") == section_asked
        ]
        if filtered:
            docs = filtered
        else:
            return {
                "answer": f"Section {section_asked} is not found in the provided legal documents.",
                "citations": []
            }

    # Build context
    context_blocks = []
    citations = []

    for doc in docs:
        citations.append({
            "law": doc.metadata.get("law"),
            "section": doc.metadata.get("section"),
            "section_title": doc.metadata.get("section_title"),
            "source_file": doc.metadata.get("source_file"),
            "chunk_id": doc.metadata.get("chunk_id")
        })

        context_blocks.append(
            f"[{doc.metadata.get('law')} Section {doc.metadata.get('section')}]\n"
            f"{doc.page_content}"
        )

    context = "\n\n---\n\n".join(context_blocks)

    prompt = f"""
{SYSTEM_PROMPT}

LEGAL CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""

    response = llm.invoke(prompt)

    return {
        "answer": clean_text(response.content),
        "citations": citations
    }


  
  
  
 