import base64
import io
import time

import numpy as np
from PIL import Image
from Pyro4 import expose
from PIL import PngImagePlugin

class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.workers = workers
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name

    def solve(self):
        n = len(self.workers)
        print("Job Started, workers: %d" % n)

        img = np.array(Image.open(self.input_file_name).convert("L"))
        h, w = img.shape

        t0 = time.time()

        padded = np.pad(img, 1, mode="edge")

        bounds = [h * i // n for i in range(n + 1)]

        results = []
        for i in range(n):
            a, b = bounds[i], bounds[i + 1]
            strip = padded[a:b + 2, :]
            data = base64.b64encode(strip.tobytes()).decode("ascii")
            results.append(self.workers[i].mymap(data, strip.shape[0], strip.shape[1]))

        parts = self.myreduce(results, w)
        edges = np.vstack(parts)

        seconds = time.time() - t0
        print("PARCS_TIME=%.3f workers=%d" % (seconds, n))

        info = PngImagePlugin.PngInfo()
        info.add_text("parcs_time", "%.3f" % seconds)
        buf = io.BytesIO()
        Image.fromarray(edges, "L").save(buf, "PNG", pnginfo=info)
        with open(self.output_file_name, "wb") as f:
            f.write(buf.getvalue())
        print("Job Finished")

    @staticmethod
    @expose
    def mymap(data, rows, cols):
        padded = np.frombuffer(base64.b64decode(data), dtype=np.uint8).reshape(rows, cols)
        result = Solver.sobel_padded(padded)
        return base64.b64encode(result.tobytes()).decode("ascii")

    @staticmethod
    def sobel_padded(padded):
        p = padded.astype(np.float32)
        gx = (p[:-2, 2:] + 2 * p[1:-1, 2:] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[1:-1, :-2] + p[2:, :-2])
        gy = (p[2:, :-2] + 2 * p[2:, 1:-1] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[:-2, 1:-1] + p[:-2, 2:])
        return np.clip(np.sqrt(gx * gx + gy * gy), 0, 255).astype(np.uint8)

    def myreduce(self, results, w):
        parts = []
        for r in results:
            raw = base64.b64decode(r.value)
            parts.append(np.frombuffer(raw, dtype=np.uint8).reshape(-1, w))
        return parts
