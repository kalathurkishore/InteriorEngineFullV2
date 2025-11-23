import sqlite3
import pickle
import os
from scripts.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    category TEXT,
    keywords TEXT,
    objects TEXT,
    colors TEXT,
    description TEXT,
    clip_embedding BLOB
);
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file TEXT,
    links TEXT,
    text_snippet TEXT,
    keywords TEXT
);
"""

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

def insert_image_record(filename, category, keywords, objects, colors, description, clip_embedding):
    conn = get_conn()
    cur = conn.cursor()

    color_hex = ",".join([f"#{r:02x}{g:02x}{b:02x}" for r, g, b in colors])
    kw_str = ", ".join(keywords)
    obj_str = ", ".join(objects)
    emb_blob = pickle.dumps(clip_embedding)

    cur.execute(
        "INSERT INTO images (filename, category, keywords, objects, colors, description, clip_embedding) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (filename, category, kw_str, obj_str, color_hex, description, emb_blob)
    )
    conn.commit()
    conn.close()
