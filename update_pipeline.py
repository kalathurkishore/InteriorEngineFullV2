#!/usr/bin/env python3
"""
Automated update pipeline for Interior Inspiration Engine.
Streamlines the Keep notes → database update workflow into a single command.

Usage:
    python update_pipeline.py [--auto] [--skip-tagging] [--skip-git]
    
Options:
    --auto          : Run without interactive prompts (use defaults)
    --skip-tagging  : Skip the auto-tagging step (faster if no new images)
    --skip-git      : Don't commit to git
"""

import subprocess
import shutil
import os
import sys
from datetime import datetime
from pathlib import Path
import argparse

# Color output for better readability
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(msg):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{msg:^60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_step(step_num, msg):
    print(f"{Colors.BLUE}{Colors.BOLD}[Step {step_num}]{Colors.END} {msg}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def run_command(cmd, cwd=None, description=""):
    """Run a command and handle errors."""
    try:
        print(f"  Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            check=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(f"  {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed!")
        if e.stderr:
            print(f"  Error: {e.stderr}")
        return False

def backup_database(base_dir):
    """Create a timestamped backup of the database."""
    print_step(1, "Creating database backup...")
    
    db_dir = base_dir / "InteriorEngineFullV2" / "InteriorEngineFullV2" / "db"
    backup_root = base_dir / "old_db_excel"
    backup_root.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / f"backup_{timestamp}"
    
    try:
        if db_dir.exists():
            shutil.copytree(db_dir, backup_dir)
            print_success(f"Backup created: {backup_dir}")
            return True
        else:
            print_warning(f"Database directory not found: {db_dir}")
            return True  # Continue anyway
    except Exception as e:
        print_error(f"Backup failed: {e}")
        return False

def process_new_takeout(base_dir, auto_mode=False):
    """Check for and process new Google Takeout exports."""
    print_step(2, "Checking for new Google Takeout exports...")
    
    # Look for takeout zips
    import glob
    pattern = str(base_dir / "takeout-*.zip")
    zips = glob.glob(pattern)
    
    if not zips:
        print_warning("No new takeout zips found")
        print("  Skipping takeout processing...")
        return True
    
    # Sort by modification time, newest first
    zips.sort(key=os.path.getmtime, reverse=True)
    latest_zip = Path(zips[0])
    
    print(f"  Found: {latest_zip.name}")
    
    if not auto_mode:
        response = input(f"{Colors.YELLOW}  Process this takeout export? [Y/n]: {Colors.END}").strip().lower()
        if response == 'n':
            print("  Skipping takeout processing...")
            return True
    
    # Run the takeout processor
    print("\n  Running automated takeout processor...")
    
    try:
        # Import and run processor
        from process_takeout import TakeoutProcessor
        
        processor = TakeoutProcessor(base_dir, auto_mode=True)
        success = processor.process(zip_path=latest_zip.name)
        
        if success:
            print_success("Takeout processed successfully")
            return True
        else:
            print_error("Takeout processing failed")
            return False
            
    except ImportError:
        print_warning("process_takeout.py not found, falling back to manual conversion")
        return True
    except Exception as e:
        print_error(f"Takeout processing error: {e}")
        return False

def convert_keep_notes(base_dir):
    """Run the Keep notes to Excel conversion script."""
    print_step(3, "Converting Keep notes to Excel...")
    
    script_path = base_dir / "keep-notes-to-excel-conv.py"
    
    if not script_path.exists():
        print_error(f"Script not found: {script_path}")
        return False
    
    return run_command(
        ["python", str(script_path)],
        cwd=str(base_dir),
        description="Keep notes conversion"
    )

def update_database(base_dir):
    """Run the database update and FAISS indexing script."""
    print_step(4, "Updating database and rebuilding FAISS index...")
    
    script_path = base_dir / "update_db_and_index.py"
    
    if not script_path.exists():
        print_error(f"Script not found: {script_path}")
        return False
    
    return run_command(
        ["python", str(script_path)],
        cwd=str(base_dir),
        description="Database update"
    )

def auto_tag_images(base_dir, skip=False):
    """Run the auto-tagging script (optional)."""
    if skip:
        print_step(5, "Skipping auto-tagging (--skip-tagging flag)")
        return True
    
    print_step(5, "Auto-tagging images with CLIP...")
    print_warning("This may take several minutes for large image collections...")
    
    script_path = base_dir / "InteriorEngineFullV2" / "InteriorEngineFullV2" / "scripts" / "auto_tag_images.py"
    
    if not script_path.exists():
        print_warning(f"Script not found: {script_path}")
        print_warning("Skipping auto-tagging step.")
        return True
    
    return run_command(
        ["python", str(script_path)],
        cwd=str(base_dir / "InteriorEngineFullV2" / "InteriorEngineFullV2"),
        description="Auto-tagging"
    )

def rebuild_faiss(base_dir):
    """Rebuild FAISS index after tagging."""
    print_step(6, "Rebuilding FAISS index...")
    
    script_path = base_dir / "InteriorEngineFullV2" / "InteriorEngineFullV2" / "scripts" / "build_faiss.py"
    
    if not script_path.exists():
        print_warning(f"Script not found: {script_path}")
        return True
    
    return run_command(
        ["python", str(script_path)],
        cwd=str(base_dir / "InteriorEngineFullV2" / "InteriorEngineFullV2"),
        description="FAISS rebuild"
    )

def git_commit(base_dir, skip=False):
    """Commit changes to git (optional)."""
    if skip:
        print_step(7, "Skipping git commit (--skip-git flag)")
        return True
    
    print_step(7, "Committing to git...")
    
    # Check if git repo exists
    if not (base_dir / ".git").exists():
        print_warning("Not a git repository. Skipping git commit.")
        return True
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"Update database: {timestamp}"
    
    # Add all changes
    if not run_command(["git", "add", "."], cwd=str(base_dir), description="Git add"):
        return False
    
    # Commit
    if not run_command(["git", "commit", "-m", commit_msg], cwd=str(base_dir), description="Git commit"):
        print_warning("Nothing to commit or commit failed")
        return True  # Not a critical failure
    
    # Push
    if not run_command(["git", "push"], cwd=str(base_dir), description="Git push"):
        print_warning("Git push failed - you may need to push manually")
        return True  # Not a critical failure
    
    print_success("Changes committed and pushed!")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Automated update pipeline for Interior Inspiration Engine"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run without interactive prompts"
    )
    parser.add_argument(
        "--skip-tagging",
        action="store_true",
        help="Skip the auto-tagging step (faster if no new images)"
    )
    parser.add_argument(
        "--skip-git",
        action="store_true",
        help="Don't commit to git"
    )
    
    args = parser.parse_args()
    
    print_header("🏠 Interior Engine Update Pipeline")
    
    # Get base directory
    base_dir = Path(__file__).parent.absolute()
    print(f"Base directory: {base_dir}\n")
    
    # Interactive prompts if not in auto mode
    skip_tagging = args.skip_tagging
    skip_git = args.skip_git
    
    if not args.auto and not skip_tagging:
        response = input(f"{Colors.YELLOW}Run auto-tagging? (adds AI tags to images, takes 2-5 min) [y/N]: {Colors.END}").strip().lower()
        skip_tagging = response != 'y'
    
    if not args.auto and not skip_git:
        response = input(f"{Colors.YELLOW}Commit to git after update? [y/N]: {Colors.END}").strip().lower()
        skip_git = response != 'y'
    
    print()  # Blank line
    
    # Execute pipeline steps
    steps = [
        (backup_database, [base_dir]),
        (process_new_takeout, [base_dir, args.auto]),
        (convert_keep_notes, [base_dir]),
        (update_database, [base_dir]),
        (auto_tag_images, [base_dir, skip_tagging]),
        (rebuild_faiss, [base_dir]),
        (git_commit, [base_dir, skip_git]),
    ]
    
    for step_func, step_args in steps:
        if not step_func(*step_args):
            print_error("\n❌ Pipeline failed! Please check errors above.")
            sys.exit(1)
        print()  # Blank line between steps
    
    print_header("✅ Pipeline Complete!")
    print(f"{Colors.GREEN}Database successfully updated with new Keep notes.{Colors.END}")
    print(f"{Colors.GREEN}You can now launch the UI: streamlit run InteriorEngineFullV2/InteriorEngineFullV2/ui/app.py{Colors.END}\n")

if __name__ == "__main__":
    main()
