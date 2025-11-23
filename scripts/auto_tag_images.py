"""
Auto-tag all images using CLIP and APPEND tags to the existing `keywords`
column in the SQLite DB.

Usage (from project root where scripts/ and ui/ live):

    cd InteriorEngineFullV2
    python scripts/auto_tag_images.py

After running this, Streamlit text search will work for queries like:
    "kitchen", "wardrobe", "pooja room", "tv unit",
    "house elevation", "construction site",
    "silk saree", "soft silk", "family photo", "cartoon", etc.
"""

import os
import sqlite3
import sys

import torch
import clip
from PIL import Image

CURRENT_FILE = os.path.abspath(__file__)
SCRIPTS_DIR = os.path.dirname(CURRENT_FILE)

# Usually project root is one level above /scripts/
PROJECT_ROOT_1 = os.path.abspath(os.path.join(SCRIPTS_DIR, ".."))

# If nested twice (your case), add second parent
PROJECT_ROOT_2 = os.path.abspath(os.path.join(SCRIPTS_DIR, "../.."))

# Add both possible paths
sys.path.insert(0, PROJECT_ROOT_1)
sys.path.insert(0, PROJECT_ROOT_2)

from scripts.config import DB_PATH, IMAGES_DIR
from scripts.clip_features import load_clip




# ---------------------------------------------------------------------
# 1. TAG VOCABULARY (high-detail; you can tweak later)
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# 1. TAG VOCABULARY (Original + Expanded Housing Tags)
# ---------------------------------------------------------------------

# ------------------ ORIGINAL TAGS (PRESERVED EXACTLY) ------------------

ORIGINAL_INTERIOR_TAGS = [
    # room types
    "living room", "hall interior", "bedroom", "master bedroom",
    "kids bedroom", "guest bedroom", "kitchen", "modular kitchen",
    "island kitchen", "open kitchen", "dining area", "study room",
    "balcony", "utility area", "bathroom", "wash basin",

    # furniture
    "sofa set", "sofa and center table", "sectional sofa",
    "tv unit", "wall mounted tv", "floating tv unit", "storage unit",
    "wardrobe", "sliding wardrobe", "wardrobe with mirror",
    "bed with headboard", "side table", "shoe rack",

    # decor & elements
    "wall paneling", "wooden wall panel", "grooved panel",
    "slatted panel", "acoustic panels", "wall cladding",
    "wall art", "paintings", "photo frames", "mirror decor",
    "indoor plants", "decor accessories", "false ceiling",
    "cove ceiling", "pop false ceiling", "tv background wall",
    "feature wall", "accent wall", "marble wall cladding",
]

ORIGINAL_ARCHITECTURE_TAGS = [
    "house exterior", "building elevation", "front elevation",
    "modern house", "contemporary house", "duplex house", "villa",
    "independent house", "kerala style house", "south indian house",
    "sloped roof house", "flat roof house", "balcony glass railing",
    "driveway", "landscape design", "compound wall", "entrance gate",
    "architectural design", "facade lighting",
]

ORIGINAL_CONSTRUCTION_TAGS = [
    "construction site", "work in progress", "house construction",
    "renovation work", "cement work", "brick work", "masonry work",
    "plastering", "floor tiling", "scaffolding", "raw unfinished walls",
    "site visit", "civil engineer", "contractor on site",
]

ORIGINAL_POOJA_TAGS = [
    "pooja room", "temple unit", "home mandir", "mandir design",
    "devotional space", "idol decor", "brass lamps", "deepam",
    "framed deity image", "backlit panel", "spiritual decor",
]

ORIGINAL_TV_WALL_TAGS = [
    "tv wall design", "media wall", "feature tv wall", "tv unit with storage",
    "floating tv cabinet", "slatted tv wall", "vertical wooden slats",
    "acoustic vertical panels", "wall mounted sound bar",
    "tv wall with fireplace", "modern media wall",
]

ORIGINAL_FASHION_TAGS = [
    "saree", "silk saree", "soft silk saree", "pattu saree",
    "kanchipuram saree", "bridal saree", "wedding saree",
    "lehenga", "bridal lehenga", "dupatta",
    "dhoti", "shirt and dhoti set", "kurta", "ethnic wear",
    "traditional wear", "couple outfit", "matching family outfit",
    "men ethnic wear", "women ethnic wear",
]

ORIGINAL_PEOPLE_SCENE_TAGS = [
    "man", "woman", "boy", "girl", "child", "children",
    "couple", "small family", "group photo",
    "selfie video", "talking to camera",
    "wedding ceremony", "engagement", "muhurtham",
    "festival celebration", "diwali", "pongal",
    "studio photo", "outdoor photo", "street scene",
]

