# Interior Inspiration Engine Full V2

Local, CPU-only interior design search engine with:

- Image indexing (CLIP + YOLO + colors + keywords)
- Text search on images
- Image similarity search (FAISS)
- Link search from Excel (YouTube/Instagram/other URLs)
- Optional automatic screenshots of URLs from Excel

## Setup

```bash
pip install -r requirements.txt
```

## Workflow

1. **(Optional) Import Excel links**

Place your Excel (from Google Takeout / Keep export) at:

`db/Interior_Inspiration_Database.xlsx`

Then run:

```bash
python scripts/import_excel.py --excel db/Interior_Inspiration_Database.xlsx
```

2. **(Optional) Auto-screenshot URLs**

Requires Google Chrome + chromedriver in PATH:

```bash
python scripts/screenshot_links.py --excel db/Interior_Inspiration_Database.xlsx --shots 3
```

This saves screenshots into `images/`.

3. **Index all images**

Put your design images (and URL screenshots) into `images/` and run:

```bash
python scripts/index_images.py --image_dir images
```

4. **Build FAISS index for fast visual search**

```bash
python scripts/build_faiss.py
```

5. **Launch the UI**

```bash
streamlit run ui/app.py
```

Then open the URL printed in the terminal (usually `http://localhost:8501`).
