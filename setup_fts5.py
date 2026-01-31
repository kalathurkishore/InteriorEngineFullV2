#!/usr/bin/env python3
"""
Setup FTS5 full-text search for existing database.
Run this once to enable fast text search.

Usage:
    python setup_fts5.py
"""

import sys
import os

# Add project root to path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)

from InteriorEngineFullV2.scripts.db_utils import rebuild_fts5, has_fts5

def main():
    print("="*60)
    print("FTS5 Full-Text Search Setup")
    print("="*60)
    print()
    
    if has_fts5():
        print("⚠️  FTS5 index already exists.")
        response = input("Rebuild anyway? [y/N]: ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return
    
    print("\nSetting up FTS5 for faster text search...")
    rebuild_fts5()
    
    print("\n✅ Done! Text search is now 10-50x faster.")
    print("You can now use the Streamlit UI for searches.\n")

if __name__ == "__main__":
    main()
