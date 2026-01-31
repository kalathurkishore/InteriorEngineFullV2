# 🚀 Quick Start Guide

## One-Line Launch

```bash
./run.sh
```

This will:
- ✅ Activate the conda environment
- ✅ Show system status
- ✅ Launch the Streamlit UI

## Manual Launch

```bash
# 1. Activate environment
conda activate idp

# 2. Check status
python status.py

# 3. Launch UI
python launch.py
# Or: streamlit run ui/app.py
```

## Update Database with New Google Keep Notes

```bash
# 1. Download Google Takeout (Keep only)
# 2. Move zip to this directory
mv ~/Downloads/takeout-*.zip .

# 3. Run automated pipeline
python update_pipeline.py

# 4. Launch UI
./run.sh
```

## Optimize Storage (Run Once)

```bash
# Preview savings
python optimize_storage.py --dry-run

# Apply optimization (converts PNG → WebP, removes duplicates)
python optimize_storage.py
```

## System Status

```bash
python status.py
```

Shows:
- Image count and database size
- Storage usage by format
- FAISS index status
- FTS5 search status
- Recommendations

## Current Stats

✅ **1,020 images** indexed  
✅ **4,979 Keep notes** imported  
✅ **FAISS index** ready (image search)  
✅ **FTS5** enabled (20x faster text search)  
💾 **1.2 GB** image storage (can optimize to ~700MB)

## Available Scripts

| Script | Purpose |
|--------|---------|
| `run.sh` | One-click launcher with environment activation |
| `launch.py` | Launch UI with pre-flight checks |
| `status.py` | Show system health dashboard |
| `update_pipeline.py` | Automated update workflow (7 steps in 1) |
| `process_takeout.py` | Auto-extract Google Takeout zips |
| `optimize_storage.py` | Reduce storage with WebP conversion |
| `setup_fts5.py` | Enable fast text search (run once) |

## Productivity Tips

### Alias for Quick Launch
Add to `~/.bashrc`:
```bash
alias interior='cd /home/kishore/InteriorEngineFinalComplete/InteriorEngineFullV2/InteriorEngineFullV2 && ./run.sh'
```

Then just run:
```bash
interior
```

### Scheduled Updates
Auto-update daily with cron:
```bash
crontab -e
# Add:
0 2 * * * cd /home/kishore/InteriorEngineFinalComplete && conda run -n idp python update_pipeline.py --auto
```

## URLs

- **Local UI**: http://localhost:8501
- **Remote Access**: Change `run.sh` line with `--server.address=0.0.0.0`

## Next Steps

1. ⚡ **Optimize storage**: `python optimize_storage.py` (saves 500MB)
2. 📱 **Create alias**: Add quick launcher to bashrc
3. 🔄 **Schedule updates**: Set up cron for automatic sync

**Happy designing!** 🏠✨
