from fastapi import FastAPI  
from pydantic import BaseModel
from src.rag_service import generate_answer

app=FastAPI(
  title="Legal RAG API",
  version="1.0"
)

class QueryRequest(BaseModel):
  query: str
  top_k: int=5
 
#health check
@app.get("/")
def health():
  return {"status":"ok"}

#Main RAG endpoint
@app.post("/query")
def query_rag(req: QueryRequest):
  return {"answer": generate_answer(req.query,req.top_k)}