ORIGINAL_PRODUCT_POSTER_TAGS = [
    "product display", "saree stack", "folded sarees", "fabric stack",
    "boutique display", "hanger set", "offer banner",
    "poster design", "promo flyer", "instagram poster",
    "coming soon post", "price information", "text overlay",
]

ORIGINAL_ART_CARTOON_TAGS = [
    "cartoon character", "family cartoon", "wedding cartoon",
    "digital illustration", "krishna cartoon", "temple art",
    "storytelling comic", "animated style artwork",
]

ORIGINAL_MATERIAL_PATTERN_TAGS = [
    "handloom fabric", "woven texture", "zari border", "golden border",
    "contrast border", "small checks pattern", "big checks pattern",
    "floral pattern", "geometric pattern", "paisley design",
    "dual tone fabric", "rich pallu", "heavy border",
    "wooden flooring", "marble flooring", "tiles flooring",
    "matte finish", "glossy finish", "granite counter",
]

ORIGINAL_LIGHTING_TAGS = [
    "spot lights", "recessed lights", "cove lighting", "ceiling lights",
    "track lights", "pendant lights", "wall sconces",
    "strip lighting", "led strip lights", "profile lights",
    "warm lighting", "cool white lighting", "backlit panel lighting",
]

ORIGINAL_COLOR_TAGS = [
    "red", "maroon", "orange", "yellow", "gold", "rose gold",
    "green", "dark green", "olive green",
    "blue", "navy blue", "royal blue", "turquoise",
    "purple", "violet", "lavender",
    "pink", "baby pink", "peach", "coral",
    "brown", "beige", "cream", "off white", "ivory",
    "black", "white", "grey", "charcoal grey",
    "multi color", "dual color", "pastel shades",
]

ORIGINAL_STYLE_VIBE_TAGS = [
    "modern interior", "contemporary interior", "minimal design",
    "luxury interior", "premium look", "cozy feel",
    "traditional interior", "south indian traditional style",
]


# ------------------ EXPANDED 560+ TAG VOCABULARY (FULL SET) ------------------

# (Already provided in previous message — too large to duplicate inside this block)

# USE THESE EXACT NAMES (do not rename):
# INTERIOR_TAGS
# ARCHITECTURE_TAGS
# CONSTRUCTION_TAGS
# POOJA_TAGS
# KITCHEN_TAGS
# BATHROOM_TAGS
# WINDOW_DOOR_TAGS
# LANDSCAPE_TAGS
# DECOR_TAGS
# LIGHTING_TAGS
# COLOR_TAGS
# VASTU_TAGS

INTERIOR_TAGS = [
    # room types
    "living room","hall interior","drawing room","family room","modular living room",
    "lounge area","foyer area","entrance lobby","reception area",
    "bedroom","master bedroom","guest bedroom","kids bedroom","teen bedroom",
    "parents bedroom","study room","home office","workspace",
    "kitchen","modular kitchen","open kitchen","island kitchen","u shaped kitchen",
    "l shaped kitchen","parallel kitchen","gallery kitchen","service kitchen",
    "dining area","breakfast counter","bar counter","pantry area",
    "balcony","utility balcony","enclosed balcony","sit out area",
    "bathroom","master bathroom","powder room","common washroom",
    "laundry room","store room","walk in wardrobe","dressing area",
    "reading corner","bay window seating","media room","theatre room",
    "entertainment room","play room","gym room","home gym","yoga room",

    # furniture
    "sofa set","l shaped sofa","sectional sofa","recliner sofa","sofa with chaise",
    "fabric sofa","leather sofa",
    "sofa and center table", "center table","wooden center table",
    "marble top center table","side table","console table","nesting tables",
    "tv unit","floating tv unit","wall mounted tv","wall mounted tv unit","media wall",
    "bookshelf","ladder shelf","open shelf","shoe rack","shoe cabinet",
    "crockery unit","wardrobe","sliding wardrobe","hinged wardrobe",
    "floor to ceiling wardrobe","walk in closet","loft storage",
    "wardrobe with mirror",
    "bed with headboard","upholstered headboard","wooden headboard",
    "king size bed","queen size bed","platform bed",
    "dressing table","vanity unit","study table","modular study unit",
    "kitchen cabinets","overhead cabinets","tall unit","pantry unit",
    "cutlery organizer","corner storage","wardrobe mirror",

    # decor
    "false ceiling","pop false ceiling","gypsum ceiling","cove ceiling",
    "recessed ceiling","wooden ceiling","groove ceiling",
    "wall paneling","wooden wall panel","slatted panel","fluted panel",
    "grooved panel","acoustic panels","pvc wall panels","marble wall cladding",
    "concrete texture wall","brick cladding","accent wall","feature wall",
    "tv background wall","marble wall cladding","tv wall cladding",
    "textured wall paint","decor niche","wall niche","floating shelves",
    "curtains","sheer curtains","blackout curtains","window blinds",
    "roman blinds","zebra blinds","curtain pelmet",
    "wall art","paintings","painting frame","gallery wall",
    "mirror decor","round mirror","full length mirror",
    "plant decor","indoor plants","ceramic planters","hanging planters",
    "partition wall","jaali partition","glass partition","wooden partition",
    "room divider","pooja partition",
    "floor rug","area rug","carpet flooring","wallpaper",
    "textured wallpaper","fabric wallpaper","decor accessories"
]

