from colorthief import ColorThief

def extract_colors(image_path, count: int = 5):
    ct = ColorThief(image_path)
    return ct.get_palette(color_count=count)
