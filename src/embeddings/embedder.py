import os
import json 
import pickle
from typing import List,Dict
import numpy as np   
from sentence_transformers import SentenceTransformer

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
CHUNKS_DIR = os.path.join("data","chunks_v2")
VECTOR_DB_DIR = os.path.join("data","vector_store")

os.makedirs(VECTOR_DB_DIR,exist_ok=True)

EMBED_MODEL = "all-MiniLM-L6-v2"

def load_all_chunks() ->List[Dict]:
  all_chunks = []
  for law in ["ipc", "crpc"]:
        law_dir = os.path.join(CHUNKS_DIR, law)
        if not os.path.exists(law_dir):
            continue



        for file_name in os.listdir(law_dir):
         if file_name.endswith("_chunks.json"):
          path = os.path.join(law_dir, file_name)

          with open(path,"r",encoding="utf-8") as f:
            data = json.load(f)
        
          for chunk in data:
            if chunk["text"].strip():
              all_chunks.append(chunk)
          
  return all_chunks


if __name__ == "__main__":
  
  chunks = load_all_chunks()
  
  if not chunks:
    print("No chunks found!")
    exit()
  
  print(f"Loaded {len(chunks)} chunks")
  
  
  #convert to langchain document
  documents = []
  
  for c in chunks:
    documents.append(
      Document(
        page_content=c["text"],
        metadata={
          "law": c["law"],
          "section":c["section"],
          "section_title":c["section_title"],
          "source_file":c["source_file"],
          "chunk_id":c["chunk_id"],
        }
      )
    )
   
  
  # Langchain embedding wrapper
  embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
  
  #create a Fiass DB using Langchain 
  vector_db = FAISS.from_documents(documents,embedder)
  
  #save in langchain format
  vector_db.save_local(folder_path=VECTOR_DB_DIR,index_name="legal")
  print("Vector Store created successfully")