# ------------------ ARCHITECTURE & EXTERIOR DESIGN ------------------

ARCHITECTURE_TAGS = [
    "house exterior","front elevation","side elevation","rear elevation",
    "modern elevation","contemporary elevation","duplex house","triplex house",
    "g+1 house","g+2 house","villa","independent house","corner plot house",
    "kerala style house","south indian house",
    "sloped roof house","flat roof house",
    "balcony railing","st stainless steel railing","glass railing","balcony glass railing",
    "compound wall","front gate","sliding gate","designer gate",
    "landscape design","driveway","driveway design","porch area",
    "terrace garden","terrace seating","pergola roof","jalli wall",
    "wooden louvers","vertical fins","hpl panels",
    "exterior cladding","stone cladding exterior","brick façade",
    "sunshade design","chajja design","parapet wall",
    "window grill design","balcony grill design",
    "architectural design","facade lighting","premium elevation","luxury villa",
    "gated community"
]

# ------------------ CONSTRUCTION PHASE TAGS ------------------

CONSTRUCTION_TAGS = [
    "construction site","foundation work","excavation work","pillar reinforcement",
    "column shuttering","beam shuttering","centering work","scaffolding",
    "curing process","brick work","block work","plastering work",
    "electrical conduit","plumbing line installation","floor tiling",
    "tile cutting","tile grouting","waterproofing","sump construction",
    "septic tank","roof slab casting","concrete mixing","rebar bending",
    "site measurement","site marking","footing marking","concrete curing",
    "cement bags","sand stockpile","raw unfinished walls","unfinished walls",
    "lintel casting","door frame installation","window frame installation",
    "wall putty","primer coat","final coat painting","masonry tools",
    "steel bars","site supervisor","civil engineer","contractor on site",
    "renovation work","house construction","work in progress"
]

# ------------------ POOJA ROOM & TEMPLE TAGS ------------------

POOJA_TAGS = [
    "pooja room","mandir design","pooja unit","home mandir",
    "backlit om panel","lattice panel","jaali doors",
    "idol niche","idol decor","brass lamps","deepam","diya stand",
    "floating pooja shelf","marble mandir","wooden mandir",
    "temple backdrop","carved panel","spiritual decor",
    "gopuram style mandir","pooja door design","bell strings",
    "incense holder","agarbatti stand","framed deity image"
]

# ------------------ KITCHEN TAGS ------------------

KITCHEN_TAGS = [
    "kitchen island","breakfast counter","spice rack","tandem drawer",
    "soft close drawers","cutlery tray","tall unit","microwave unit",
    "oven unit","hob and chimney","parallel kitchen","u shaped kitchen",
    "l shaped kitchen","quartz counter","granite counter","backsplash tiles",
    "modular kitchen baskets","wicker basket","bottle pull out","corner carousel",
    "undermount sink","double sink","granite sink",
    "led kitchen lighting","under cabinet lights",
    "open shelves kitchen","glass door cabinets",
    "kitchen skirting","dado tiles","chimney hood","breakfast nook",
    "appliance garage"
]

# ------------------ BATHROOM TAGS ------------------

BATHROOM_TAGS = [
    "vanity unit","vanity mirror","led mirror","concealed cistern",
    "wall mounted toilet","floor mounted toilet","shower partition",
    "glass partition","shower cubicle","rain shower","hand shower",
    "bathroom tiles","anti skid tiles","designer bathroom wall",
    "bathroom niche","soap holder niche","water heater","exhaust fan",
    "towel rack","mirror cabinet","bathroom accessories"
]

# ------------------ WINDOWS & DOORS ------------------

