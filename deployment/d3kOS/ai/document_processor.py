#!/usr/bin/env python3
"""
d3kOS Document Processor with RAG Integration
Extracts text from PDFs, populates skills.md, and adds to RAG vector database.
Falls back to Gemini Vision OCR for scanned image PDFs.
"""

import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("PyPDF2 not installed. Install with: pip3 install --break-system-packages PyPDF2")
    exit(1)

try:
    import fitz  # PyMuPDF — for page rendering when OCR fallback is needed
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

# Add PDF processor to path for RAG integration
sys.path.insert(0, '/opt/d3kos/services/documents')

# Paths
MANUALS_DIR = "/opt/d3kos/data/manuals"
SKILLS_PATH = "/opt/d3kos/config/skills.md"
# Import PDF processor for RAG (optional - fail gracefully if not available)
try:
    from pdf_processor import PDFProcessor
    RAG_AVAILABLE = True
    print("✓ RAG integration enabled", flush=True)
except ImportError as e:
    RAG_AVAILABLE = False
    print(f"⚠ RAG integration disabled: {e}", flush=True)


class DocumentProcessor:
    def __init__(self):
        self.manuals_dir = Path(MANUALS_DIR)
        self.skills_path = Path(SKILLS_PATH)
        self.manuals_dir.mkdir(parents=True, exist_ok=True)

        if RAG_AVAILABLE:
            try:
                self.rag_processor = PDFProcessor()
                print("✓ RAG processor initialized", flush=True)
            except Exception as e:
                print(f"⚠ RAG processor initialization failed: {e}", flush=True)
                self.rag_processor = None
        else:
            self.rag_processor = None

    def _extract_text_tesseract(self, pdf_path):
        """
        OCR fallback for scanned PDFs using tesseract (local, free, no rate limits).
        Renders each page via fitz at 200 DPI, runs tesseract OCR, returns combined text.
        """
        if not FITZ_AVAILABLE:
            print("⚠ PyMuPDF not available — cannot run OCR", flush=True)
            return ""

        try:
            import pytesseract
            from PIL import Image
            import io
        except ImportError:
            print("⚠ pytesseract/Pillow not installed — cannot run OCR", flush=True)
            return ""

        print(f"🔍 Scanned PDF detected — running tesseract OCR (local)", flush=True)

        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        print(f"   {total_pages} pages — processing in background...", flush=True)

        all_text = []
        for page_num in range(total_pages):
            if page_num % 10 == 0:
                print(f"   Page {page_num + 1}/{total_pages}...", flush=True)
            page = doc[page_num]
            # 150 DPI — sufficient for printed manuals, faster on Pi 4
            mat = fitz.Matrix(150 / 72, 150 / 72)
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            try:
                text = pytesseract.image_to_string(img, lang='eng', timeout=120)
                if text.strip():
                    all_text.append(f"\n--- Page {page_num + 1} ---\n{text.strip()}")
            except Exception as e:
                print(f"   ⚠ Page {page_num + 1} OCR failed: {e}", flush=True)

        doc.close()
        combined = "\n".join(all_text).strip()
        print(f"✓ Tesseract OCR complete — {len(combined)} characters extracted", flush=True)
        return combined

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF. Falls back to Gemini Vision OCR for scanned PDFs."""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num} ---\n"
                        text += page_text
                except Exception as e:
                    print(f"  Warning: Could not extract page {page_num}: {e}")

            if text.strip():
                return text.strip()

            # No text extracted — scanned PDF, use tesseract OCR
            return self._extract_text_tesseract(pdf_path)

        except Exception as e:
            print(f"  Error extracting PDF: {e}")
            return None

    def process_manual(self, pdf_path, manual_type="boat"):
        """Process a manual and extract key information"""
        print(f"Processing: {pdf_path}")

        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return None

        filename = Path(pdf_path).name
        sections = self.identify_sections(text)

        return {
            "filename": filename,
            "type": manual_type,
            "text": text,
            "sections": sections,
            "processed_date": datetime.now().isoformat()
        }

    def identify_sections(self, text):
        """Identify common manual sections"""
        sections = {}
        patterns = {
            "specifications": r"(specifications|technical data|engine data)",
            "maintenance": r"(maintenance|service|schedule)",
            "troubleshooting": r"(troubleshooting|problems|diagnostics)",
            "safety": r"(safety|warnings|cautions)",
            "operation": r"(operation|operating|procedures)"
        }
        for section_name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                sections[section_name] = match.start()
        return sections

    def extract_specifications(self, text):
        """Extract specifications from manual text"""
        specs = {}
        patterns = {
            "displacement": r"displacement[:\s]+([0-9.]+)\s*(L|cu\.? ?in)",
            "horsepower": r"horsepower[:\s]+([0-9.]+)\s*(HP|hp)",
            "cylinders": r"cylinders?[:\s]+([0-9]+)",
            "fuel_type": r"fuel[:\s]+(gasoline|diesel|gas)",
            "oil_capacity": r"oil capacity[:\s]+([0-9.]+)\s*(qt|qts|quarts?|L|liters?)",
            "coolant_capacity": r"coolant capacity[:\s]+([0-9.]+)\s*(qt|qts|quarts?|L|liters?)"
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                specs[key] = match.group(1) + (" " + match.group(2) if len(match.groups()) > 1 else "")
        return specs

    def update_skills_md(self, manual_data):
        """Update skills.md with manual information"""
        if self.skills_path.exists():
            with open(self.skills_path, 'r') as f:
                content = f.read()
        else:
            content = self.create_skills_template()

        manuals_section_start = content.find("## Manuals")
        if manuals_section_start == -1:
            content += "\n\n## Manuals\n\n"
            manuals_section_start = len(content) - 15

        next_section = content.find("##", manuals_section_start + 3)
        manuals_section_end = next_section if next_section != -1 else len(content)

        filename = manual_data['filename']
        manual_type = manual_data.get('type', 'boat')

        new_entry = f"\n### {filename}\n"
        new_entry += f"**Type**: {manual_type}\n"
        new_entry += f"**Added**: {datetime.now().strftime('%Y-%m-%d')}\n\n"

        specs = self.extract_specifications(manual_data['text'])
        if specs:
            new_entry += "**Key Specifications**:\n"
            for key, value in specs.items():
                new_entry += f"- {key.replace('_', ' ').title()}: {value}\n"
            new_entry += "\n"

        text_excerpt = manual_data["text"][:20000].strip()
        new_entry += f"**Content Preview**:\n{text_excerpt}...\n\n"

        updated_content = (
            content[:manuals_section_end] +
            new_entry +
            content[manuals_section_end:]
        )

        with open(self.skills_path, 'w') as f:
            f.write(updated_content)

        print(f"✓ Updated skills.md with {filename}")

    def add_to_rag(self, pdf_path, extracted_text=None):
        """Add PDF to RAG vector database. Uses pre-extracted text if provided."""
        if not self.rag_processor:
            print("⚠ RAG not available - skipping vector database", flush=True)
            return {"success": False, "error": "RAG not available"}

        try:
            print(f"📚 Adding to RAG knowledge base: {Path(pdf_path).name}", flush=True)
            if extracted_text:
                result = self.rag_processor.add_document_with_text(pdf_path, extracted_text)
            else:
                result = self.rag_processor.add_document(pdf_path)

            if result.get('success'):
                print(f"✓ RAG complete: {result.get('chunks')} chunks, {result.get('characters')} characters", flush=True)
            else:
                print(f"⚠ RAG failed: {result.get('error')}", flush=True)

            return result

        except Exception as e:
            print(f"⚠ RAG error: {str(e)}", flush=True)
            return {"success": False, "error": str(e)}

    def create_skills_template(self):
        """Create initial skills.md template"""
        return """# d3kOS Skills Knowledge Base

