import re
import os
from typing import List

class LegalTextCleaner:
  """
     Clean legal text while preserving:
     -section numbers
     -sub-sections (1),(a),(b)
     -Heading and legal meaning
  """
  
  def __init__(self):
    #common and unwanted pattern in legal pdfs
    self.page_number_pattern = re.compile(r"\bPage\s+\d+\b",re.IGNORECASE)
    self.header_footer_pattern = re.compile( r"(THE\s+INDIAN\s+PENAL\s+CODE.*?|CODE\s+OF\s+CRIMINAL\s+PROCEDURE.*?1973)",
            re.IGNORECASE)
    self.arrangement_pattern = re.compile(r"ARRANGEMENT\s+OF\s+SECTIONS.*?(?=\n\s*\d+\.)",
            re.IGNORECASE | re.DOTALL)
    self.multiple_spaces = re.compile(r"[ \t]{2,}")
    self.multiple_newlines = re.compile(r"\n{3,}")
    
  
  def clean_text(self, text:str) -> str:
    "Main cleaning pipeline"
    
    if not text or not text.strip():
      return ""
    
    text = self._remove_headers_and_toc(text)
    text = self._remove_page_numbers(text)
    text = self._preserve_section_boundaries(text)

    text = self._normalize_whitespace(text)
    
    return text.strip()
  
  def _remove_headers_and_toc(self,text:str) -> str:
    #Remove the headers like IPC/Crpc titles
    text =self.header_footer_pattern.sub("",text)
    #Remove arrangement of sections
    text = re.sub(
              r"ARRANGEMENT\s+OF\s+SECTIONS.*?(?=\n\s*\d+\.)",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL

    )
    return text
  def _remove_page_numbers(self,text:str)-> str:
    return self.page_number_pattern.sub("",text)
  
  def _remove_headers_and_footers(self,text:str)->str:
    return self.header_footer_pattern.sub("",text)
  
  def _preserve_section_boundaries(self, text: str) -> str:
        """
        Fix OCR issues like:
        '58 217. Public servant disobeying...'
        → '217. Public servant disobeying...'
        """

        # Remove page-number + section-number collision
        text = re.sub(
            r"(?:^|\n)\s*\d+\s+(\d+[A-Z]*(?:\(\d+\))?)\.",
            r"\n\1.",
            text
        )

        # Ensure every section starts on a new line
        text = re.sub(
            r"\s+(\d+[A-Z]*(?:\(\d+\))?)\.",
            r"\n\1.",

            text
        )
        return text
  def _normalize_whitespace(self,text:str)->str:
    text = self.multiple_spaces.sub(" ", text)
    text = self.multiple_newlines.sub("\n\n",text)
    return text
  
  

def clean_file(input_path: str, output_path:str):
  cleaner = LegalTextCleaner()
  
  
  with open(input_path,"r", encoding="utf-8") as f:
    raw_text = f.read()
    
    
  cleaned_text = cleaner.clean_text(raw_text)
  
  with open(output_path,"w", encoding="utf-8") as f:
    f.write(cleaned_text)
    
  print(f"Cleaned file: {os.path.basename(input_path)}")
  

if __name__ == "__main__":
  input_dir = os.path.join("data","extracted")
  output_dir = os.path.join("data","cleaned_text")
  
  os.makedirs(output_dir, exist_ok=True)
  
  for file_name in os.listdir(input_dir):
    if file_name.endswith(".txt"):
      input_path = os.path.join(input_dir, file_name)
      output_path = os.path.join(output_dir, file_name.replace(".txt","_cleaned.txt"))
      clean_file(input_path, output_path)
      
  print("All extracted files cleaned successfully")
  
    