WINDOW_DOOR_TAGS = [
    "wooden door","flush door","designer main door","sliding door",
    "folding door","glass door","wooden frame window","upvc window",
    "aluminium window","french window","bay window","corner window",
    "ventilator window","door handle","brass handle","digital lock",
    "door architrave","window grill design","balcony grill pattern",
    "mesh door","mosquito mesh window","louvered door"
]

# ------------------ LANDSCAPING TAGS ------------------

LANDSCAPE_TAGS = [
    "garden landscape","front yard","backyard garden","planter wall",
    "terrace garden","balcony planters","grass pavers","cobblestone flooring",
    "pergola seating","garden lights","pathway lighting","outdoor seating",
    "swing seat","hammock","gazebo","water fountain","lotus pond",
    "rock garden","vertical garden","green wall","bonsai display",
    "tree pit","boundary planters","outdoor tiles"
]

# ------------------ HOME DECOR TAGS ------------------

DECOR_TAGS = [
    "cushion set","throw blanket","bed runner","decor vases","ceramic pots",
    "abstract sculpture","wall clocks","hanging decor","candles","diffusers",
    "centerpiece decor","dining table decor","photo frame set",
    "gallery wall frames","decor baskets","rug decor","table lamps",
    "floor lamps","indoor planters","metal wall art","wall shelves decor",
    "lantern decor","artificial plants","textured cushions","floor candles"
]

# ------------------ LIGHTING TAGS ------------------

LIGHTING_TAGS = [
    "ceiling lights","recessed lights","spot lights","cove lights",
    "profile lights","led strip lights","pendant lights","hanging lights",
    "chandeliers","wall sconces","bedside lamps","floor lamps",
    "track lights","linear lights","picture lights","warm white lighting",
    "cool white lighting","neutral white lighting","backlit panel",
    "backlit mirror","sensor lights","hidden lighting","toe kick lighting",
    "under cabinet lighting","lobby lighting","staircase lighting",
    "outdoor wall lights","gate lights","façade spotlights",
    "garden bollard lights","pathway lights","balcony lights",
    "backlit panel lighting"
]

# ------------------ COLOR TAGS ------------------

COLOR_TAGS = [
    "red","maroon","orange","yellow","gold","rose gold",
    "green","dark green","olive green","blue","navy blue",
    "royal blue","turquoise","purple","violet","lavender",
    "pink","baby pink","peach","coral",
    "brown","beige","cream","off white","ivory",
    "black","white","grey","charcoal grey",
    "multi color","dual color","pastel shades"
]

# ------------------ VASTU TAGS ------------------

VASTU_TAGS = [
    "vastu compliant","east facing entrance","north facing kitchen",
    "south west master bedroom","puja room east direction",
    "cooking east facing","staircase south west","bedhead south direction",
    "toilet northwest","positive energy interior","vastu colors",
    "water element zone","fire element zone","balcony north east",
    "heavy storage south west","mirror vastu","mandir vastu",
    "main door vastu","center of house vastu","vastu corrections"
]

# ---------------------------------------------------------------------
# 2. MERGE EVERYTHING INTO A SINGLE MASTER TAG LIST
# ---------------------------------------------------------------------

ALL_TAGS = list(dict.fromkeys(

    # original preserved tags
    ORIGINAL_INTERIOR_TAGS +
    ORIGINAL_ARCHITECTURE_TAGS +
    ORIGINAL_CONSTRUCTION_TAGS +
    ORIGINAL_POOJA_TAGS +
    ORIGINAL_TV_WALL_TAGS +
    ORIGINAL_FASHION_TAGS +
    ORIGINAL_PEOPLE_SCENE_TAGS +
    ORIGINAL_PRODUCT_POSTER_TAGS +
    ORIGINAL_ART_CARTOON_TAGS +
    ORIGINAL_MATERIAL_PATTERN_TAGS +
    ORIGINAL_LIGHTING_TAGS +
    ORIGINAL_COLOR_TAGS +
    ORIGINAL_STYLE_VIBE_TAGS +

    # expanded 560+ vocab
    INTERIOR_TAGS +
    ARCHITECTURE_TAGS +
    CONSTRUCTION_TAGS +
    POOJA_TAGS +
    KITCHEN_TAGS +
    BATHROOM_TAGS +
    WINDOW_DOOR_TAGS +
    LANDSCAPE_TAGS +
    DECOR_TAGS +
    LIGHTING_TAGS +
    COLOR_TAGS +
    VASTU_TAGS
))



