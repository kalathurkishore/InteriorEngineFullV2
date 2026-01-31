#!/usr/bin/env python3
"""
Automated Google Takeout processor for Interior Inspiration Engine.
Automatically detects, extracts, and processes new Google Keep takeout exports.

Usage:
    # Just download the takeout zip to InteriorEngineFinalComplete/ and run:
    python process_takeout.py
    
    # Or specify the zip file:
    python process_takeout.py --zip takeout-20260131T160657Z-3-001.zip
    
    # Auto-mode (no prompts):
    python process_takeout.py --auto
"""

import os
import sys
import zipfile
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import glob


class TakeoutProcessor:
    def __init__(self, base_dir, auto_mode=False):
        self.base_dir = Path(base_dir)
        self.auto_mode = auto_mode
        self.takeout_dir = None
        self.keep_dir = None
        
    def find_latest_takeout_zip(self):
        """Find the most recent takeout zip file."""
        pattern = str(self.base_dir / "takeout-*.zip")
        zips = glob.glob(pattern)
        
        if not zips:
            print("❌ No takeout zip files found in", self.base_dir)
            print(f"\nPlease download Google Takeout and place the .zip file in:")
            print(f"  {self.base_dir}/\n")
            return None
        
        # Sort by modification time, newest first
        zips.sort(key=os.path.getmtime, reverse=True)
        latest = zips[0]
        
        print(f"✅ Found takeout zip: {Path(latest).name}")
        
        if len(zips) > 1:
            print(f"\nℹ️  Note: {len(zips)} takeout zips found, using the newest one")
            print(f"   To use a different file, run: python process_takeout.py --zip <filename>")
        
        return Path(latest)
    
    def extract_zip(self, zip_path):
        """Extract the takeout zip file."""
        print(f"\n📦 Extracting {zip_path.name}...")
        
        # Create extraction directory
        extract_dir = self.base_dir / zip_path.stem
        
        if extract_dir.exists():
            if not self.auto_mode:
                response = input(f"\n⚠️  Directory {extract_dir.name} already exists. Overwrite? [y/N]: ").strip().lower()
                if response != 'y':
                    print("Using existing extraction...")
                    self.takeout_dir = extract_dir
                    return True
            
            print(f"Removing old extraction: {extract_dir.name}")
            shutil.rmtree(extract_dir)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            print(f"✅ Extracted to: {extract_dir.name}")
            self.takeout_dir = extract_dir
            return True
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False
    
    def find_keep_folder(self):
        """Find the Keep folder within the extracted takeout."""
        if not self.takeout_dir:
            return False
        
        # Common paths in takeout structure
        possible_paths = [
            self.takeout_dir / "Takeout" / "Keep",
            self.takeout_dir / "Keep",
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                # Verify it has Keep notes
                files = list(path.glob("*.json")) + list(path.glob("*.html"))
                if files:
                    print(f"✅ Found Keep notes: {len(files)} files in {path.relative_to(self.base_dir)}")
                    self.keep_dir = path
                    return True
        
        print("❌ Could not find Keep folder in takeout")
        print(f"\nSearched in:")
        for p in possible_paths:
            print(f"  - {p}")
        return False
    
    def update_conversion_script(self):
        """Update keep-notes-to-excel-conv.py with the new Keep folder path."""
        script_path = self.base_dir / "keep-notes-to-excel-conv.py"
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return False
        
        print(f"\n📝 Updating conversion script with new path...")
        
        try:
            # Read the script
            with open(script_path, 'r') as f:
                content = f.read()
            
            # Find and replace the folder_path line
            import re
            
            # Pattern to match: folder_path = r"..." or folder_path = "..."
            pattern = r'folder_path\s*=\s*r?"([^"]+)"'
            new_path_str = str(self.keep_dir).replace('\\', '/')
            replacement = f'folder_path = r"{new_path_str}"'
            
            # Check if pattern exists
            if not re.search(pattern, content):
                print("⚠️  Could not find folder_path in script")
                print(f"\nPlease manually update line 74 in {script_path.name} to:")
                print(f'  folder_path = r"{new_path_str}"')
                return False
            
            new_content = re.sub(pattern, replacement, content)
            
            # Write back
            with open(script_path, 'w') as f:
                f.write(new_content)
            
            print(f"✅ Updated script with path: {new_path_str}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update script: {e}")
            return False
    
    def convert_to_excel(self):
        """Run the keep-notes-to-excel conversion."""
        print(f"\n🔄 Converting Keep notes to Excel...")
        
        script_path = self.base_dir / "keep-notes-to-excel-conv.py"
        
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(result.stdout)
                print("✅ Conversion complete")
                return True
            else:
                print("❌ Conversion failed")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error running conversion: {e}")
            return False
    
    def cleanup_old_takeouts(self, keep_latest=2):
        """Clean up old takeout folders and zips."""
        print(f"\n🧹 Cleaning up old takeout files...")
        
        # Find all takeout directories
        takeout_dirs = list(self.base_dir.glob("takeout-*"))
        takeout_dirs = [d for d in takeout_dirs if d.is_dir()]
        
        # Find all takeout zips
        takeout_zips = list(self.base_dir.glob("takeout-*.zip"))
        
        if not takeout_dirs and not takeout_zips:
            print("  No old takeouts to clean up")
            return
        
        # Sort by modification time
        takeout_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        takeout_zips.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Keep only the N most recent
        old_dirs = takeout_dirs[keep_latest:]
        old_zips = takeout_zips[keep_latest:]
        
        if not old_dirs and not old_zips:
            print(f"  Keeping {len(takeout_dirs)} most recent takeouts")
            return
        
        total_size = 0
        
        # Remove old directories
        for old_dir in old_dirs:
            size = sum(f.stat().st_size for f in old_dir.rglob('*') if f.is_file())
            total_size += size
            shutil.rmtree(old_dir)
            print(f"  ✅ Removed: {old_dir.name} ({self.format_bytes(size)})")
        
        # Remove old zips
        for old_zip in old_zips:
            size = old_zip.stat().st_size
            total_size += size
            old_zip.unlink()
            print(f"  ✅ Removed: {old_zip.name} ({self.format_bytes(size)})")
        
        if total_size > 0:
            print(f"\n  Freed up: {self.format_bytes(total_size)}")
    
    def format_bytes(self, bytes_val):
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} TB"
    
    def process(self, zip_path=None):
        """Main processing pipeline."""
        print("="*60)
        print("🏠 Google Takeout Auto-Processor")
        print("="*60)
        print()
        
        # Step 1: Find or use specified zip
        if zip_path:
            zip_file = self.base_dir / zip_path
            if not zip_file.exists():
                print(f"❌ Specified zip not found: {zip_path}")
                return False
        else:
            zip_file = self.find_latest_takeout_zip()
            if not zip_file:
                return False
        
        # Step 2: Extract
        if not self.extract_zip(zip_file):
            return False
        
        # Step 3: Find Keep folder
        if not self.find_keep_folder():
            return False
        
        # Step 4: Update conversion script
        if not self.update_conversion_script():
            return False
        
        # Step 5: Convert to Excel
        if not self.convert_to_excel():
            return False
        
        # Step 6: Cleanup (optional)
        if not self.auto_mode:
            response = input("\n🧹 Clean up old takeout files? [Y/n]: ").strip().lower()
            if response != 'n':
                self.cleanup_old_takeouts()
        else:
            self.cleanup_old_takeouts()
        
        print("\n" + "="*60)
        print("✅ TAKEOUT PROCESSING COMPLETE")
        print("="*60)
        print()
        print("Next steps:")
        print("  1. Run: python update_db_and_index.py")
        print("  2. Or run the full pipeline: python update_pipeline.py")
        print()
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Automated Google Takeout processor for Interior Inspiration Engine"
    )
    parser.add_argument(
        "--zip",
        type=str,
        help="Specific takeout zip file to process"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run without interactive prompts"
    )
    
    args = parser.parse_args()
    
    # Get base directory
    base_dir = Path(__file__).parent.absolute()
    
    # Create processor
    processor = TakeoutProcessor(base_dir, auto_mode=args.auto)
    
    # Process
    success = processor.process(zip_path=args.zip)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
