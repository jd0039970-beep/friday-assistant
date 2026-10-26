"""Simple SQLite + embedding memory store."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import numpy as np


class MemoryStore:
    def __init__(self, db_path: str):
        self.path = Path(db_path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, text TEXT, embedding BLOB, created_at TEXT)")
        self.conn.commit()

    def add(self, text: str, embedding: list[float] | None = None):
        emb = json.dumps(embedding) if embedding else None
        self.conn.execute("INSERT INTO memories (text, embedding, created_at) VALUES (?, ?, datetime('now'))", (text, emb))
        self.conn.commit()

    def search(self, query_emb: list[float], k: int = 6) -> list[str]:
        rows = self.conn.execute("SELECT text, embedding FROM memories WHERE embedding IS NOT NULL").fetchall()
        if not rows:
            return []
        q = np.array(query_emb, dtype=np.float32)
        scored = []
        for text, emb_json in rows:
            try:
                e = np.array(json.loads(emb_json), dtype=np.float32)
                score = float(np.dot(q, e) / (np.linalg.norm(q) * np.linalg.norm(e) + 1e-9))
                scored.append((score, text))
            except Exception:
                continue
        scored.sort(reverse=True)
        return [t for _, t in scored[:k]]
