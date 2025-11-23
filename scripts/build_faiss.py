"""Build FAISS index for fast image similarity search."""

import sqlite3
import pickle
import numpy as np
import faiss
import os
import sys

# Ensure project root is on sys.path so this file can be run directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.config import DB_PATH, FAISS_INDEX_PATH, FAISS_IDS_PATH

def build_faiss():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, clip_embedding FROM images")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        print("No images to index in FAISS.")
        return

    ids = []
    vecs = []
    for _id, blob in rows:
        ids.append(_id)
        vecs.append(pickle.loads(blob))

    vecs = np.array(vecs).astype("float32")
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)
    faiss.write_index(index, FAISS_INDEX_PATH)

    with open(FAISS_IDS_PATH, "wb") as f:
        pickle.dump(ids, f)

    print(f"Built FAISS index for {len(ids)} images.")

if __name__ == "__main__":
    build_faiss()
