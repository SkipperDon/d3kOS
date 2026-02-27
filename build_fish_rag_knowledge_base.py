#!/usr/bin/env python3
"""
Fish Species RAG Knowledge Base Builder
Builds text corpus + reference images for Ollama + Phi-3.5 + RAG
"""
import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
import time
from bs4 import BeautifulSoup
import urllib.parse
import hashlib

# Configuration
BASE_DIR = Path("/opt/d3kos/datasets/fish-rag")
TEXT_DIR = BASE_DIR / "species_descriptions"
IMAGES_DIR = BASE_DIR / "reference_images"
PDFS_DIR = BASE_DIR / "visual_guides"
OUTPUT_DIR = BASE_DIR / "knowledge_base"
LOG_FILE = BASE_DIR / "rag_builder.log"

# Ensure directories exist
for d in [BASE_DIR, TEXT_DIR, IMAGES_DIR, PDFS_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def log(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + '\n')

def download_file(url, dest_path, description="file"):
    """Download file with retries"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            with open(dest_path, 'wb') as f:
                f.write(response.content)

            log(f"✓ Downloaded: {description} ({len(response.content)} bytes)")
            return True

        except Exception as e:
            if attempt < max_retries - 1:
                log(f"⚠ Download failed (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(5)
            else:
                log(f"✗ Download failed after {max_retries} attempts: {e}")
                return False
    return False

def scrape_ontario_fish_species():
    """Scrape Ontario Freshwater Fishes database for all species"""
    log("=" * 60)
    log("SCRAPING ONTARIO FRESHWATER FISHES DATABASE")
    log("=" * 60)

    base_url = "https://www.ontariofishes.ca"
    species_list_url = f"{base_url}/fish_list.php"

    try:
        # Get species list page
        response = requests.get(species_list_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all species links
        species_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'fish_detail.php?FID=' in href:
                species_links.append(href)

        log(f"Found {len(species_links)} species links")

        # Process each species
        species_data = []
        for idx, link in enumerate(species_links, 1):
            species_url = f"{base_url}/{link}" if not link.startswith('http') else link

            log(f"[{idx}/{len(species_links)}] Processing: {species_url}")

            species_info = scrape_species_page(species_url)
            if species_info:
                species_data.append(species_info)

                # Save individual species JSON
                species_file = TEXT_DIR / f"{species_info['species_id']}.json"
                with open(species_file, 'w') as f:
                    json.dump(species_info, f, indent=2)

            # Rate limiting
            time.sleep(2)

        # Save complete species database
        database_file = OUTPUT_DIR / "ontario_fish_database.json"
        with open(database_file, 'w') as f:
            json.dump(species_data, f, indent=2)

        log(f"✓ Complete database saved: {database_file}")
        log(f"✓ Total species scraped: {len(species_data)}")

        return species_data

    except Exception as e:
        log(f"✗ Failed to scrape species list: {e}")
        return []

def scrape_species_page(url):
    """Scrape individual species detail page"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract species ID from URL
        species_id = url.split('FID=')[1] if 'FID=' in url else hashlib.md5(url.encode()).hexdigest()[:8]

        # Extract species information
        species_info = {
            'species_id': species_id,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'common_name': '',
            'scientific_name': '',
            'family': '',
            'description': '',
            'visual_characteristics': '',
            'habitat': '',
            'distribution': '',
            'size_range': '',
            'conservation_status': '',
            'reference_images': []
        }

        # Extract common name (usually in page title or h1)
        title = soup.find('h1') or soup.find('title')
        if title:
            species_info['common_name'] = title.get_text().strip()

        # Extract scientific name (usually in italics)
        for italic in soup.find_all(['i', 'em']):
            text = italic.get_text().strip()
            if ' ' in text and len(text.split()) == 2:  # Genus species format
                species_info['scientific_name'] = text
                break

        # Extract text content (descriptions, characteristics)
        # Look for specific sections
        for tag in soup.find_all(['p', 'div', 'td']):
            text = tag.get_text().strip()

            # Identify section by keywords
            if any(kw in text.lower() for kw in ['appearance', 'color', 'marking', 'fin', 'scale']):
                if len(text) > 50:
                    species_info['visual_characteristics'] += text + ' '

            elif any(kw in text.lower() for kw in ['habitat', 'found in', 'lives in', 'prefers']):
                if len(text) > 30:
                    species_info['habitat'] += text + ' '

            elif any(kw in text.lower() for kw in ['distribution', 'range', 'ontario', 'lake']):
                if len(text) > 30:
                    species_info['distribution'] += text + ' '

            elif any(kw in text.lower() for kw in ['length', 'size', 'weight', 'cm', 'inches']):
                if len(text) > 20 and len(text) < 200:
                    species_info['size_range'] += text + ' '

            elif len(text) > 100 and not species_info['description']:
                # First long paragraph is usually main description
                species_info['description'] = text

        # Extract images
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and not any(skip in src.lower() for skip in ['logo', 'banner', 'icon', 'button']):
                # Convert relative URL to absolute
                if not src.startswith('http'):
                    src = urllib.parse.urljoin(url, src)

                # Download image
                img_filename = f"{species_id}_{len(species_info['reference_images']) + 1}.jpg"
                img_path = IMAGES_DIR / img_filename

                if download_file(src, img_path, f"{species_info['common_name']} image"):
                    species_info['reference_images'].append(str(img_path))

        # Clean up text fields
        for key in ['visual_characteristics', 'habitat', 'distribution', 'size_range']:
            species_info[key] = ' '.join(species_info[key].split()).strip()

        log(f"  ✓ {species_info['common_name']} - {len(species_info['reference_images'])} images")

        return species_info

    except Exception as e:
        log(f"  ✗ Failed to scrape species page: {e}")
        return None

def download_visual_guides():
    """Download PDF visual identification guides"""
    log("=" * 60)
    log("DOWNLOADING VISUAL IDENTIFICATION GUIDES")
    log("=" * 60)

    guides = [
        {
            'name': 'Salmon and Trout of the Great Lakes',
            'url': 'https://seagrant.sunysb.edu/glsportfish/pdfs/SalmonTrout-LakeOntario2012.pdf',
            'filename': 'salmon_trout_great_lakes.pdf'
        },
        {
            'name': 'Ontario Fishing Regulations',
            'url': 'https://files.ontario.ca/environment-and-energy/fishing/198234.pdf',
            'filename': 'ontario_fishing_regulations.pdf'
        },
        {
            'name': 'Learn to Fish Identification Guide',
            'url': 'https://files.ontario.ca/ndmnrf-learn-to-fish-identification-and-invasive-species-activity-en-form-2021-11-24.pdf',
            'filename': 'learn_to_fish_identification.pdf'
        }
    ]

    downloaded = []
    for guide in guides:
        dest_path = PDFS_DIR / guide['filename']
        log(f"Downloading: {guide['name']}")

        if download_file(guide['url'], dest_path, guide['name']):
            downloaded.append(str(dest_path))

        time.sleep(3)  # Rate limiting

    log(f"✓ Downloaded {len(downloaded)} PDF guides")
    return downloaded

def extract_species_from_pdfs():
    """Extract species information from PDF guides"""
    log("=" * 60)
    log("EXTRACTING TEXT FROM PDF GUIDES")
    log("=" * 60)

    try:
        import PyPDF2

        pdf_texts = {}
        for pdf_file in PDFS_DIR.glob("*.pdf"):
            log(f"Processing: {pdf_file.name}")

            try:
                with open(pdf_file, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"

                    pdf_texts[pdf_file.stem] = text

                    # Save extracted text
                    text_file = TEXT_DIR / f"{pdf_file.stem}.txt"
                    with open(text_file, 'w', encoding='utf-8') as tf:
                        tf.write(text)

                    log(f"  ✓ Extracted {len(text)} characters")

            except Exception as e:
                log(f"  ✗ Failed to extract: {e}")

        return pdf_texts

    except ImportError:
        log("⚠ PyPDF2 not installed. Install with: pip3 install PyPDF2")
        log("⚠ Skipping PDF text extraction")
        return {}

def build_rag_corpus():
    """Build complete RAG corpus from all sources"""
    log("=" * 60)
    log("BUILDING RAG CORPUS")
    log("=" * 60)

    corpus = {
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'version': '1.0',
            'sources': [
                'Ontario Freshwater Fishes Database',
                'NOAA Great Lakes Water Life',
                'Visual Identification Guides'
            ],
            'total_species': 0,
            'total_images': 0
        },
        'species': []
    }

    # Load all species JSON files
    for species_file in TEXT_DIR.glob("*.json"):
        try:
            with open(species_file, 'r') as f:
                species_data = json.load(f)
                corpus['species'].append(species_data)
                corpus['metadata']['total_images'] += len(species_data.get('reference_images', []))
        except Exception as e:
            log(f"⚠ Failed to load {species_file}: {e}")

    corpus['metadata']['total_species'] = len(corpus['species'])

    # Save complete corpus
    corpus_file = OUTPUT_DIR / "fish_rag_corpus.json"
    with open(corpus_file, 'w') as f:
        json.dump(corpus, f, indent=2)

    log(f"✓ RAG corpus saved: {corpus_file}")
    log(f"  Species: {corpus['metadata']['total_species']}")
    log(f"  Images: {corpus['metadata']['total_images']}")

    # Create species embeddings preparation file
    embeddings_prep = []
    for species in corpus['species']:
        # Combine all text for embedding
        text_content = f"""
Species: {species['common_name']} ({species['scientific_name']})
Family: {species['family']}

Description: {species['description']}

Visual Characteristics: {species['visual_characteristics']}

Habitat: {species['habitat']}

Distribution: {species['distribution']}

Size: {species['size_range']}
""".strip()

        embeddings_prep.append({
            'species_id': species['species_id'],
            'common_name': species['common_name'],
            'scientific_name': species['scientific_name'],
            'text_for_embedding': text_content,
            'reference_images': species['reference_images']
        })

    embeddings_file = OUTPUT_DIR / "species_embeddings_prep.json"
    with open(embeddings_file, 'w') as f:
        json.dump(embeddings_prep, f, indent=2)

    log(f"✓ Embeddings prep saved: {embeddings_file}")

    return corpus

def create_quick_reference():
    """Create quick reference guide for common species"""
    log("=" * 60)
    log("CREATING QUICK REFERENCE GUIDE")
    log("=" * 60)

    # Top 30 Great Lakes species for quick lookup
    priority_species = [
        'Yellow Perch', 'Walleye', 'Smallmouth Bass', 'Largemouth Bass',
        'Northern Pike', 'Lake Trout', 'Brook Trout', 'Rainbow Trout',
        'Brown Trout', 'Chinook Salmon', 'Coho Salmon', 'Lake Whitefish',
        'Burbot', 'Black Crappie', 'Bluegill', 'Pumpkinseed',
        'Rock Bass', 'White Bass', 'Muskellunge', 'Channel Catfish',
        'Steelhead', 'Atlantic Salmon', 'Pink Salmon', 'Sockeye Salmon',
        'Freshwater Drum', 'Lake Sturgeon', 'Longnose Gar'
    ]

    quick_ref = {
        'title': 'Great Lakes Fish Quick Reference',
        'created_at': datetime.now().isoformat(),
        'species_count': len(priority_species),
        'species': []
    }

    # Load species data
    for species_file in TEXT_DIR.glob("*.json"):
        try:
            with open(species_file, 'r') as f:
                species_data = json.load(f)
                common_name = species_data.get('common_name', '')

                # Check if priority species
                for priority in priority_species:
                    if priority.lower() in common_name.lower():
                        quick_ref['species'].append({
                            'common_name': species_data['common_name'],
                            'scientific_name': species_data['scientific_name'],
                            'key_features': species_data['visual_characteristics'][:200] + '...',
                            'habitat': species_data['habitat'][:150] + '...',
                            'typical_size': species_data['size_range'],
                            'images': species_data['reference_images'][:3]  # Top 3 images
                        })
                        break
        except:
            pass

    quick_ref_file = OUTPUT_DIR / "quick_reference.json"
    with open(quick_ref_file, 'w') as f:
        json.dump(quick_ref, f, indent=2)

    log(f"✓ Quick reference saved: {quick_ref_file}")
    log(f"  Priority species included: {len(quick_ref['species'])}")

    return quick_ref

def main():
    """Main execution"""
    log("=" * 60)
    log("FISH SPECIES RAG KNOWLEDGE BASE BUILDER")
    log("=" * 60)
    log(f"Output directory: {BASE_DIR}")
    log(f"Log file: {LOG_FILE}")
    log("")

    # Phase 1: Scrape Ontario Fishes database
    log("PHASE 1: Scraping Ontario Freshwater Fishes Database")
    species_data = scrape_ontario_fish_species()
    log("")

    # Phase 2: Download PDF visual guides
    log("PHASE 2: Downloading Visual Identification Guides")
    pdf_guides = download_visual_guides()
    log("")

    # Phase 3: Extract text from PDFs
    log("PHASE 3: Extracting Text from PDFs")
    pdf_texts = extract_species_from_pdfs()
    log("")

    # Phase 4: Build RAG corpus
    log("PHASE 4: Building RAG Corpus")
    corpus = build_rag_corpus()
    log("")

    # Phase 5: Create quick reference
    log("PHASE 5: Creating Quick Reference Guide")
    quick_ref = create_quick_reference()
    log("")

    # Summary
    log("=" * 60)
    log("✓ RAG KNOWLEDGE BASE BUILD COMPLETE!")
    log("=" * 60)
    log(f"Location: {BASE_DIR}")
    log(f"Species: {corpus['metadata']['total_species']}")
    log(f"Images: {corpus['metadata']['total_images']}")
    log(f"PDF Guides: {len(pdf_guides)}")
    log("")
    log("NEXT STEPS:")
    log("1. Review corpus: cat /opt/d3kos/datasets/fish-rag/knowledge_base/fish_rag_corpus.json")
    log("2. Load into vector database (ChromaDB, FAISS, or Ollama embeddings)")
    log("3. Integrate with Phi-3.5 RAG system")
    log("4. Test species identification")
    log("")

    return 0

if __name__ == "__main__":
    sys.exit(main())