## System Information
- **OS**: Debian GNU/Linux 13 (Trixie)
- **Hardware**: Raspberry Pi 4B (8GB RAM)
- **Software**: d3kOS v2.0
- **Signal K**: Active on port 3000
- **Node-RED**: Active on port 1880

## Boat Information
*To be populated from onboarding wizard*

## Engine Information
*To be populated from onboarding wizard and manuals*

## Manuals
*Uploaded manuals will appear here*

## Regulations
### USCG Requirements
*To be added*

### ABYC Standards
*To be added*

## Best Practices
### Engine Maintenance
*To be added*

### Safety Procedures
*To be added*

## Conversation History
*Important conversations will be added here automatically*

## Maintenance Log
*Maintenance records will be tracked here*
"""

    def list_manuals(self):
        """List all processed manuals"""
        manuals = []
        if self.manuals_dir.exists():
            for pdf_file in self.manuals_dir.glob("*.pdf"):
                manuals.append(str(pdf_file))
        return manuals


def main():
    """Process a PDF manual and add to both skills.md and RAG database"""
    processor = DocumentProcessor()

    if len(sys.argv) < 2:
        print("Usage: python3 document_processor.py <pdf_file> [manual_type]")
        print("\nExample: python3 document_processor.py engine_manual.pdf engine")
        print("\nManual types: boat, engine, electronics, safety, regulations")
        manuals = processor.list_manuals()
        if manuals:
            print(f"\nFound {len(manuals)} manual(s):")
            for manual in manuals:
                print(f"  - {manual}")
        return

    pdf_path = sys.argv[1]
    manual_type = sys.argv[2] if len(sys.argv) > 2 else "boat"

    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return

    print("=" * 60, flush=True)
    print("d3kOS Document Processor with RAG Integration", flush=True)
    print("=" * 60, flush=True)

    manual_data = processor.process_manual(pdf_path, manual_type)

    if manual_data:
        print(f"\n✓ Extracted {len(manual_data['text'])} characters", flush=True)
        print(f"✓ Found sections: {list(manual_data['sections'].keys())}", flush=True)

        processor.update_skills_md(manual_data)
        rag_result = processor.add_to_rag(pdf_path, extracted_text=manual_data['text'])

        print("\n" + "=" * 60, flush=True)
        print("✓ Manual processing complete", flush=True)
        print("=" * 60, flush=True)
        print(f"Skills.md: Updated", flush=True)
        print(f"RAG Database: {'Added' if rag_result.get('success') else 'Failed'}", flush=True)
        if rag_result.get('success'):
            print(f"  - Chunks: {rag_result.get('chunks', 0)}", flush=True)
            print(f"  - Characters: {rag_result.get('characters', 0)}", flush=True)
        print("=" * 60, flush=True)
    else:
        print("\n✗ Failed to process manual", flush=True)


if __name__ == "__main__":
    main()
