"""Index all images in a folder into SQLite DB."""

import argparse
import os
import sys
from glob import glob

# Ensure project root is on sys.path so `python scripts/index_images.py` works
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.clip_features import get_clip_embedding
from scripts.yolo_features import detect_objects
from scripts.color_features import extract_colors
from scripts.keyword_extractor import extract_keywords
from scripts.db_utils import init_db, insert_image_record

def index_images(image_dir: str):
    exts = ("*.jpg", "*.jpeg", "*.png")
    paths = []
    for e in exts:
        paths.extend(glob(os.path.join(image_dir, e)))
    if not paths:
        print("No images found in", image_dir)
        return
    init_db()
    for p in sorted(paths):
        print("Indexing:", p)
        emb = get_clip_embedding(p)
        objs = detect_objects(p)
        colors = extract_colors(p)
        desc = f"objects: {', '.join(objs)}"
        base = os.path.basename(p)
        text = base.lower() + " " + desc.lower()
        kw = extract_keywords(text, top_n=12)
        insert_image_record(
            filename=base,
            category="unknown",
            keywords=kw,
            objects=objs,
            colors=colors,
            description=desc,
            clip_embedding=emb,
        )
    print("Indexing complete.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir", default="images")
    args = parser.parse_args()
    index_images(args.image_dir)

if __name__ == "__main__":
    main()
