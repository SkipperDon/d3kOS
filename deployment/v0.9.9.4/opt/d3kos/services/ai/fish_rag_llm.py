#!/usr/bin/env python3
"""
fish_rag_llm.py — On-demand Ollama LLM synthesizer for d3kOS RAG pipeline

Starts ollama serve on-demand (not a persistent service).
Uses phi3.5 to synthesize answers from retrieved document chunks.
Falls back gracefully — caller always handles None return.

Model unloads from RAM after OLLAMA_KEEP_ALIVE timeout (default 5 min).
ollama serve process stays alive at ~70 MB until Pi reboot (by design).
"""

import subprocess
import time
import urllib.request
import urllib.error
import json
import logging

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL    = "http://localhost:11434"
OLLAMA_MODEL       = "gemma3:1b"
OLLAMA_EMBED_MODEL = "nomic-embed-text"   # evicted from RAM before synthesis
OLLAMA_TIMEOUT     = 300   # seconds — allows for cold model load (~60s) + inference on Pi 4
STARTUP_TIMEOUT    = 15    # seconds to wait for ollama serve to become ready
STARTUP_POLL       = 1     # seconds between readiness checks

SYSTEM_PROMPT = (
    "You are the d3kOS marine assistant. "
    "Answer the user's question using ONLY the provided document excerpts. "
    "Be concise and practical. If the excerpts do not contain the answer, "
    "say so clearly in one sentence."
)


def _is_running() -> bool:
    """Return True if ollama serve is up and responding."""
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=3):
            return True
    except Exception:
        return False


def _start_serve() -> bool:
    """
    Launch ollama serve as a background subprocess.
    Returns True when the server is ready, False on timeout.
    """
    if _is_running():
        return True

    logger.info("fish_rag_llm: starting ollama serve on-demand")
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,   # detach from parent process group
        )
    except FileNotFoundError:
        logger.error("fish_rag_llm: ollama binary not found at /usr/local/bin/ollama")
        return False
    except Exception as e:
        logger.error(f"fish_rag_llm: failed to start ollama serve: {e}")
        return False

    # Poll until ready
    deadline = time.time() + STARTUP_TIMEOUT
    while time.time() < deadline:
        time.sleep(STARTUP_POLL)
        if _is_running():
            logger.info("fish_rag_llm: ollama serve is ready")
            return True

    logger.warning("fish_rag_llm: ollama serve did not become ready within timeout")
    return False


def _evict_model(model_name: str) -> None:
    """
    Ask Ollama to immediately unload a model from RAM (keep_alive=0).
    Called before loading the generation model to free RAM held by the
    embedding model (nomic-embed-text).  Silent no-op on any failure.
    """
    try:
        payload = {"model": model_name, "keep_alive": 0}
        data    = json.dumps(payload).encode("utf-8")
        req     = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10):
            logger.info(f"fish_rag_llm: evicted {model_name} from RAM")
    except Exception:
        pass   # eviction is best-effort — failure is not fatal


def synthesize(question: str, context_chunks: list[dict], model: str = OLLAMA_MODEL) -> str | None:
    """
    Synthesize an answer from retrieved RAG chunks using phi3.5.

    Args:
        question:       The user's question.
        context_chunks: List of dicts with 'content' and 'source' keys,
                        as returned by PDFProcessor.search().
        model:          Ollama model name (default: phi3.5).

    Returns:
        Synthesized answer string, or None if Ollama is unavailable or fails.
        Caller is responsible for fallback behaviour.
    """
    if not context_chunks:
        return None

    # Ensure ollama serve is running
    if not _start_serve():
        logger.warning("fish_rag_llm: ollama unavailable — skipping synthesis")
        return None

    # Evict embedding model from RAM before loading generation model.
    # nomic-embed-text + phi3.5 + d3kOS stack exceeds 8 GB simultaneously.
    _evict_model(OLLAMA_EMBED_MODEL)

    # Build context block from retrieved chunks
    context_parts = []
    for chunk in context_chunks:
        source  = chunk.get("source", "unknown")
        content = chunk.get("content", "").strip()
        if content:
            context_parts.append(f"[{source}]\n{content}")
    context_block = "\n\n".join(context_parts)

    prompt = (
        f"Document excerpts:\n\n"
        f"{context_block}\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )

    payload = {
        "model":  model,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": 0.2,   # low temp — factual, not creative
            "num_predict": 400,   # cap response length for Pi speed
        },
    }

    try:
        data    = json.dumps(payload).encode("utf-8")
        req     = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            result   = json.loads(resp.read().decode("utf-8"))
            response = result.get("response", "").strip()
            if response:
                logger.info(f"fish_rag_llm: synthesized {len(response)} chars via {model}")
                return response
    except urllib.error.URLError as e:
        logger.error(f"fish_rag_llm: HTTP error during synthesis: {e}")
    except TimeoutError:
        logger.warning(f"fish_rag_llm: inference timed out after {OLLAMA_TIMEOUT}s")
    except Exception as e:
        logger.error(f"fish_rag_llm: unexpected error: {e}")

    return None
