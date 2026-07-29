"""
rag/indexer.py — Phase 5: Local Knowledge Base Indexer
Scans local files (PDFs, code, text, markdown) and stores chunked content
in SQLite for fast retrieval by the RAGRetriever.
"""
import os
import re
from pathlib import Path
from typing import Optional

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    ".txt", ".md", ".py", ".js", ".ts", ".jsx", ".tsx",
    ".html", ".css", ".json", ".yaml", ".yml", ".xml",
    ".java", ".cpp", ".c", ".cs", ".go", ".rs", ".rb",
    ".sh", ".bat", ".env", ".cfg", ".ini", ".toml",
    ".pdf", ".rst"
}

CHUNK_SIZE = 800    # Characters per chunk
CHUNK_OVERLAP = 100 # Overlap between chunks for context continuity


class LocalKnowledgeIndexer:
    """
    Indexes local files into the SQLite database for RAG retrieval.
    Supports PDFs, source code, markdown, text files.
    """

    def __init__(self, db):
        """
        Args:
            db: DatabaseMemory instance
        """
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def index_folder(self, folder_path: str, recursive: bool = True) -> dict:
        """
        Scans a folder and indexes all supported files.
        Returns a summary dict with counts.
        """
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return {"success": False, "error": f"Folder not found: {folder_path}"}

        results = {"indexed": 0, "skipped": 0, "errors": 0, "files": []}

        pattern = "**/*" if recursive else "*"
        for filepath in folder.glob(pattern):
            if filepath.is_file() and filepath.suffix.lower() in SUPPORTED_EXTENSIONS:
                # Skip hidden files and common junk directories
                parts = filepath.parts
                if any(p.startswith(".") or p in {"node_modules", "__pycache__", ".git", "dist", "build", ".venv", "venv"} for p in parts):
                    results["skipped"] += 1
                    continue
                try:
                    count = self._index_file(str(filepath))
                    if count > 0:
                        results["indexed"] += 1
                        results["files"].append(filepath.name)
                    else:
                        results["skipped"] += 1
                except Exception:
                    results["errors"] += 1

        return results

    def index_file(self, filepath: str) -> dict:
        """Indexes a single file. Returns summary dict."""
        fp = Path(filepath)
        if not fp.exists():
            return {"success": False, "error": f"File not found: {filepath}"}
        if fp.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return {"success": False, "error": f"Unsupported file type: {fp.suffix}"}
        try:
            count = self._index_file(filepath)
            if count == 0 and fp.suffix.lower() == ".pdf":
                return {"success": False, "error": "Image/Scanned PDF without text layer", "chunks": 0, "file": fp.name}
            return {"success": True, "chunks": count, "file": fp.name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_indexed_files(self) -> list:
        """Returns list of all indexed files from the database."""
        return self.db.get_indexed_files()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _index_file(self, filepath: str) -> int:
        """Extracts text from a file, chunks it, and stores in DB. Returns chunk count."""
        ext = Path(filepath).suffix.lower()

        if ext == ".pdf":
            text = self._extract_pdf(filepath)
        else:
            text = self._extract_text(filepath)

        if not text or len(text.strip()) < 10:
            return 0

        chunks = self._chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

        # Clear previous index for this file before re-indexing
        self.db.clear_rag_chunks_for_file(filepath)

        for i, chunk in enumerate(chunks):
            self.db.add_rag_chunk(filepath, chunk, chunk_index=i)

        return len(chunks)

    def _extract_text(self, filepath: str) -> str:
        """Reads a plain text file with encoding fallback."""
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                with open(filepath, "r", encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, PermissionError):
                continue
        return ""

    def _extract_pdf(self, filepath: str) -> str:
        """Extracts text content from a PDF file using pdfplumber with pypdf fallback."""
        pages = []

        # Engine 1: pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages[:100]:
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append(text.strip())
            if pages:
                return "\n\n".join(pages)
        except Exception as e:
            print(f"[PDF Indexer] pdfplumber notice: {e}")

        # Engine 2: pypdf fallback
        try:
            import pypdf
            reader = pypdf.PdfReader(filepath)
            for page in reader.pages[:100]:
                text = page.extract_text()
                if text and text.strip():
                    pages.append(text.strip())
            if pages:
                return "\n\n".join(pages)
        except Exception as e:
            print(f"[PDF Indexer] pypdf notice: {e}")

        return ""


    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> list:
        """Splits text into overlapping chunks for better context retrieval."""
        # Clean excess whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size

            # Try to break at a natural boundary (newline, period, space)
            if end < text_len:
                for boundary in ['\n\n', '\n', '. ', ' ']:
                    pos = text.rfind(boundary, start, end)
                    if pos > start + overlap:
                        end = pos + len(boundary)
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = max(start + 1, end - overlap)

        return chunks
