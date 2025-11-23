import torch
import clip
from PIL import Image
from functools import lru_cache

DEVICE = "cpu"

@lru_cache(maxsize=1)
def load_clip():
    model, preprocess = clip.load("ViT-B/32", device=DEVICE)
    model.eval()
    return model, preprocess

def get_clip_embedding(image_path):
    model, preprocess = load_clip()
    img = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        emb = model.encode_image(img)
    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.cpu().numpy().flatten().astype("float32")
