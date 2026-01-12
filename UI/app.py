import streamlit as st  
import requests

#  FastAPI endpoint
API_URL = "http://127.0.0.1:8000/query"

st.set_page_config(
  page_title="Legal RAG Assistant",
  layout = "centered"
)

st.title("Legal RAG Assistant")
st.write("Ask questions related to IPC sections/Code of Criminal procedure crpc")


#intput box
query = st.text_area(
  "Enter your legal question:",
  placeholder="e.g. What sections apply in a attempt to murder case?"
)

if st.button("Ask"):
  if query.strip() == "":
    st.warning("Please enter a question.")
  else:
    with st.spinner("Searching legal documents..."):
       response = requests.post(
         API_URL,
         json={"query":query}
       )
       
    if response.status_code==200:
      answer = response.json()["answer"]
      
      st.subheader("Answer")
      st.write(answer)
    else:
      st.error("Error connection to backend")
    