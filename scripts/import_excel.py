"""Import Excel links (Keep export) into notes table."""

import argparse
import ast
import sqlite3

import pandas as pd

from scripts.config import DB_PATH
from scripts.db_utils import init_db

def import_excel(path: str):
    df = pd.read_excel(path)
    req_cols = ["file", "links", "text_snippet"]
    for c in req_cols:
        if c not in df.columns:
            raise ValueError(f"Excel missing required column: {c}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for _, row in df.iterrows():
        file = str(row["file"])
        snippet = str(row["text_snippet"])
        links_raw = row["links"]
        links = None
        try:
            parsed = ast.literal_eval(links_raw)
            if isinstance(parsed, (list, tuple)):
                links = ", ".join(map(str, parsed))
            else:
                links = str(links_raw)
        except Exception:
            links = str(links_raw)
        keywords = (snippet.lower() + " " + links.lower())[:500]
        cur.execute(
            "INSERT INTO notes (file, links, text_snippet, keywords) VALUES (?, ?, ?, ?)",
            (file, links, snippet, keywords)
        )
    conn.commit()
    conn.close()
    print("Imported Excel into notes table.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel", required=True)
    args = parser.parse_args()
    init_db()
    import_excel(args.excel)

if __name__ == "__main__":
    main()
