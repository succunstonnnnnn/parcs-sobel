# -*- coding: utf-8 -*-
# PARCS-модуль: паралельний Sobel. Працює в Python 2.7 (так написана платформа PARCS).
#
# Схема:  master ділить картинку на смуги -> кожен worker рахує Sobel своєї смуги -> master склеює.
# Вхідний файл (input.txt) - це саме PNG-зображення, вихідний (output.txt) - PNG з контурами.
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

    # ---------- ця частина виконується на MASTER ----------
    def solve(self):
        n = len(self.workers)
        print("Job Started, workers: %d" % n)

        # 1. Читаємо зображення у сірому кольорі: масив h x w, числа 0..255
        img = np.array(Image.open(self.input_file_name).convert("L"))
        h, w = img.shape

        t0 = time.time()  # відлік часу: ділення + обчислення + збирання

        # 2. Додаємо рамку в 1 піксель (дублюємо краї), щоб крайні рядки теж мали сусідів
        padded = np.pad(img, 1, mode="edge")

        # 3. Ділимо h рядків на n смуг. bounds[i]..bounds[i+1] - рядки результату для worker i
        bounds = [h * i // n for i in range(n + 1)]

        # 4. Розсилаємо смуги. Планувальник PARCS уже зробив виклики workers асинхронними
        #    (не блокуючими) - тому всі workers стартують одночасно, а не по черзі.
        #    Результат виклику - "обіцянка", значення береться через .value (див. myreduce).
        #    Смуга з "перекриттям": беремо рядки a..b+2 з padded, тобто +1 зайвий рядок зверху і знизу.
        results = []
        for i in range(n):
            a, b = bounds[i], bounds[i + 1]
            strip = padded[a:b + 2, :]
            data = base64.b64encode(strip.tobytes()).decode("ascii")  # байти -> текст для передачі по мережі
            results.append(self.workers[i].mymap(data, strip.shape[0], strip.shape[1]))

        # 5. Збираємо відповіді (.value чекає, поки worker закінчить)
        parts = self.myreduce(results, w)
        edges = np.vstack(parts)  # склеюємо смуги зверху вниз

        seconds = time.time() - t0
        print("PARCS_TIME=%.3f workers=%d" % (seconds, n))

        # 6. Зберігаємо PNG (не входить у заміряний час). Час записуємо в текстову мітку PNG,
        #    щоб скрипт замірів міг його прочитати з output без доступу до логів сервера.
        info = PngImagePlugin.PngInfo()
        info.add_text("parcs_time", "%.3f" % seconds)
        buf = io.BytesIO()
        Image.fromarray(edges, "L").save(buf, "PNG", pnginfo=info)
        with open(self.output_file_name, "wb") as f:
            f.write(buf.getvalue())
        print("Job Finished")

    # ---------- ця частина виконується на WORKER ----------
    @staticmethod
    @expose
    def mymap(data, rows, cols):
        # Відновлюємо масив зі смуги (rows x cols), що прийшла текстом
        padded = np.frombuffer(base64.b64decode(data), dtype=np.uint8).reshape(rows, cols)
        result = Solver.sobel_padded(padded)
        return base64.b64encode(result.tobytes()).decode("ascii")

    @staticmethod
    def sobel_padded(padded):
        # Копія функції з sobel_seq.py (див. там коментарі до кожного рядка)
        p = padded.astype(np.float32)
        gx = (p[:-2, 2:] + 2 * p[1:-1, 2:] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[1:-1, :-2] + p[2:, :-2])
        gy = (p[2:, :-2] + 2 * p[2:, 1:-1] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[:-2, 1:-1] + p[:-2, 2:])
        return np.clip(np.sqrt(gx * gx + gy * gy), 0, 255).astype(np.uint8)

    # ---------- збирання результатів (на MASTER) ----------
    def myreduce(self, results, w):
        parts = []
        for r in results:
            raw = base64.b64decode(r.value)
            parts.append(np.frombuffer(raw, dtype=np.uint8).reshape(-1, w))
        return parts
