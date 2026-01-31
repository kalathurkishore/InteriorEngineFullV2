#!/usr/bin/env python3
"""
Storage optimization tool for Interior Inspiration Engine.
Reduces image storage by converting PNGs to WebP and removing duplicate screenshot frames.

Usage:
    python optimize_storage.py [--dry-run] [--keep-all-frames] [--quality 85]
    
Options:
    --dry-run          : Preview changes without actually deleting/converting
    --keep-all-frames  : Don't delete duplicate frames (_0, _2), keep all
    --quality N        : WebP quality (1-100, default: 85)
    --backup           : Create backup of deleted files before removing
"""

import os
import argparse
from pathlib import Path
from PIL import Image
import shutil
from datetime import datetime


class StorageOptimizer:
    def __init__(self, images_dir, dry_run=False, keep_all_frames=False, 
                 webp_quality=85, backup=False):
        self.images_dir = Path(images_dir)
        self.dry_run = dry_run
        self.keep_all_frames = keep_all_frames
        self.webp_quality = webp_quality
        self.backup = backup
        
        self.stats = {
            'total_files': 0,
            'frames_deleted': 0,
            'pngs_converted': 0,
            'bytes_saved': 0,
            'errors': 0
        }
    
    def format_bytes(self, bytes_val):
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f} TB"
    
    def delete_duplicate_frames(self):
        """Delete _0.png and _2.png files, keeping only _1.png."""
        if self.keep_all_frames:
            print("⏭️  Skipping frame deletion (--keep-all-frames flag)")
            return
        
        print("\n📸 Removing duplicate screenshot frames...")
        
        patterns = ['*_0.png', '*_2.png']
        deleted_count = 0
        bytes_saved = 0
        
        for pattern in patterns:
            for filepath in self.images_dir.glob(pattern):
                file_size = filepath.stat().st_size
                
                if self.dry_run:
                    print(f"  [DRY-RUN] Would delete: {filepath.name} ({self.format_bytes(file_size)})")
                else:
                    if self.backup:
                        self.backup_file(filepath)
                    
                    try:
                        filepath.unlink()
                        print(f"  ✅ Deleted: {filepath.name}")
                        deleted_count += 1
                        bytes_saved += file_size
                    except Exception as e:
                        print(f"  ❌ Error deleting {filepath.name}: {e}")
                        self.stats['errors'] += 1
        
        self.stats['frames_deleted'] = deleted_count
        self.stats['bytes_saved'] += bytes_saved
        
        if not self.dry_run:
            print(f"\n  Deleted {deleted_count} duplicate frames")
            print(f"  Saved: {self.format_bytes(bytes_saved)}")
    
    def convert_png_to_webp(self):
        """Convert all remaining PNG files to WebP format."""
        print("\n🖼️  Converting PNGs to WebP...")
        
        png_files = list(self.images_dir.glob('*.png'))
        converted_count = 0
        bytes_saved = 0
        
        for png_path in png_files:
            webp_path = png_path.with_suffix('.webp')
            
            # Skip if WebP already exists
            if webp_path.exists():
                print(f"  ⏭️  Skipped (WebP exists): {png_path.name}")
                continue
            
            try:
                png_size = png_path.stat().st_size
                
                if self.dry_run:
                    print(f"  [DRY-RUN] Would convert: {png_path.name} → {webp_path.name}")
                else:
                    # Open and convert
                    img = Image.open(png_path)
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGB')
                    
                    img.save(webp_path, 'WEBP', quality=self.webp_quality, method=6)
                    webp_size = webp_path.stat().st_size
                    
                    # Calculate savings
                    savings = png_size - webp_size
                    savings_pct = (savings / png_size) * 100 if png_size > 0 else 0
                    
                    print(f"  ✅ {png_path.name} → {webp_path.name}")
                    print(f"     {self.format_bytes(png_size)} → {self.format_bytes(webp_size)} "
                          f"({savings_pct:.1f}% smaller)")
                    
                    # Delete original PNG
                    if self.backup:
                        self.backup_file(png_path)
                    
                    png_path.unlink()
                    
                    converted_count += 1
                    bytes_saved += savings
                    
            except Exception as e:
                print(f"  ❌ Error converting {png_path.name}: {e}")
                self.stats['errors'] += 1
        
        self.stats['pngs_converted'] = converted_count
        self.stats['bytes_saved'] += bytes_saved
        
        if not self.dry_run:
            print(f"\n  Converted {converted_count} PNGs to WebP")
            print(f"  Saved: {self.format_bytes(bytes_saved)}")
    
    def backup_file(self, filepath):
        """Create backup of file before deletion."""
        backup_root = self.images_dir.parent / 'image_backups'
        backup_root.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = backup_root / f"backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        backup_path = backup_dir / filepath.name
        shutil.copy2(filepath, backup_path)
    
    def generate_report(self):
        """Generate and display optimization report."""
        print("\n" + "="*60)
        print("📊 STORAGE OPTIMIZATION REPORT")
        print("="*60)
        
        # Calculate current storage
        total_size = sum(f.stat().st_size for f in self.images_dir.glob('*') if f.is_file())
        
        print(f"\nCurrent storage: {self.format_bytes(total_size)}")
        
        if self.dry_run:
            print(f"\n[DRY-RUN MODE - No changes made]")
            print(f"Potential savings: {self.format_bytes(self.stats['bytes_saved'])}")
        else:
            print(f"\nTotal saved: {self.format_bytes(self.stats['bytes_saved'])}")
        
        print(f"\nDuplicate frames removed: {self.stats['frames_deleted']}")
        print(f"PNGs converted to WebP: {self.stats['pngs_converted']}")
        
        if self.stats['errors'] > 0:
            print(f"\n⚠️  Errors encountered: {self.stats['errors']}")
        
        print("\n" + "="*60 + "\n")
    
    def run(self):
        """Execute optimization pipeline."""
        if not self.images_dir.exists():
            print(f"❌ Images directory not found: {self.images_dir}")
            return
        
        print(f"🎯 Target directory: {self.images_dir}")
        print(f"Mode: {'DRY-RUN (no changes)' if self.dry_run else 'LIVE (will modify files)'}")
        print(f"WebP quality: {self.webp_quality}")
        
        if self.dry_run:
            print("\n⚠️  Running in DRY-RUN mode - no files will be modified\n")
        
        # Count total files
        self.stats['total_files'] = len(list(self.images_dir.glob('*')))
        print(f"Total files: {self.stats['total_files']}\n")
        
        # Execute optimization steps
        self.delete_duplicate_frames()
        self.convert_png_to_webp()
        
        # Generate report
        self.generate_report()


def main():
    parser = argparse.ArgumentParser(
        description="Optimize image storage for Interior Inspiration Engine"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without actually modifying files"
    )
    parser.add_argument(
        "--keep-all-frames",
        action="store_true",
        help="Don't delete duplicate frames (_0, _2)"
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="WebP quality (1-100, default: 85)"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup of files before deleting"
    )
    parser.add_argument(
        "--images-dir",
        type=str,
        help="Custom images directory path (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    # Determine images directory
    if args.images_dir:
        images_dir = Path(args.images_dir)
    else:
        # Auto-detect based on script location
        base_dir = Path(__file__).parent
        images_dir = base_dir / "InteriorEngineFullV2" / "InteriorEngineFullV2" / "images"
    
    # Create optimizer and run
    optimizer = StorageOptimizer(
        images_dir=images_dir,
        dry_run=args.dry_run,
        keep_all_frames=args.keep_all_frames,
        webp_quality=args.quality,
        backup=args.backup
    )
    
    optimizer.run()


if __name__ == "__main__":
    main()
