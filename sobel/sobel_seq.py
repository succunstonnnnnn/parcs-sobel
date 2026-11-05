import sys
import time
import numpy as np
from PIL import Image

def sobel_padded(padded):
    """Приймає зображення, яке вже має +1 рядок/стовпець з кожного боку
    (розмір (h+2) x (w+2)), і повертає контури розміром h x w.
    Ця ж функція (копія) є в solution.py - тому результати збігаються."""
    p = padded.astype(np.float32)
    gx = (p[:-2, 2:] + 2 * p[1:-1, 2:] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[1:-1, :-2] + p[2:, :-2])
    gy = (p[2:, :-2] + 2 * p[2:, 1:-1] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[:-2, 1:-1] + p[:-2, 2:])
    return np.clip(np.sqrt(gx * gx + gy * gy), 0, 255).astype(np.uint8)

if __name__ == "__main__":
    img = np.array(Image.open(sys.argv[1]).convert("L"))
    t0 = time.time()
    padded = np.pad(img, 1, mode="edge")
    result = sobel_padded(padded)
    seconds = time.time() - t0
    Image.fromarray(result, "L").save(sys.argv[2])
    print("SEQ_TIME=%.3f" % seconds)
