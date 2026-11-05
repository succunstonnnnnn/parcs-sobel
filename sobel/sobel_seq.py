# -*- coding: utf-8 -*-
# ПОСЛІДОВНА версія Sobel (без PARCS). Працює і в Python 2, і в Python 3.
# Запуск:  python sobel_seq.py input.png output_seq.png
import sys
import time
import numpy as np
from PIL import Image


def sobel_padded(padded):
    """Приймає зображення, яке вже має +1 рядок/стовпець з кожного боку
    (розмір (h+2) x (w+2)), і повертає контури розміром h x w.
    Ця ж функція (копія) є в solution.py - тому результати збігаються."""
    p = padded.astype(np.float32)
    # Sobel X: ядро [[-1,0,1],[-2,0,2],[-1,0,1]] - різниця правого і лівого сусіда
    gx = (p[:-2, 2:] + 2 * p[1:-1, 2:] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[1:-1, :-2] + p[2:, :-2])
    # Sobel Y: ядро [[-1,-2,-1],[0,0,0],[1,2,1]] - різниця нижнього і верхнього сусіда
    gy = (p[2:, :-2] + 2 * p[2:, 1:-1] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[:-2, 1:-1] + p[:-2, 2:])
    # Довжина градієнта = яскравість контуру; обрізаємо до 0..255
    return np.clip(np.sqrt(gx * gx + gy * gy), 0, 255).astype(np.uint8)


if __name__ == "__main__":
    img = np.array(Image.open(sys.argv[1]).convert("L"))
    t0 = time.time()
    # "edge" - краї дублюються, щоб у крайніх пікселів теж були сусіди
    padded = np.pad(img, 1, mode="edge")
    result = sobel_padded(padded)
    seconds = time.time() - t0
    Image.fromarray(result, "L").save(sys.argv[2])
    print("SEQ_TIME=%.3f" % seconds)
