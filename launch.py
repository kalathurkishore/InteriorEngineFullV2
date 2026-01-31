#!/usr/bin/env python3
"""
Quick launch script for Interior Inspiration Engine.
Handles environment setup and launches the Streamlit UI.

Usage:
    python launch.py
    python launch.py --port 8502
    python launch.py --host 0.0.0.0  # For remote access
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse


def check_environment():
    """Check if required packages are installed."""
    try:
        import streamlit
        import torch
        import clip
        import faiss
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nPlease install requirements:")
        print("  pip install -r requirements.txt")
        return False


def check_database():
    """Check if database exists and has data."""
    db_path = Path(__file__).parent / "db" / "interior.db"
    
    if not db_path.exists():
        print("❌ Database not found!")
        print("\nPlease run the setup first:")
        print("  python update_pipeline.py")
        return False
    
    # Check database size
    size_mb = db_path.stat().st_size / (1024 * 1024)
    if size_mb < 0.1:
        print("⚠️  Database appears to be empty")
        print("\nRun the pipeline to index your images:")
        print("  python update_pipeline.py")
        return False
    
    print(f"✅ Database ready ({size_mb:.1f} MB)")
    return True


def check_images():
    """Check if images directory has content."""
    images_dir = Path(__file__).parent / "images"
    
    if not images_dir.exists():
        print("⚠️  Images directory not found")
        return False
    
    image_count = len(list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.webp")))
    
    if image_count == 0:
        print("⚠️  No images found")
        print("\nAdd images to: images/")
        return False
    
    print(f"✅ Found {image_count} images")
    return True


def launch_streamlit(port=8501, host="localhost"):
    """Launch the Streamlit application."""
    ui_path = Path(__file__).parent / "ui" / "app.py"
    
    if not ui_path.exists():
        print(f"❌ UI not found at: {ui_path}")
        return False
    
    print(f"\n🚀 Launching Interior Inspiration Engine...")
    print(f"   URL: http://{host}:{port}")
    print(f"\n   Press Ctrl+C to stop\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(ui_path),
            f"--server.port={port}",
            f"--server.address={host}",
            "--theme.base=light",
            "--theme.primaryColor=#1976D2",
        ])
        return True
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        return True
    except Exception as e:
        print(f"\n❌ Launch failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Launch Interior Inspiration Engine UI"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port to run on (default: 8501)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host address (default: localhost, use 0.0.0.0 for remote access)"
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip pre-launch checks"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("🏠 Interior Inspiration Engine")
    print("="*60)
    print()
    
    if not args.skip_checks:
        # Pre-launch checks
        print("Running pre-launch checks...\n")
        
        if not check_environment():
            sys.exit(1)
        
        if not check_database():
            response = input("\nContinue anyway? [y/N]: ").strip().lower()
            if response != 'y':
                sys.exit(1)
        
        check_images()
        print()
    
    # Launch
    success = launch_streamlit(port=args.port, host=args.host)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
