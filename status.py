#!/usr/bin/env python3
"""
Status dashboard for Interior Inspiration Engine.
Shows statistics about your collection.

Usage:
    python status.py
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Add project root to path
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.config import DB_PATH, IMAGES_DIR


def format_bytes(bytes_val):
    """Format bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB"


def get_database_stats():
    """Get statistics from the database."""
    if not os.path.exists(DB_PATH):
        return None
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    stats = {}
    
    # Image count
    cur.execute("SELECT COUNT(*) FROM images")
    stats['image_count'] = cur.fetchone()[0]
    
    # Notes count
    try:
        cur.execute("SELECT COUNT(*) FROM notes")
        stats['notes_count'] = cur.fetchone()[0]
    except:
        stats['notes_count'] = 0
    
    # Categories
    cur.execute("SELECT category, COUNT(*) FROM images GROUP BY category ORDER BY COUNT(*) DESC LIMIT 5")
    stats['top_categories'] = cur.fetchall()
    
    # Most recent additions (if there's a timestamp column)
    try:
        cur.execute("SELECT filename FROM images ORDER BY id DESC LIMIT 5")
        stats['recent_images'] = [row[0] for row in cur.fetchall()]
    except:
        stats['recent_images'] = []
    
    conn.close()
    
    # Database size
    stats['db_size'] = os.path.getsize(DB_PATH)
    
    return stats


def get_images_stats():
    """Get statistics from the images directory."""
    if not os. path.exists(IMAGES_DIR):
        return None
    
    stats = {}
    
    # Count by extension
    extensions = {}
    total_size = 0
    
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
        files = list(Path(IMAGES_DIR).glob(ext))
        if files:
            ext_name = ext[1:]  # Remove *
            extensions[ext_name] = len(files)
            total_size += sum(f.stat().st_size for f in files)
    
    stats['extensions'] = extensions
    stats['total_size'] = total_size
    stats['total_count'] = sum(extensions.values())
    
    return stats


def get_faiss_stats():
    """Get FAISS index statistics."""
    from scripts.config import FAISS_INDEX_PATH, FAISS_IDS_PATH
    
    stats = {}
    
    if os.path.exists(FAISS_INDEX_PATH):
        stats['index_exists'] = True
        stats['index_size'] = os.path.getsize(FAISS_INDEX_PATH)
        
        # Try to load and get vector count
        try:
            import faiss
            index = faiss.read_index(FAISS_INDEX_PATH)
            stats['vector_count'] = index.ntotal
        except:
            stats['vector_count'] = 'Unknown'
    else:
        stats['index_exists'] = False
    
    return stats


def print_status():
    """Print the status dashboard."""
    print("="*70)
    print("🏠 Interior Inspiration Engine - Status Dashboard")
    print("="*70)
    print()
    
    # Database Stats
    print("📊 DATABASE")
    print("-"*70)
    db_stats = get_database_stats()
    
    if db_stats:
        print(f"  Images indexed:      {db_stats['image_count']:,}")
        print(f"  Keep notes:          {db_stats['notes_count']:,}")
        print(f"  Database size:       {format_bytes(db_stats['db_size'])}")
        
        if db_stats['top_categories']:
            print(f"\n  Top categories:")
            for cat, count in db_stats['top_categories']:
                print(f"    - {cat}: {count}")
        
        if db_stats['recent_images']:
            print(f"\n  Recent additions:")
            for img in db_stats['recent_images'][:3]:
                print(f"    - {img}")
    else:
        print("  ❌ Database not found")
        print(f"     Expected at: {DB_PATH}")
    
    print()
    
    # Images Stats
    print("🖼️  IMAGES")
    print("-"*70)
    img_stats = get_images_stats()
    
    if img_stats and img_stats['total_count'] > 0:
        print(f"  Total images:        {img_stats['total_count']:,}")
        print(f"  Total size:          {format_bytes(img_stats['total_size'])}")
        print(f"  Average size:        {format_bytes(img_stats['total_size'] / img_stats['total_count'])}")
        
        print(f"\n  By format:")
        for ext, count in img_stats['extensions'].items():
            print(f"    - {ext}: {count:,}")
    else:
        print("  ❌ No images found")
        print(f"     Expected in: {IMAGES_DIR}")
    
    print()
    
    # FAISS Index Stats
    print("🔍 SEARCH INDEX")
    print("-"*70)
    faiss_stats = get_faiss_stats()
    
    if faiss_stats['index_exists']:
        print(f"  ✅ FAISS index ready")
        print(f"  Index size:          {format_bytes(faiss_stats['index_size'])}")
        print(f"  Vectors indexed:     {faiss_stats['vector_count']}")
    else:
        print(f"  ❌ FAISS index not built")
        print(f"     Run: python scripts/build_faiss.py")
    
    print()
    
    # FTS5 Stats
    print("⚡ FULL-TEXT SEARCH")
    print("-"*70)
    
    if db_stats:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM images_fts")
            fts_count = cur.fetchone()[0]
            print(f"  ✅ FTS5 enabled")
            print(f"  Indexed entries:     {fts_count:,}")
        except:
            print(f"  ❌ FTS5 not enabled")
            print(f"     Run: python setup_fts5.py")
        conn.close()
    
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS")
    print("-"*70)
    
    recommendations = []
    
    if not db_stats or db_stats['image_count'] == 0:
        recommendations.append("Run: python update_pipeline.py (to index images)")
    
    if img_stats and '.png' in img_stats['extensions'] and img_stats['extensions']['.png'] > 10:
        recommendations.append("Run: python optimize_storage.py (save storage with WebP)")
    
    if not faiss_stats['index_exists']:
        recommendations.append("Run: python scripts/build_faiss.py (enable image search)")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    else:
        print("  ✅ All systems operational!")
    
    print()
    print("="*70)
    print()


if __name__ == "__main__":
    try:
        print_status()
    except Exception as e:
        print(f"❌ Error generating status: {e}")
        sys.exit(1)
