from ultralytics import YOLO
from functools import lru_cache

@lru_cache(maxsize=1)
def load_yolo():
    # lightweight CPU-friendly YOLO
    return YOLO("yolov8n.pt")

def detect_objects(image_path, conf: float = 0.35):
    model = load_yolo()
    results = model.predict(image_path, conf=conf, verbose=False)
    labels = set()
    for r in results:
        for cls_idx in r.boxes.cls.tolist():
            labels.add(model.names[int(cls_idx)])
    return sorted(list(labels))
