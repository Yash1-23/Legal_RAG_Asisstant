import os
import re
from typing import List,Optional,Tuple
import json
import glob


from rank_bm25 import BM25Okapi

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS  
from langchain_core.documents import Document   

VECTOR_STORE_PATH = os.path.join("data","vector_store")
INDEX_NAME = "legal"
CHUNKS_DIR = os.path.join("data","chunks_v2")

def direct_section_lookup(vector_db, law: str, section: str) -> List[Document]:
    filters = {"section": section}
    if law:
        filters["law"] = law

    return vector_db.similarity_search(
        query=f"{law} Section {section}",
        k=2,
        filter=filters
    )

def parse_law_and_section(query:str)  ->Tuple[Optional[str],Optional[str]]:
  q=query.lower()
  
  law=None
  if "ipc" in q:
    law="IPC"
  elif "crpc" in q or "criminal procedure" in q:
    law = "CRPC"
  
  section_match = re.search(r"\b(\d+[A-Z]*(?:\(\d+\))?)\b",query)
  section = section_match.group(1) if section_match else None
  
  return law, section

def load_all_chunks():
  all_chunks =[]
  files = glob.glob(os.path.join(CHUNKS_DIR,"**","*.json"),recursive=True)
  for file in files:
    with open(file,"r", encoding="utf-8") as f:
      all_chunks.extend(json.load(f))
  return all_chunks
  
ALL_CHUNKS = load_all_chunks()

if not ALL_CHUNKS:
  raise ValueError("NO chunks found for BM25. Check CHUNKS_DIR path.")

## BM25 
BM25_CORPUS = [chunk["text"] for chunk in ALL_CHUNKS]
BM25_TOKENIZED = [doc.lower().split() for doc in BM25_CORPUS]
BM25 = BM25Okapi(BM25_TOKENIZED)




#Load langchain Embedding model
def load_embedding_model() ->HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
  

# Load Faiss vector store
def load_vector_store(embedder):
    absolute_path = os.path.abspath(VECTOR_STORE_PATH)
    return FAISS.load_local(
      folder_path = absolute_path,
      index_name=INDEX_NAME,
      embeddings=embedder,
      allow_dangerous_deserialization=True
    )


# Vector Retriever Function
def retrieve(query: str,top_k:int=5) -> List[Document]:
  
    embedder = load_embedding_model()
    vector_db = load_vector_store(embedder)
   
    law, section = parse_law_and_section(query)
   
    if section:
      docs = direct_section_lookup(vector_db, law, section)
      if docs :
        return docs
  
   
    docs = vector_db.similarity_search(query,k=top_k)
    return docs

# BM25 Retriever
def bm25_retrieve(query: str, top_k: int=5) -> List[Document]:
    tokens = query.lower().split()
    scores = BM25.get_scores(tokens)
    
    top_indices = sorted(range(len(scores)),key=lambda i: scores[i],reverse=True)[:top_k]
    
    docs = [] 
    for idx in top_indices:
        chunk = ALL_CHUNKS[idx]
        docs.append(
          Document(
            page_content = chunk["text"],
            metadata = {
              "law":chunk.get("law"),
              "section":chunk.get("section"),
              "section_title":chunk.get("section_title"),
              "page":chunk.get("page"),
              "source_file":chunk.get("source_file"),
              "chunk_id": chunk.get("chunk_id")
            }
          )
        )
    return docs
  
#Hybrid retriever
def hybrid_retrieve(query:str, top_k: int=5)->List[Document]:
  vector_docs  = retrieve(query,top_k)
  bm25_docs = bm25_retrieve(query, top_k)
  
  if vector_docs is None:
    vector_docs=[]
  if bm25_docs is None:
     bm25_docs=[]
  
  combined = {}
  for doc in vector_docs + bm25_docs:
    key = (doc.metadata.get("source_file"),doc.metadata.get("chunk_id"))
    combined[key] = doc
  results = list(combined.values())
  
  # prefer chunks with real sections (avoid chapters/TOC)
  results.sort(key=lambda d: doc.metadata.get("section") is None)
  return results[:top_k]
#Test 
if __name__ == "__main__":
  test_query = "Explain IPC section 499"
  
  results = hybrid_retrieve(test_query, top_k=3)
  
  print("\n Top Retrieved Documents:\n")
  
  for i ,doc in enumerate(results):
    print(f"\nResult {i+1}--")
    print("Section:",doc.metadata.get("section"))
    print(doc.page_content[:300])
    print("-"*40)
