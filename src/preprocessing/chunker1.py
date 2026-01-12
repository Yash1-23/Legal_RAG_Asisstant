import os
import re
import json
from typing import Dict,Any,List


CLEANED_DIR = os.path.join("data","cleaned_text")
OUTPUT_CHUNKS_DIR = os.path.join("data","chunks_v2")

MAX_CHARS = 800

#Section pattern 
#SECTION_PATTERN = re.compile(  )

STRUCTURAL_KEYWORDS =[
   "ARRANGEMENT OF SECTIONS",
    "TABLE OF CONTENTS",
    "CHAPTER",
    "SECTIONS 1.",
]

def detect_law(file_name:str) ->str |None:
  name = file_name.lower()
  if name.startswith("ipc_"):
      return "IPC"
  if name.startswith("crpc_"):
      return "CRPC"
  return None

def is_structural_page(text:str) ->bool:
  upper = text.upper()
  return any(k in upper for k in STRUCTURAL_KEYWORDS)

def is_section_index_page(text:str) ->bool:
  "Detect pages that only list section titles (indexpages) without actual section body content"
  lines = [l.strip() for l in text.splitlines() if l.strip()]
  
  section_lines =[
    l for l in lines
    if re.match(r"\d+[A-Z]?(?:\(\d+\))?\.\s+[A-Za-z]", l)
  ]
  return len(section_lines) >=5 and len(text) <2500
#Extract sections 
def  extract_sections(text:str, law:str) ->List[Dict]:
    sections = []
    
    #Normalize spacing 
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    # Remove amendment footnotes like:
    # "1. Subs. by Act 25 of 2005..."
    text = re.sub(
        r"^\s*\d+\.\s+(Subs\.|Ins\.|Amended|Omitted|Added).*?$",
        "",
        text,
        flags=re.MULTILINE | re.IGNORECASE
    )
     # LEGAL DELIMITER REGEX (IPC + CRPC safe)
    pattern = re.compile(
        r"^\s*(\d+[A-Z]*(?:\(\d+\))?)\.\s*(.*?)\n"   # section header line
        r"(.*?)(?=^\s*\d+[A-Z]*(?:\(\d+\))?\.|\Z)",  # stop at NEXT section
        re.MULTILINE |re.DOTALL
    )
    matches = list(pattern.finditer(text))

    for m in matches:
        section_no = m.group(1).strip()
        title = m.group(2).strip()
        body = m.group(3).strip()

        # Filter broken fragments
        if len(body) < 40:
            continue
        if law == "IPC" and section_no == "420":
            print("IPC 420 Extracted")
        sections.append({
            "section": section_no,
            "section_title": title if title else f"Section {section_no}",
            "text": f"{law} Section {section_no}. {title}: {body}".strip()
        })
    
    return sections


def chunk_section(section: Dict, law: str, source_file: str) -> List[Dict]:
    text = section["text"]
    chunks = []

    if len(text) <= MAX_CHARS:
        chunks.append({
            "law": law,
            "section": section["section"],
            "section_title": section["section_title"],
            "text": text,
            "source_file": source_file
        })
        return chunks

    paragraphs = re.split(r"\n\s*\n", text)
    current = ""

    for para in paragraphs:
        if len(current) + len(para) > MAX_CHARS:
            if current.strip():
                chunks.append({
                    "law": law,
                    "section": section["section"],
                    "section_title": section["section_title"],
                    "text": current.strip(),
                    "source_file": source_file
                })
                current = ""
        current += para + "\n\n"

    if current.strip():
        chunks.append({
            "law": law,
            "section": section["section"],
            "section_title": section["section_title"],
            "text": current.strip(),
            "source_file": source_file
        })

    return chunks


# ================= MAIN =================

def run_chunking():
    os.makedirs(OUTPUT_CHUNKS_DIR, exist_ok=True)
    ipc_chunks, crpc_chunks = [], []
    chunk_id = 0

    for file in sorted(os.listdir(CLEANED_DIR)):
        if not file.endswith(".txt"):
            continue

        law = detect_law(file)
        if law is None:
            continue

        path = os.path.join(CLEANED_DIR, file)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        # Skip TOC / index pages
        if is_structural_page(text) or is_section_index_page(text):
            continue

        sections = extract_sections(text,law)

        for sec in sections:
            sec_chunks = chunk_section(sec, law, file)
            for ch in sec_chunks:
                ch["chunk_id"] = chunk_id
                chunk_id += 1

                if law == "IPC":
                    ipc_chunks.append(ch)
                else:
                    crpc_chunks.append(ch)

    # Write output
    os.makedirs(os.path.join(OUTPUT_CHUNKS_DIR, "ipc"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_CHUNKS_DIR, "crpc"), exist_ok=True)

    with open(os.path.join(OUTPUT_CHUNKS_DIR, "ipc", "ipc_chunks.json"), "w", encoding="utf-8") as f:
        json.dump(ipc_chunks, f, indent=2, ensure_ascii=False)

    with open(os.path.join(OUTPUT_CHUNKS_DIR, "crpc", "crpc_chunks.json"), "w", encoding="utf-8") as f:
        json.dump(crpc_chunks, f, indent=2, ensure_ascii=False)

    print(f"✓ IPC chunks: {len(ipc_chunks)}")
    print(f"✓ CRPC chunks: {len(crpc_chunks)}")
    print("✅ Chunking completed successfully")


if __name__ == "__main__":
    run_chunking()
  
  