# import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import sqlite3
# import pickle
# import numpy as np
# import streamlit as st

# from scripts.config import DB_PATH, IMAGES_DIR, FAISS_INDEX_PATH, FAISS_IDS_PATH
# from scripts.clip_features import get_clip_embedding

# st.set_page_config(page_title="Interior Engine Full V2", layout="wide")
# st.title("🏠 Interior Inspiration Engine – Full V2")

# def text_search(query: str, limit: int = 50):
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()
#     q = f"%{query.lower()}%"
#     cur.execute(
#         """SELECT filename, category, keywords, objects, colors, description
#                FROM images
#                WHERE lower(keywords) LIKE ?
#                   OR lower(objects) LIKE ?
#                   OR lower(description) LIKE ?""", (q, q, q)
#     )
#     rows = cur.fetchall()
#     conn.close()
#     return rows[:limit]

# def link_search(query: str, limit: int = 50):
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()
#     q = f"%{query.lower()}%"
#     cur.execute(
#         """SELECT file, links, text_snippet, keywords
#                FROM notes
#                WHERE lower(links) LIKE ?
#                   OR lower(text_snippet) LIKE ?
#                   OR lower(keywords) LIKE ?""", (q, q, q)
#     )
#     rows = cur.fetchall()
#     conn.close()
#     return rows[:limit]

# def image_search_faiss(uploaded, limit: int = 20):
#     if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(FAISS_IDS_PATH):
#         st.error("FAISS index not found. Run `python scripts/build_faiss.py` after indexing images.")
#         return []
#     temp_path = os.path.join(IMAGES_DIR, "_query_temp.jpg")
#     with open(temp_path, "wb") as f:
#         f.write(uploaded.getbuffer())
#     query_emb = get_clip_embedding(temp_path)

#     import faiss

#     index = faiss.read_index(FAISS_INDEX_PATH)
#     with open(FAISS_IDS_PATH, "rb") as f:
#         ids = pickle.load(f)

#     D, I = index.search(query_emb.reshape(1, -1), limit)

#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()

#     results = []
#     for score, idx in zip(D[0], I[0]):
#         img_id = ids[idx]
#         cur.execute("SELECT filename, category, keywords, objects, colors, description FROM images WHERE id=?", (img_id,))
#         row = cur.fetchone()
#         if row:
#             results.append((float(score), row))
#     conn.close()
#     return results

# tab1, tab2, tab3 = st.tabs(["🔎 Text Search", "📷 Image Search", "🔗 Link Search"])

# with tab1:
#     st.subheader("Text Search on Indexed Images")
#     col_q, col_l = st.columns([3,1])
#     with col_q:
#         q = st.text_input("Keyword (e.g., 'wardrobe', 'kitchen', 'tv unit'):", key="txt_q")
#     with col_l:
#         limit = st.number_input("Max results", min_value=5, max_value=200, value=20, step=5, key="txt_limit")
#     if st.button("Search images", key="text_search_btn") and q.strip():
#         rows = text_search(q, int(limit))
#         if not rows:
#             st.info("No results found.")
#         else:
#             for fname, cat, kw, objs, cols, desc in rows:
#                 with st.expander(f"{fname}  [{cat}]"):
#                     c1, c2 = st.columns([1,2])
#                     with c1:
#                         img_path = os.path.join(IMAGES_DIR, fname)
#                         if os.path.exists(img_path):
#                             st.image(img_path, use_column_width=True)
#                         else:
#                             st.write("(Image missing:", fname, ")")
#                     with c2:
#                         st.write(f"**Category:** {cat}")
#                         st.write(f"**Keywords:** {kw}")
#                         st.write(f"**Objects:** {objs}")
#                         st.write(f"**Colors:** {cols}")
#                         st.write(f"**Description:** {desc}")

