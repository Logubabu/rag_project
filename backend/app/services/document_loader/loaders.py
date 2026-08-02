import os
import json
import zipfile
import tempfile
import csv
import openpyxl
from docx import Document
from typing import List, Dict

class DocumentLoader:
    def __init__(self):
        self.supported_extensions = {
            ".pdf": self.load_pdf,
            ".docx": self.load_docx,
            ".txt": self.load_text,
            ".md": self.load_text,
            ".csv": self.load_csv,
            ".xlsx": self.load_excel,
            ".json": self.load_json,
            ".html": self.load_text,
            ".xml": self.load_text,
            ".py": self.load_text,
            ".js": self.load_text,
            ".ts": self.load_text,
            ".java": self.load_text,
            ".sql": self.load_text,
            ".yaml": self.load_text,
            ".ini": self.load_text,
            ".log": self.load_text,
        }

    def load_file(self, file_path: str) -> List[Dict[str, str]]:
        _, ext = os.path.splitext(file_path.lower())

        if ext == '.zip':
            return self.load_zip(file_path)

        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {ext}")

        loader_func = self.supported_extensions[ext]
        try:
            content = loader_func(file_path)
            if not content.strip():
                return []
            return [{"filename": os.path.basename(file_path), "content": content}]
        except Exception as e:
            raise RuntimeError(f"Error loading {file_path}: {str(e)}")

    def load_zip(self, zip_path: str) -> List[Dict[str, str]]:
        extracted_docs = []
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file_path.lower())
                    if ext in self.supported_extensions:
                        try:
                            content = self.supported_extensions[ext](file_path)
                            if content.strip():
                                extracted_docs.append({
                                    "filename": file,
                                    "content": content
                                })
                        except Exception as e:
                            print(f"Skipping {file} due to error: {e}")
        return extracted_docs

    def load_pdf(self, file_path: str) -> str:
        import pypdf
        text = ""
        with open(file_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text

    def load_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def load_text(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def load_csv(self, file_path: str) -> str:
        text = ""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            for row in reader:
                text += "\t".join(row) + "\n"
        return text

    def load_excel(self, file_path: str) -> str:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        text = ""
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                text += "\t".join([str(cell) if cell is not None else "" for cell in row]) + "\n"
        return text

    def load_json(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return json.dumps(data, indent=2)

document_loader = DocumentLoader()
