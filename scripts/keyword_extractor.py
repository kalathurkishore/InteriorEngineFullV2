from keybert import KeyBERT

_kw_model = None

def get_kw_model():
    global _kw_model
    if _kw_model is None:
        _kw_model = KeyBERT("all-MiniLM-L6-v2")
    return _kw_model

def extract_keywords(text: str, top_n: int = 10):
    if not text:
        return []
    model = get_kw_model()
    out = model.extract_keywords(text, top_n=top_n)
    return [k for k, _ in out]
