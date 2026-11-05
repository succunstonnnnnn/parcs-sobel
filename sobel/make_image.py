import sys
import numpy as np
from PIL import Image

SIZE = 4000
rng = np.random.RandomState(42)

x = np.linspace(0, 255, SIZE, dtype=np.float32)
img = np.tile(x, (SIZE, 1)) * 0.5

yy, xx = np.mgrid[0:SIZE, 0:SIZE]
for _ in range(60):
    cx, cy = rng.randint(0, SIZE, 2)
    r = rng.randint(50, 300)
    img[(xx - cx) ** 2 + (yy - cy) ** 2 < r * r] = rng.randint(0, 256)
for _ in range(60):
    x0, y0 = rng.randint(0, SIZE - 400, 2)
    w, h = rng.randint(50, 400, 2)
    img[y0:y0 + h, x0:x0 + w] = rng.randint(0, 256)

img += rng.normal(0, 5, img.shape)

Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'L').save(sys.argv[1])
print("Збережено", sys.argv[1])
