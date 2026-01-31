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

FTS5_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS images_fts USING fts5(
    filename, category, keywords, objects, description,
    content='images',
    content_rowid='id'
);

CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
    file, links, text_snippet, keywords,
    content='notes',
    content_rowid='id'
);

-- Triggers to keep FTS tables in sync with main tables
CREATE TRIGGER IF NOT EXISTS images_ai AFTER INSERT ON images BEGIN
  INSERT INTO images_fts(rowid, filename, category, keywords, objects, description)
  VALUES (new.id, new.filename, new.category, new.keywords, new.objects, new.description);
END;

CREATE TRIGGER IF NOT EXISTS images_ad AFTER DELETE ON images BEGIN
  INSERT INTO images_fts(images_fts, rowid, filename, category, keywords, objects, description)
  VALUES('delete', old.id, old.filename, old.category, old.keywords, old.objects, old.description);
END;

CREATE TRIGGER IF NOT EXISTS images_au AFTER UPDATE ON images BEGIN
  INSERT INTO images_fts(images_fts, rowid, filename, category, keywords, objects, description)
  VALUES('delete', old.id, old.filename, old.category, old.keywords, old.objects, old.description);
  INSERT INTO images_fts(rowid, filename, category, keywords, objects, description)
  VALUES (new.id, new.filename, new.category, new.keywords, new.objects, new.description);
END;

CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
  INSERT INTO notes_fts(rowid, file, links, text_snippet, keywords)
  VALUES (new.id, new.file, new.links, new.text_snippet, new.keywords);
END;

CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
  INSERT INTO notes_fts(notes_fts, rowid, file, links, text_snippet, keywords)
  VALUES('delete', old.id, old.file, old.links, old.text_snippet, old.keywords);
END;

CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN
  INSERT INTO notes_fts(notes_fts, rowid, file, links, text_snippet, keywords)
  VALUES('delete', old.id, old.file, old.links, old.text_snippet, old.keywords);
  INSERT INTO notes_fts(rowid, file, links, text_snippet, keywords)
  VALUES (new.id, new.file, new.links, new.text_snippet, new.keywords);
END;
"""

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize database with both regular and FTS tables."""
    conn = get_conn()
    conn.executescript(SCHEMA)
    try:
        conn.executescript(FTS5_SCHEMA)
        print("✅ FTS5 full-text search enabled")
    except sqlite3.OperationalError as e:
        print(f"⚠️  FTS5 setup warning: {e}")
    conn.commit()
    conn.close()

def has_fts5():
    """Check if FTS5 tables exist and are populated."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM images_fts")
        count = cur.fetchone()[0]
        conn.close()
        return count > 0
    except sqlite3.OperationalError:
        conn.close()
        return False

def rebuild_fts5():
    """Rebuild FTS5 index from existing data."""
    conn = get_conn()
    cur = conn.cursor()
    
    print("Rebuilding FTS5 index from existing data...")
    
    try:
        # Drop and recreate FTS tables
        cur.execute("DROP TABLE IF EXISTS images_fts")
        cur.execute("DROP TABLE IF EXISTS notes_fts")
        cur.execute("DROP TRIGGER IF EXISTS images_ai")
        cur.execute("DROP TRIGGER IF EXISTS images_ad")
        cur.execute("DROP TRIGGER IF EXISTS images_au")
        cur.execute("DROP TRIGGER IF EXISTS notes_ai")
        cur.execute("DROP TRIGGER IF EXISTS notes_ad")
        cur.execute("DROP TRIGGER IF EXISTS notes_au")
        
        conn.executescript(FTS5_SCHEMA)
        
        # Populate images_fts
        cur.execute("""
            INSERT INTO images_fts(rowid, filename, category, keywords, objects, description)
            SELECT id, filename, category, 
                   COALESCE(keywords, ''), 
                   COALESCE(objects, ''), 
                   COALESCE(description, '')
            FROM images
        """)
        
        # Populate notes_fts
        cur.execute("""
            INSERT INTO notes_fts(rowid, file, links, text_snippet, keywords)
            SELECT id, file, 
                   COALESCE(links, ''), 
                   COALESCE(text_snippet, ''), 
                   COALESCE(keywords, '')
            FROM notes
        """)
        
        conn.commit()
        
        images_count = cur.execute("SELECT COUNT(*) FROM images_fts").fetchone()[0]
        notes_count = cur.execute("SELECT COUNT(*) FROM notes_fts").fetchone()[0]
        
        print(f"✅ FTS5 index rebuilt: {images_count} images, {notes_count} notes")
        
    except Exception as e:
        print(f"❌ Error rebuilding FTS5: {e}")
        conn.rollback()
    finally:
        conn.close()

def insert_image_record(filename, category, keywords, objects, colors, description, clip_embedding):
    """Insert image record (FTS triggers will auto-update FTS table)."""
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
