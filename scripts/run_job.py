# -*- coding: utf-8 -*-
# Запускає PARCS-задачу через HTTP API master-вузла, чекає завершення і зберігає результат.
# Використання:  python3 run_job.py HOST:PORT solution.py input.png output.png
# Друкує час, який записав solution.py у PNG (мітка parcs_time).
import re
import subprocess
import sys
import time

from PIL import Image

host, solution, inp, out = sys.argv[1:5]
base = "http://" + host


def curl(*args):
    # -s тихий режим; повертає відповідь як байти
    return subprocess.run(["curl", "-s"] + list(args), capture_output=True).stdout


def max_job_id():
    # на сторінці /jobs кожна задача має data-job-id="N"; беремо найбільший
    ids = re.findall(rb'data-job-id="(\d+)"', curl(base + "/jobs"))
    return max(map(int, ids)) if ids else -1


before = max_job_id()
# Відправляємо задачу: файл рішення + вхідний файл (це наша картинка)
curl("-F", "job_name=sobel", "-F", "solution_file=@" + solution, "-F", "input_file=@" + inp, base + "/api/job")
job_id = max_job_id()
if job_id == before:
    sys.exit("Задача не створилась")

# Чекаємо: поки задача виконується, /output повертає 400 і порожню відповідь
for _ in range(600):
    time.sleep(1)
    page = curl(base + "/jobs").decode("utf-8", "ignore")
    block = page.split('data-job-id="%d"' % job_id)[1].split("data-job-id=")[0]
    if "Duration" in block and "error-text" in block:
        sys.exit("Задача впала: див. сторінку /jobs")
    data = curl(base + "/api/job/%d/output" % job_id)
    if data.startswith(b"\x89PNG"):
        open(out, "wb").write(data)
        print("PARCS_TIME=" + Image.open(out).text["parcs_time"])
        break
else:
    sys.exit("Таймаут")
