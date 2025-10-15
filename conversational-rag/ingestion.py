from typing import List 
from PyPDF2 import PDFReader 

def extract_text_from_pdf(file_path: str)-> str:
    reader = PDFReader(file_path)
    return " ".join