# with tab2:
#     st.subheader("Image Similarity Search (FAISS)")
#     up = st.file_uploader("Upload a reference image", type=["jpg", "jpeg", "png"], key="img_up")
#     limit2 = st.number_input("Similar images to show", min_value=5, max_value=50, value=10, step=5, key="img_limit")
#     if up and st.button("Find similar", key="img_search_btn"):
#         res = image_search_faiss(up, int(limit2))
#         if not res:
#             st.info("No similar images found (or FAISS index not built).")
#         else:
#             for score, (fname, cat, kw, objs, cols, desc) in res:
#                 with st.expander(f"{fname}  [score={score:.3f}]"):
#                     c1, c2 = st.columns([1,2])
#                     with c1:
#                         img_path = os.path.join(IMAGES_DIR, fname)
#                         if os.path.exists(img_path):
#                             st.image(img_path, use_column_width=True)
#                         else:
#                             st.write("(Image missing:", fname, ")")
#                     with c2:
#                         st.write(f"**Category:** {cat}")
#                         st.write(f"**Keywords:** {kw}")
#                         st.write(f"**Objects:** {objs}")
#                         st.write(f"**Colors:** {cols}")
#                         st.write(f"**Description:** {desc}")

# with tab3:
#     st.subheader("Link Search (Excel URLs)")
#     col_q2, col_l2 = st.columns([3,1])
#     with col_q2:
#         q2 = st.text_input("Search in links/snippets (e.g., 'wardrobe', 'staircase'):", key="link_q")
#     with col_l2:
#         limit3 = st.number_input("Max link results", min_value=5, max_value=200, value=20, step=5, key="link_limit")
#     if st.button("Search links", key="link_search_btn") and q2.strip():
#         rows = link_search(q2, int(limit3))
#         if not rows:
#             st.info("No matching links.")
#         else:
#             for file, links, text_snippet, kw in rows:
#                 with st.expander(file):
#                     st.write(f"**Links:** {links}")
#                     st.write(f"**Keywords:** {kw}")
#                     st.write(f"**Snippet:** {text_snippet[:400]}…")

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlite3
import pickle
import numpy as np
import streamlit as st

from scripts.config import DB_PATH, IMAGES_DIR, FAISS_INDEX_PATH, FAISS_IDS_PATH
from scripts.clip_features import get_clip_embedding

st.set_page_config(page_title="Interior Engine Full V2", layout="wide")
st.title("🏠 Interior Inspiration Engine – Full V2")


# -------------------------------------------------------
# FIXED TEXT SEARCH FUNCTION
# -------------------------------------------------------
def text_search(query: str, limit: int = 50):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    q = f"%{query.lower()}%"

    cur.execute(
        """
        SELECT filename, category, keywords, objects, colors, description
        FROM images
        WHERE COALESCE(lower(keywords), '') LIKE ?
           OR COALESCE(lower(objects), '') LIKE ?
           OR COALESCE(lower(description), '') LIKE ?
        """,
        (q, q, q)
    )

    rows = cur.fetchall()
    conn.close()
    return rows[:limit]


# -------------------------------------------------------
# Link Search unchanged
# -------------------------------------------------------
def link_search(query: str, limit: int = 50):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    q = f"%{query.lower()}%"
    cur.execute(
        """SELECT file, links, text_snippet, keywords
           FROM notes
           WHERE COALESCE(lower(links), '') LIKE ?
              OR COALESCE(lower(text_snippet), '') LIKE ?
              OR COALESCE(lower(keywords), '') LIKE ?""",
        (q, q, q)
    )
    rows = cur.fetchall()
    conn.close()
    return rows[:limit]


