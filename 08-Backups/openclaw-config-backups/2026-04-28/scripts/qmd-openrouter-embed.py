#!/usr/bin/env python3
"""
DEPRECATED: QMD OpenRouter Embedding Script v2

Reason:
- QMD native embeddings are now the preferred path.
- External OpenRouter embedding bypass adds schema/runtime complexity.
- Keep only for historical reference or explicit one-off recovery work.

Do not use as the default QMD embedding pipeline.
"""

import sqlite3
import json
import time
import struct
from datetime import datetime, timezone
from typing import List, Tuple, Optional

# Config
QMD_DB = "/home/piet/.cache/qmd/index.sqlite"
VEC0_PATH = "/home/piet/.openclaw/workspace/node_modules/sqlite-vec-linux-x64/vec0.so"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "openai/text-embedding-3-small"
EMBEDDING_DIMENSIONS = 768
BATCH_SIZE = 100
CHUNK_SIZE = 900
CHUNK_OVERLAP = 0.15


def load_openrouter_key() -> str:
    with open("/home/piet/.openclaw/openclaw.json") as f:
        config = json.load(f)
    providers = config.get("models", {}).get("providers", {})
    for name, prov in providers.items():
        if name == "openrouter":
            return prov.get("apiKey", "")
    return ""


def get_pending_docs(conn) -> List:
    cur = conn.cursor()
    cur.execute("""
        SELECT d.hash, d.id, d.collection, d.path, c.doc
        FROM documents d
        JOIN content c ON d.hash = c.hash
        WHERE d.hash NOT IN (SELECT DISTINCT hash FROM content_vectors)
    """)
    return cur.fetchall()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: float = CHUNK_OVERLAP) -> List[Tuple[str, int]]:
    words = text.split()
    step = int(chunk_size * (1 - overlap))
    chunks = []
    for i in range(0, len(words), step):
        chunk_words = words[i:i + chunk_size]
        if len(chunk_words) < 10:
            continue
        chunk_text_str = " ".join(chunk_words)
        char_pos = len(" ".join(words[:i]))
        chunks.append((chunk_text_str, char_pos))
    return chunks


def embed_chunks_batch(chunks: List[str], api_key: str) -> Optional[List]:
    import urllib.request
    import urllib.error

    url = f"{OPENROUTER_BASE_URL}/embeddings"
    data = {"model": MODEL, "input": chunks, "dimensions": EMBEDDING_DIMENSIONS}

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openclaw.ai",
            "X-Title": "OpenClaw QMD Embedding"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return [item["embedding"] for item in result["data"]]
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"  HTTP Error {e.code}: {body[:200]}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def write_all_vectors(conn, hash_val: str, chunks_with_emb: List[Tuple[str, int, List[float]]], model: str):
    """Write to both content_vectors AND vectors_vec."""
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    for seq, (text, pos, embedding) in enumerate(chunks_with_emb):
        # Write content_vectors metadata
        cur.execute("""
            INSERT OR REPLACE INTO content_vectors (hash, seq, pos, model, embedded_at)
            VALUES (?, ?, ?, ?, ?)
        """, (hash_val, seq, pos, model, now))

        # Write to vectors_vec — vec0 format: hash_seq, embedding (blob)
        hash_seq = f"{hash_val}_{seq}"
        embedding_bytes = struct.pack(f"<{len(embedding)}f", *embedding)

        cur.execute("""
            INSERT OR REPLACE INTO vectors_vec (hash_seq, embedding)
            VALUES (?, ?)
        """, (hash_seq, embedding_bytes))

    conn.commit()


def main():
    print("QMD OpenRouter Embedding Script v2 (with vec0)")
    print("=" * 50)

    api_key = load_openrouter_key()
    if not api_key:
        print("ERROR: Could not load OpenRouter API key")
        return 1

    # Connect with vec0 extension loaded
    conn = sqlite3.connect(QMD_DB)
    conn.enable_load_extension(True)
    conn.execute(f"SELECT load_extension('{VEC0_PATH}')")

    print(f"Key: {api_key[:15]}...")
    print(f"Model: {MODEL} ({EMBEDDING_DIMENSIONS}d)")
    print(f"DB: {QMD_DB}")
    print(f"vec0: {VEC0_PATH}")
    print()

    pending = get_pending_docs(conn)
    print(f"Documents needing embedding: {len(pending)}")

    if not pending:
        print("Nothing to do!")
        return 0

    total_chunks = 0
    errors = 0

    for doc_hash, doc_id, collection, path, doc_text in pending:
        print(f"\n[{doc_id}] {collection}/{path}")
        print(f"  Text: {len(doc_text)} chars")

        chunks = chunk_text(doc_text)
        print(f"  Chunks: {len(chunks)}")

        if not chunks:
            continue

        all_embeddings = []
        for i in range(0, len(chunks), BATCH_SIZE):
            batch_texts = [c[0] for c in chunks[i:i+BATCH_SIZE]]
            print(f"  Batch {i//BATCH_SIZE + 1}: {len(batch_texts)} chunks...", end=" ", flush=True)

            embeddings = embed_chunks_batch(batch_texts, api_key)
            if embeddings is None:
                print("FAILED")
                errors += 1
                break

            print(f"OK ({len(embeddings)})")
            for (text, pos), emb in zip(chunks[i:i+BATCH_SIZE], embeddings):
                all_embeddings.append((text, pos, emb))
            time.sleep(0.05)

        if len(all_embeddings) != len(chunks):
            continue

        try:
            write_all_vectors(conn, doc_hash, all_embeddings, f"openrouter/{MODEL}")
            print(f"  Written ✅")
            total_chunks += len(all_embeddings)
        except Exception as e:
            print(f"  DB error: {e}")
            conn.rollback()
            errors += 1

    conn.close()

    print()
    print("=" * 50)
    print(f"Done! {total_chunks} chunks in {len(pending) - errors} docs.")
    if errors:
        print(f"Errors: {errors}")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
