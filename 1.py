# Install required libraries first
# pip install transformers torch PyPDF2 python-docx

from transformers import pipeline
from PyPDF2 import PdfReader
from docx import Document
from pathlib import Path
import math

# Reading functions
def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def read_pdf(file_path):
    pdf = PdfReader(file_path)
    text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def read_docx(file_path):
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Summarization function with chunking for long texts
def summarize_text(text, max_length=150, min_length=40):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Split text into chunks of ~1000 tokens (roughly 750-1000 words)
    chunks = []
    words = text.split()
    chunk_size = 750
    for i in range(0, len(words), chunk_size):
        chunk_text = " ".join(words[i:i+chunk_size])
        chunks.append(chunk_text)
    
    summaries = []
    for idx, chunk in enumerate(chunks):
        print(f"[+] Summarizing chunk {idx+1}/{len(chunks)}...")
        summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    
    # Combine summaries of all chunks
    final_summary = " ".join(summaries)
    return final_summary

def main():
    print("=== Document Summarization System ===")
    file_path = input("Enter file path (TXT, PDF, DOCX): ").strip()
    path = Path(file_path)

    if not path.exists():
        print("[!] File not found.")
        return

    # Read document based on file type
    if path.suffix.lower() == ".txt":
        text = read_txt(path)
    elif path.suffix.lower() == ".pdf":
        text = read_pdf(path)
    elif path.suffix.lower() == ".docx":
        text = read_docx(path)
    else:
        print("[!] Unsupported file format.")
        return

    print("\n[+] Generating summary...")
    summary = summarize_text(text)

    # Save summary to a file in the same folder
    output_file = path.parent / f"{path.stem}_summary.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"\n=== Summary Generated ===\n")
    print(summary)
    print(f"\n[+] Summary saved to: {output_file.resolve()}")

if __name__ == "__main__":
    main()
