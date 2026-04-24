import os
from pypdf import PdfReader

def extract_pdf_text(filepath):
    try:
        reader = PdfReader(filepath)
        text = ""
        for i, page in enumerate(reader.pages):
            text += f"\n--- Page {i + 1} ---\n"
            text += page.extract_text() + "\n"
        
        with open("pdf_content.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Successfully extracted PDF text to pdf_content.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_pdf_text(r"C:\Users\Admin\Downloads\DMBI INDEX_merged (1).pdf")
