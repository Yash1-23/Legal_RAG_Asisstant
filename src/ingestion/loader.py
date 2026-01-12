import os
from pypdf import PdfReader
BASE_DIR = os.getcwd() #project root
RAW_PDF_DIR = os.path.join(BASE_DIR,"data","raw_pdfs")
EXTRACTED_DIR = os.path.join(BASE_DIR,"data","extracted")


def extracted_pdf_pages(pdf_path: str, prefix:str):
  reader = PdfReader(pdf_path)
  
  for page_num, page in enumerate(reader.pages,start=1):
    text = page.extract_text()
    
    if not text or not text.strip():
      continue
    
    file_name = f"{prefix}_page_{page_num:03}.txt"
    output_path = os.path.join(EXTRACTED_DIR, file_name)
    
    with open(output_path, "w", encoding="utf-8") as f:
      f.write(text)
      

def run_loader():
  os.makedirs(EXTRACTED_DIR,exist_ok=True)
  
  for law in ["ipc","crpc"]:
    law_folder = os.path.join(RAW_PDF_DIR,law)
    
    if not os.path.exists(law_folder):
      raise FileNotFoundError(f"Folder not found: {law_folder}")
    
    for file in os.listdir(law_folder):
      if file.endswith(".pdf"):
        pdf_path = os.path.join(law_folder, file)
        print(f"loading:{pdf_path}")
        extracted_pdf_pages(pdf_path, law)
        
        
        
if __name__ == "__main__":
  run_loader()
  print("PDF loading completed")     