# ---------------------------------------------------------------------
# 2. CLIP helpers
# ---------------------------------------------------------------------

def get_model_and_text_embeddings():
    """
    Load CLIP (same as rest of project) and precompute embeddings
    for all tag texts.
    """
    model, preprocess = load_clip()  # from scripts.clip_features
    device = next(model.parameters()).device

    print(f"[CLIP] Loaded model on device: {device}")
    print(f"[CLIP] Building text embeddings for {len(ALL_TAGS)} tags...")

    text_tokens = clip.tokenize(ALL_TAGS).to(device)

    with torch.no_grad():
        text_emb = model.encode_text(text_tokens)

    text_emb = text_emb / text_emb.norm(dim=-1, keepdim=True)
    return model, preprocess, text_emb, device


def encode_image(model, preprocess, device, image_path):
    img = Image.open(image_path).convert("RGB")
    img_in = preprocess(img).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = model.encode_image(img_in)
    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb  # (1, D), normalized


def select_tags_for_image(
    img_emb,
    text_emb,
    min_tags: int = 10,
    max_tags: int = 80,
    sim_threshold: float = 0.25,
):
    """
    Given one image embedding and all text embeddings, return a list
    of selected tags based on cosine similarity.

    High detail mode:
      - always take TOP min_tags tags
      - then keep adding tags while similarity >= threshold
      - stop at max_tags
    """
    sims = (img_emb @ text_emb.T).squeeze(0)  # (N,)
    sims_cpu = sims.cpu().numpy()

    sorted_idx = sims_cpu.argsort()[::-1]  # high → low
    chosen = []

    for idx in sorted_idx:
        score = sims_cpu[idx]
        tag = ALL_TAGS[idx]

        # always take top N
        if len(chosen) < min_tags:
            chosen.append(tag)
            continue

        # beyond min_tags: only if above threshold
        if score < sim_threshold:
            break

        chosen.append(tag)
        if len(chosen) >= max_tags:
            break

    # Deduplicate while preserving order
    seen = set()
    final = []
    for t in chosen:
        if t not in seen:
            seen.add(t)
            final.append(t)

    return final


# ---------------------------------------------------------------------
# 3. DB update logic (APPEND to existing keywords)
# ---------------------------------------------------------------------

def main():
    print(f"[DB] Using database: {DB_PATH}")
    print(f"[IMG] Using images dir: {IMAGES_DIR}")

    if not os.path.exists(DB_PATH):
        raise SystemExit(f"DB not found at {DB_PATH}")

    model, preprocess, text_emb, device = get_model_and_text_embeddings()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, filename, COALESCE(keywords, '') FROM images")
    rows = cur.fetchall()

    total = len(rows)
    print(f"[DB] Found {total} images to tag.")

    updated = 0
    skipped = 0

    for i, (img_id, fname, existing_kw) in enumerate(rows, start=1):
        img_path = os.path.join(IMAGES_DIR, fname)

        if not os.path.exists(img_path):
            print(f"[WARN] Missing image file, skipping: {fname}")
            skipped += 1
            continue

        try:
            img_emb = encode_image(model, preprocess, device, img_path)
            new_tags = select_tags_for_image(img_emb, text_emb)

            if not new_tags:
                print(f"[INFO] No new tags for {fname}, keeping existing keywords.")
                skipped += 1
                continue

            # existing keywords → list
            existing_list = [
                x.strip() for x in existing_kw.split(",") if x.strip()
            ]

            # merge existing + new, preserving order & uniqueness
            merged = []
            seen = set()

            for t in existing_list + new_tags:
                if t not in seen:
                    seen.add(t)
                    merged.append(t)

            kw_str = ", ".join(merged)

            cur.execute(
                "UPDATE images SET keywords = ? WHERE id = ?",
                (kw_str, img_id),
            )
            updated += 1

        except Exception as e:
            print(f"[ERROR] Failed on {fname}: {e}")
            skipped += 1
            continue

        if i % 25 == 0 or i == total:
            conn.commit()
            print(
                f"[PROGRESS] {i}/{total} processed "
                f"(updated={updated}, skipped={skipped})"
            )

    conn.commit()
    conn.close()

    print("\n[DONE] Auto-tagging complete.")
    print(f"       Updated rows : {updated}")
    print(f"       Skipped rows : {skipped}")
    print("Now run your Streamlit app and try searches like:")
    print("  'kitchen', 'pooja room', 'tv unit design',")
    print("  'house elevation', 'construction site',")
    print("  'soft silk saree', 'family photo', 'cartoon story', etc.")


if __name__ == "__main__":
    main()
