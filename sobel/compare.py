import sys
import numpy as np
from PIL import Image

a = np.array(Image.open(sys.argv[1]))
b = np.array(Image.open(sys.argv[2]))
same = a.shape == b.shape and (a == b).all()
print("ЗБІГАЄТЬСЯ" if same else "НЕ ЗБІГАЄТЬСЯ", a.shape, b.shape)
sys.exit(0 if same else 1)
