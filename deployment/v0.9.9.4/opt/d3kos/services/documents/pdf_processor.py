#!/usr/bin/env python3
"""
d3kOS PDF Learning System (RAG)
Allows Ollama to learn from PDFs and permanently retain knowledge

Uses:
- PyMuPDF: PDF text extraction
- LangChain: Document chunking
- Ollama: Embeddings (nomic-embed-text) + LLM (phi3.5)
- ChromaDB: Vector storage

Author: d3kOS Project
Date: 2026-02-27
"""

import os
import json
import fitz  # PyMuPDF
from typing import List, Dict, Optional
import subprocess
import hashlib
import re

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

# Paths
UPLOAD_DIR = "/opt/d3kos/data/uploaded-pdfs"
VECTOR_DB_DIR = "/opt/d3kos/data/vector-db"
METADATA_FILE = "/opt/d3kos/data/pdf-metadata.json"

class PDFProcessor:
    """Process PDFs for RAG system"""

    def __init__(self):
        """Initialize PDF processor"""
        self.upload_dir = UPLOAD_DIR
        self.vector_db_dir = VECTOR_DB_DIR
        self.metadata_file = METADATA_FILE

        # Ensure directories exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.vector_db_dir, exist_ok=True)

        # Initialize embeddings model (Ollama nomic-embed-text)
        print("Initializing embeddings model...", flush=True)
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://localhost:11434"
        )

        # Initialize vector store
        print("Initializing vector store...", flush=True)
        self.vector_store = Chroma(
            collection_name="d3kos_documents",
            embedding_function=self.embeddings,
            persist_directory=self.vector_db_dir
        )

        # Load metadata
        self.metadata = self._load_metadata()

        print("✓ PDF Processor initialized", flush=True)

    def _load_metadata(self) -> Dict:
        """Load PDF metadata from disk"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        """Save PDF metadata to disk"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _compute_file_hash(self, filepath: str) -> str:
        """Compute SHA-256 hash of file for deduplication"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        print(f"Extracting text from: {os.path.basename(pdf_path)}", flush=True)

        text = ""
        page_count = 0
        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)

            for page_num in range(page_count):
                page = doc.load_page(page_num)
                text += page.get_text()

            doc.close()

            print(f"  ✓ Extracted {len(text)} characters from {page_count} pages", flush=True)
            return text

        except Exception as e:
            print(f"  ✗ Error extracting text: {e}", flush=True)
            return ""

    def chunk_text(self, text: str, filename: str) -> List[Document]:
        """Split text into chunks for embedding"""
        print(f"Chunking text from {filename}...", flush=True)

        # Create text splitter
        # 500 chars per chunk, 50 char overlap for context
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        # Split text
        chunks = text_splitter.split_text(text)

        # Create LangChain Document objects with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "source": filename,
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                }
            )
            documents.append(doc)

        print(f"  ✓ Created {len(documents)} chunks", flush=True)
        return documents

    def add_document(self, pdf_path: str) -> Dict:
        """
        Add a PDF document to the knowledge base

        Returns:
            Dict with status and information
        """
        filename = os.path.basename(pdf_path)
        print(f"\n{'='*60}", flush=True)
        print(f"Adding document: {filename}", flush=True)
        print(f"{'='*60}\n", flush=True)

        # Check if file exists
        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "error": f"File not found: {pdf_path}"
            }

        # Compute file hash
        file_hash = self._compute_file_hash(pdf_path)

        # Check if already processed
        if file_hash in self.metadata:
            print(f"⚠ Document already exists: {self.metadata[file_hash]['filename']}", flush=True)
            return {
                "success": False,
                "error": "Document already exists",
                "existing": self.metadata[file_hash]
            }

        # Extract text
        text = self.extract_text_from_pdf(pdf_path)

        if not text or len(text) < 100:
            return {
                "success": False,
                "error": "No text extracted or text too short"
            }

        # Chunk text
        documents = self.chunk_text(text, filename)

        if not documents:
            return {
                "success": False,
                "error": "No chunks created"
            }

        # Add to vector store
        print(f"Adding {len(documents)} chunks to vector database...", flush=True)
        try:
            # Generate embeddings and store
            self.vector_store.add_documents(documents)

            # langchain-chroma persists automatically — no explicit call needed

            print(f"  ✓ Added to vector database", flush=True)

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to add to vector store: {e}"
            }

        # Save metadata
        self.metadata[file_hash] = {
            "filename": filename,
            "filepath": pdf_path,
            "hash": file_hash,
            "chunks": len(documents),
            "characters": len(text),
            "added_at": subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode().strip()
        }
        self._save_metadata()

        print(f"\n{'='*60}", flush=True)
        print(f"✓ Document successfully added to knowledge base!", flush=True)
        print(f"{'='*60}\n", flush=True)

        return {
            "success": True,
            "filename": filename,
            "chunks": len(documents),
            "characters": len(text)
        }

    def add_document_with_text(self, pdf_path: str, text: str) -> Dict:
        """Add a document using pre-extracted text (e.g. from Gemini Vision OCR)."""
        filename = os.path.basename(pdf_path)
        print(f"\n{'='*60}", flush=True)
        print(f"Adding document (pre-extracted): {filename}", flush=True)
        print(f"{'='*60}\n", flush=True)

        file_hash = self._compute_file_hash(pdf_path)

        if file_hash in self.metadata:
            print(f"⚠ Document already exists: {self.metadata[file_hash]['filename']}", flush=True)
            return {"success": False, "error": "Document already exists", "existing": self.metadata[file_hash]}

        if not text or len(text) < 100:
            return {"success": False, "error": "Text too short"}

        documents = self.chunk_text(text, filename)
        if not documents:
            return {"success": False, "error": "No chunks created"}

        print(f"Adding {len(documents)} chunks to vector database...", flush=True)
        try:
            self.vector_store.add_documents(documents)
            self.vector_store.persist()
            print(f"  ✓ Added to vector database", flush=True)
        except Exception as e:
            return {"success": False, "error": f"Failed to add to vector store: {e}"}

        self.metadata[file_hash] = {
            "filename": filename,
            "filepath": pdf_path,
            "hash": file_hash,
            "chunks": len(documents),
            "characters": len(text),
            "added_at": subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode().strip()
        }
        self._save_metadata()

        print(f"\n{'='*60}", flush=True)
        print(f"✓ Document successfully added to knowledge base!", flush=True)
        print(f"{'='*60}\n", flush=True)

        return {"success": True, "filename": filename, "chunks": len(documents), "characters": len(text)}

    def search(self, query: str, k: int = 3) -> List[Dict]:
        """
        Search for relevant document chunks with relevance filtering
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of relevant chunks with metadata
        """
        print(f"Searching for: {query}", flush=True)
        
        try:
            # Perform similarity search with scores (higher k to filter later)
            results = self.vector_store.similarity_search(query, k=k)
            
            
            # Format results
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "chunk_id": doc.metadata.get("chunk_id", 0)
                })
            
            
            # Re-rank by keyword matching
            query_words = set(re.findall(r"\w+", query.lower()))
            stopwords = {"the", "a", "an", "is", "are", "what", "how", "in", "on", "for"}
            keywords = query_words - stopwords
            
            # Score each result
            scored = []
            for doc in results:
                content_lower = doc.page_content.lower()
                score = sum(1 for kw in keywords if kw in content_lower)
                scored.append((score, doc))
            
            # Sort by score (highest first)
            scored.sort(key=lambda x: x[0], reverse=True)
            results = [doc for score, doc in scored]
            
            print(f"  ✓ Found {len(results)} relevant chunks", flush=True)
            return formatted_results
        
        except Exception as e:
            print(f"  ✗ Search error: {e}", flush=True)
            return []

    def query_with_context(self, question: str, k: int = 3) -> str:
        """
        Query Ollama with context from PDFs

        Args:
            question: User's question
            k: Number of context chunks to retrieve

        Returns:
            Ollama's response
        """
        print(f"\nQuerying with context: {question}", flush=True)

        # Search for relevant chunks
        chunks = self.search(question, k=k)

        if not chunks:
            # No relevant context found
            print("  ⚠ No relevant context found, querying without context", flush=True)
            return self._query_ollama(question, context="")

        # Build context from chunks
        context = "\n\n".join([
            f"From {chunk['source']}:\n{chunk['content']}"
            for chunk in chunks
        ])

        print(f"  ✓ Retrieved context from {len(set([c['source'] for c in chunks]))} document(s)", flush=True)

        # Query Ollama with context
        return self._query_ollama(question, context)

    def _query_ollama(self, question: str, context: str) -> str:
        """
        Query Ollama LLM with optional context

        Args:
            question: User's question
            context: Relevant context from PDFs (optional)

        Returns:
            Ollama's response
        """
        if context:
            prompt = f"""Based on the following information from the documentation:

