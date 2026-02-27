#!/usr/bin/env python3
"""Add fish species PDFs to RAG database"""
import sys
sys.path.insert(0, '/opt/d3kos/services/documents')

from pdf_processor import PDFProcessor
import os
import time

processor = PDFProcessor()
pdf_dir = "/opt/d3kos/datasets/fish-rag/species_pdfs"

print("=" * 60)
print("ADDING FISH SPECIES PDFs TO RAG DATABASE")
print("=" * 60)
print("")

pdfs = sorted([f for f in os.listdir(pdf_dir) if f.endswith(".pdf")])
print(f"Found {len(pdfs)} fish species PDFs")
print("")

success_count = 0
for i, pdf in enumerate(pdfs, 1):
    pdf_path = os.path.join(pdf_dir, pdf)
    print(f"[{i}/{len(pdfs)}] Adding {pdf}...", flush=True)

    try:
        result = processor.add_document(pdf_path)

        if result.get("success"):
            chunks = result.get("chunks", 0)
            chars = result.get("characters", 0)
            print(f"  ✓ Added: {chunks} chunks, {chars} chars")
            success_count += 1
        else:
            error = result.get("error", "Unknown error")
            print(f"  ✗ Failed: {error}")

        # Small delay to avoid overwhelming the system
        time.sleep(0.5)

    except Exception as e:
        print(f"  ✗ Error: {e}")

    print("")

print("=" * 60)
print(f"✓ COMPLETE: Added {success_count}/{len(pdfs)} species to RAG database")
print("=" * 60)