# -------------------------------------------------------
# FAISS Image Search unchanged
# -------------------------------------------------------
def image_search_faiss(uploaded, limit: int = 20):
    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(FAISS_IDS_PATH):
        st.error("FAISS index not found. Run `python scripts/build_faiss.py` after indexing images.")
        return []

    temp_path = os.path.join(IMAGES_DIR, "_query_temp.jpg")
    with open(temp_path, "wb") as f:
        f.write(uploaded.getbuffer())

    query_emb = get_clip_embedding(temp_path)

    import faiss

    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(FAISS_IDS_PATH, "rb") as f:
        ids = pickle.load(f)

    D, I = index.search(query_emb.reshape(1, -1), limit)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    results = []
    for score, idx in zip(D[0], I[0]):
        img_id = ids[idx]
        cur.execute("SELECT filename, category, keywords, objects, colors, description FROM images WHERE id=?", (img_id,))
        row = cur.fetchone()
        if row:
            results.append((float(score), row))

    conn.close()
    return results


# -------------------------------------------------------
# UI TABS
# -------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🔎 Text Search", "📷 Image Search", "🔗 Link Search"])


# =======================================================
# FIXED TEXT SEARCH TAB
# =======================================================
with tab1:
    st.subheader("Text Search on Indexed Images")

    col_q, col_l = st.columns([3, 1])
    with col_q:
        q = st.text_input("Keyword (e.g., 'wardrobe', 'kitchen', 'tv unit'):", key="txt_q")
    with col_l:
        limit = st.number_input("Max results", min_value=5, max_value=200, value=20, step=5)

    search_clicked = st.button("Search images", key="text_search_btn")

    if search_clicked:
        if not q.strip():
            st.warning("Please enter a search keyword.")
        else:
            rows = text_search(q.strip(), int(limit))

            if not rows:
                st.info("No results found.")
            else:
                for fname, cat, kw, objs, cols, desc in rows:
                    with st.expander(f"{fname}  [{cat}]"):
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            img_path = os.path.join(IMAGES_DIR, fname)
                            if os.path.exists(img_path):
                                st.image(img_path, use_column_width=True)
                            else:
                                st.write("(Image missing:", fname, ")")
                        with c2:
                            st.write(f"**Category:** {cat}")
                            st.write(f"**Keywords:** {kw}")
                            st.write(f"**Objects:** {objs}")
                            st.write(f"**Colors:** {cols}")
                            st.write(f"**Description:** {desc}")


# =======================================================
# FAISS Search tab (unchanged)
# =======================================================
with tab2:
    st.subheader("Image Similarity Search (FAISS)")
    up = st.file_uploader("Upload a reference image", type=["jpg", "jpeg", "png"])
    limit2 = st.number_input("Similar images to show", min_value=5, max_value=50, value=10, step=5)

    if up and st.button("Find similar"):
        res = image_search_faiss(up, int(limit2))
        if not res:
            st.info("No similar images found (or FAISS index not built).")
        else:
            for score, (fname, cat, kw, objs, cols, desc) in res:
                with st.expander(f"{fname}  [score={score:.3f}]"):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        img_path = os.path.join(IMAGES_DIR, fname)
                        if os.path.exists(img_path):
                            st.image(img_path, use_column_width=True)
                        else:
                            st.write("(Image missing:", fname, ")")
                    with c2:
                        st.write(f"**Category:** {cat}")
                        st.write(f"**Keywords:** {kw}")
                        st.write(f"**Objects:** {objs}")
                        st.write(f"**Colors:** {cols}")
                        st.write(f"**Description:** {desc}")


# =======================================================
# Link Search tab (unchanged)
# =======================================================
with tab3:
    st.subheader("Link Search (Excel URLs)")

    col_q2, col_l2 = st.columns([3, 1])
    with col_q2:
        q2 = st.text_input("Search links/snippets:", key="link_q")
    with col_l2:
        limit3 = st.number_input("Max link results", min_value=5, max_value=200, value=20, step=5)

    link_clicked = st.button("Search links")

    if link_clicked:
        rows = link_search(q2.strip(), int(limit3))

        if not rows:
            st.info("No matching links.")
        else:
            for file, links, text_snippet, kw in rows:
                with st.expander(file):
                    st.write(f"**Links:** {links}")
                    st.write(f"**Keywords:** {kw}")
                    st.write(f"**Snippet:** {text_snippet[:400]}…")
