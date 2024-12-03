import numpy as np

def convert_float32(obj):
    if isinstance(obj, list):
        return [convert_float32(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_float32(v) for k, v in obj.items()}
    elif isinstance(obj, np.float32):
        return float(obj)
    return obj

def bbox_to_xywh(x1, y1, x2, y2, img_w, img_h):
    w = x2 - x1
    h = y2 - y1
    x = x1 + w / 2
    y = y1 + h / 2
    return x / img_w, y / img_h, w / img_w, h / img_h
