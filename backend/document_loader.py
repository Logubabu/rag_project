import os
import json
import zipfile
import pandas as pd
import fitz  # PyMuPDF
from docx import Document
import shutil
from typing import List, Dict

def extract_text(file_path: str) -> str:
    ext = file_path.lower().split('.')[-1]
    text = ""
    
    try:
        if ext == 'pdf':
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text() + "\n"
        elif ext == 'docx':
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext == 'csv':
            df = pd.read_csv(file_path)
            text = df.to_string()
        elif ext == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                text = json.dumps(data, indent=2)
        else:
            # Fallback for txt, md, py, js, ts, java, sql, html, xml, log
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        
    return text

def process_file(file_path: str, upload_dir: str) -> List[Dict[str, str]]:
    """
    Processes a file. If it's a zip, extracts it and processes contents.
    Returns a list of dicts with 'filename' and 'text'.
    """
    ext = file_path.lower().split('.')[-1]
    
    if ext == 'zip':
        extracted_dir = os.path.join(upload_dir, f"extracted_{os.path.basename(file_path)}")
        os.makedirs(extracted_dir, exist_ok=True)
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)
            
        results = []
        for root, dirs, files in os.walk(extracted_dir):
            for file in files:
                current_file = os.path.join(root, file)
                # Ignore hidden files or directories
                if not file.startswith('.'):
                    text = extract_text(current_file)
                    if text.strip():
                        results.append({'filename': file, 'text': text})
        return results
    else:
        text = extract_text(file_path)
        if text.strip():
            return [{'filename': os.path.basename(file_path), 'text': text}]
        return []
