import json
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = 3
ZONE = "europe-central2-a"
SEQ_VM = "parcs-worker-1"

def sh(cmd):
    """Виконати shell-команду і повернути її вивід."""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True).stdout

master_ip = sh("gcloud compute instances describe parcs-master --zone %s "
               "--format='value(networkInterfaces[0].accessConfigs[0].natIP)'" % ZONE).strip()
host = master_ip + ":8080"
print("master:", host)
results = {}

image = sh("bash -c 'source %s/scripts/config.sh; echo $IMAGE'" % ROOT).strip()
sh("gcloud compute scp %s/sobel/sobel_seq.py %s/images/input.png %s:~ --zone %s" % (ROOT, ROOT, SEQ_VM, ZONE))
times = []
for i in range(RUNS):
    out = sh("gcloud compute ssh %s --zone %s --command \"docker run --rm -v \\$HOME:/data %s "
             "python /data/sobel_seq.py /data/input.png /data/output_seq.png\"" % (SEQ_VM, ZONE, image))
    t = float(re.search(r"SEQ_TIME=([\d.]+)", out).group(1))
    times.append(t)
    print("послідовна, запуск %d: %.3f c" % (i + 1, t))
results["seq"] = times
sh("gcloud compute scp %s:~/output_seq.png %s/images/output_seq_vm.png --zone %s" % (SEQ_VM, ROOT, ZONE))

workers = json.load(urllib.request.urlopen("http://%s/api/worker" % host))["workers"]
ids = sorted(w["id"] for w in workers)
print("воркери:", ids)
for n in range(1, len(ids) + 1):
    for k, wid in enumerate(ids):
        state = "enable" if k < n else "disable"
        urllib.request.urlopen(urllib.request.Request("http://%s/api/worker/%d/%s" % (host, wid, state), method="POST"))
    times = []
    for i in range(RUNS):
        out_png = "%s/images/output_parcs_n%d.png" % (ROOT, n)
        out = sh(sys.executable + " %s/scripts/run_job.py %s %s/sobel/solution.py %s/images/input.png %s"
                 % (ROOT, host, ROOT, ROOT, out_png))
        t = float(re.search(r"PARCS_TIME=([\d.]+)", out).group(1))
        times.append(t)
        print("N=%d, запуск %d: %.3f c" % (n, i + 1, t))
    results[n] = times
    print(sh(sys.executable + " %s/sobel/compare.py %s/images/output_seq_vm.png %s" % (ROOT, ROOT, out_png)).strip())

json.dump({str(k): v for k, v in results.items()}, open(ROOT + "/results.json", "w"), indent=2)
print("Збережено results.json")
