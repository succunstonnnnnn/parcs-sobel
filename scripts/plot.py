# Будує графік results.png з results.json (час від кількості воркерів).
import json
import os
import matplotlib
matplotlib.use("Agg")                      # без вікна, просто зберегти у файл
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(ROOT + "/results.json"))
mean = lambda v: sum(v) / len(v)

ns = sorted(int(k) for k in data if k != "seq")
parcs = [mean(data[str(n)]) for n in ns]
seq = mean(data["seq"])

plt.figure(figsize=(7, 4.5))
plt.plot(ns, parcs, "o-", color="#1f77b4", label="PARCS (середнє з 3 запусків)")
plt.axhline(seq, linestyle="--", color="#d62728", label="Послідовна версія (%.2f с)" % seq)
for n, t in zip(ns, parcs):
    plt.annotate("%.2f" % t, (n, t), textcoords="offset points", xytext=(0, 8), ha="center")
plt.xticks(ns)
plt.xlabel("Кількість воркерів N")
plt.ylabel("Час, с")
plt.title("Sobel 4000x4000: час виконання від кількості воркерів")
plt.ylim(0, max(parcs) * 1.15)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(ROOT + "/results.png", dpi=150)
print("Збережено results.png")