{context}

Answer this question: {question}

If the information above doesn't contain the answer, say so clearly."""
        else:
            prompt = question

        print(f"  → Querying Ollama...", flush=True)

        try:
            # Run ollama via subprocess
            result = subprocess.run(
                ['ollama', 'run', 'phi3.5', prompt],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if result.returncode == 0:
                response = result.stdout.strip()
                print(f"  ✓ Received response ({len(response)} chars)", flush=True)
                return response
            else:
                return f"Error: Ollama failed with code {result.returncode}"

        except subprocess.TimeoutExpired:
            return "Error: Query timed out (2 minutes)"
        except Exception as e:
            return f"Error: {e}"

    def list_documents(self) -> List[Dict]:
        """List all documents in the knowledge base"""
        return list(self.metadata.values())

    def delete_document(self, filename: str) -> Dict:
        """
        Delete a document from the knowledge base

        Note: ChromaDB doesn't easily support deletion by metadata.
        For simplicity, we'll mark as deleted in metadata but keep in vector DB.
        Full rebuild would be needed to truly remove.
        """
        # Find document by filename
        doc_hash = None
        for hash_val, meta in self.metadata.items():
            if meta['filename'] == filename:
                doc_hash = hash_val
                break

        if not doc_hash:
            return {
                "success": False,
                "error": f"Document not found: {filename}"
            }

        # Remove from metadata
        del self.metadata[doc_hash]
        self._save_metadata()

        # Remove PDF file
        filepath = os.path.join(self.upload_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        return {
            "success": True,
            "message": f"Document {filename} removed from metadata and deleted"
        }


def main():
    """Test the PDF processor"""
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Add document:    python3 pdf_processor.py add <pdf_path>")
        print("  Search:          python3 pdf_processor.py search <query>")
        print("  Query with LLM:  python3 pdf_processor.py query <question>")
        print("  List documents:  python3 pdf_processor.py list")
        print("  Delete document: python3 pdf_processor.py delete <filename>")
        sys.exit(1)

    # Initialize processor
    processor = PDFProcessor()

    command = sys.argv[1]

    if command == "add" and len(sys.argv) >= 3:
        pdf_path = sys.argv[2]
        result = processor.add_document(pdf_path)
        print(json.dumps(result, indent=2))

    elif command == "search" and len(sys.argv) >= 3:
        query = " ".join(sys.argv[2:])
        results = processor.search(query, k=3)
        print(json.dumps(results, indent=2))

    elif command == "query" and len(sys.argv) >= 3:
        question = " ".join(sys.argv[2:])
        response = processor.query_with_context(question, k=3)
        print("\nResponse:")
        print(response)

    elif command == "list":
        docs = processor.list_documents()
        print(json.dumps(docs, indent=2))

    elif command == "delete" and len(sys.argv) >= 3:
        filename = sys.argv[2]
        result = processor.delete_document(filename)
        print(json.dumps(result, indent=2))

    else:
        print("Unknown command or missing arguments")
        sys.exit(1)


if __name__ == "__main__":
    main()
