#!/bin/bash
# install-ollama.sh — Install Ollama and pull d3kOS local AI models
#
# Run this after first boot if you want local AI features (Helm Assistant RAG,
# offline AI navigation). Requires internet access. Downloads ~2 GB.
#
# Usage: sudo /opt/d3kos/scripts/install-ollama.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"; }
error(){ echo -e "${RED}[ERROR]${NC} $1" >&2; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

log "=================================================="
log "d3kOS Ollama Installer"
log "=================================================="
log ""
log "This installs Ollama and downloads the following models:"
log "  • gemma3:1b          (~800 MB) — Helm Assistant local AI"
log "  • nomic-embed-text   (~270 MB) — RAG document embeddings"
log ""
warn "Requires internet access and ~2 GB of free disk space."
log ""

# Check disk space (need at least 3 GB free)
FREE_KB=$(df /home/d3kos --output=avail | tail -1)
FREE_GB=$((FREE_KB / 1024 / 1024))
if [ "$FREE_GB" -lt 3 ]; then
    error "Only ${FREE_GB} GB free. Need at least 3 GB. Aborting."
    exit 1
fi
log "Disk space: ${FREE_GB} GB free — OK"

# Check internet
if ! curl -s --max-time 5 https://ollama.com > /dev/null 2>&1; then
    error "No internet access. Connect to WiFi or Ethernet and retry."
    exit 1
fi
log "Internet: reachable — OK"

# ==============================================================================
# STEP 1: Install Ollama if not present
# ==============================================================================

log ""
log "STEP 1: Checking Ollama installation..."

if command -v ollama &>/dev/null; then
    OLLAMA_VER=$(ollama --version 2>/dev/null | head -1 || echo "unknown")
    log "  Ollama already installed: $OLLAMA_VER"
else
    log "  Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    log "  Ollama installed"
fi

# Ensure service is running
systemctl enable ollama 2>/dev/null || true
systemctl start ollama  2>/dev/null || true

# Wait for Ollama API to be ready (up to 30s)
log "  Waiting for Ollama API..."
for i in $(seq 1 30); do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        log "  Ollama API ready"
        break
    fi
    sleep 1
    if [ "$i" -eq 30 ]; then
        error "Ollama API did not start within 30 seconds."
        exit 1
    fi
done

# ==============================================================================
# STEP 2: Pull models
# ==============================================================================

log ""
log "STEP 2: Pulling models (this will take several minutes)..."

log "  Pulling gemma3:1b..."
ollama pull gemma3:1b

log "  Pulling nomic-embed-text..."
ollama pull nomic-embed-text

# ==============================================================================
# STEP 3: Verify
# ==============================================================================

log ""
log "STEP 3: Verifying..."

MODELS=$(ollama list 2>/dev/null || echo "")

if echo "$MODELS" | grep -q "gemma3:1b"; then
    log "  ✓ gemma3:1b present"
else
    error "gemma3:1b not found after pull — check Ollama logs: journalctl -u ollama -n 50"
    exit 1
fi

if echo "$MODELS" | grep -q "nomic-embed-text"; then
    log "  ✓ nomic-embed-text present"
else
    error "nomic-embed-text not found after pull — check Ollama logs: journalctl -u ollama -n 50"
    exit 1
fi

# ==============================================================================
# Done
# ==============================================================================

log ""
log "=================================================="
log "✓ Ollama installation complete!"
log "=================================================="
log ""
log "Local AI is now available:"
log "  • Helm Assistant local mode: http://<pi-ip>:3000/helm-assistant"
log "  • RAG document ingestion: re-upload your boat manuals via the dashboard"
log ""
log "Ollama API: http://localhost:11434"
log "Service: systemctl status ollama"
log ""
