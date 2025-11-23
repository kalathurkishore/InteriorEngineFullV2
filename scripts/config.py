import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
MODELS_DIR = os.path.join(BASE_DIR, "models")
DB_PATH = os.path.join(BASE_DIR, "db", "interior.db")
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "db", "faiss.index")
FAISS_IDS_PATH = os.path.join(BASE_DIR, "db", "faiss_ids.pkl")

DEFAULT_CATEGORIES = [
    "living_room", "bedroom", "kitchen", "wardrobe",
    "staircase", "ceiling", "lighting", "bathroom",
    "balcony", "pooja_room", "exterior", "decor",
]

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
