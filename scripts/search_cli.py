"""CLI search for testing: text search and image similarity (FAISS)."""

import argparse
import sqlite3
import pickle
import numpy as np
import os
import faiss

from scripts.config import DB_PATH, FAISS_INDEX_PATH, FAISS_IDS_PATH
from scripts.clip_features import get_clip_embedding

def text_search(query: str, limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    q = f"%{query.lower()}%"
    cur.execute(
        """SELECT id, filename, category, keywords, objects, colors, description
               FROM images
               WHERE lower(keywords) LIKE ?
                  OR lower(objects) LIKE ?
                  OR lower(description) LIKE ?""", (q, q, q)
    )
    rows = cur.fetchall()
    conn.close()
    return rows[:limit]

def image_search_faiss(image_path: str, limit: int = 10):
    if not os.path.exists(FAISS_INDEX_PATH):
        raise SystemExit("FAISS index not found. Run build_faiss.py first.")
    emb = get_clip_embedding(image_path)
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(FAISS_IDS_PATH, "rb") as f:
        ids = pickle.load(f)
    D, I = index.search(emb.reshape(1, -1), limit)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    res = []
    for score, idx in zip(D[0], I[0]):
        img_id = ids[idx]
        cur.execute("SELECT filename, category, keywords, objects, colors, description FROM images WHERE id=?", (img_id,))
        row = cur.fetchone()
        if row:
            res.append((float(score), row))
    conn.close()
    return res

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["text", "image"], required=True)
    parser.add_argument("--query")
    parser.add_argument("--image")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    if args.mode == "text":
        if not args.query:
            raise SystemExit("Provide --query")
        rows = text_search(args.query, args.limit)
        for r in rows:
            print(r)
    else:
        if not args.image:
            raise SystemExit("Provide --image")
        rows = image_search_faiss(args.image, args.limit)
        for score, row in rows:
            print(score, row)

if __name__ == "__main__":
    main()
