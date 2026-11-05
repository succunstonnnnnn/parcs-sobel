# Базовий образ вже містить Python 2.7 (платформа PARCS написана на Python 2),
# тому apt-get не потрібен (репозиторії Debian stretch вже видалені).
FROM python:2.7-slim

WORKDIR /parcs
COPY . /parcs

# Версії зафіксовані, бо "останні" вже не підтримують Python 2.
# numpy 1.16 - остання гілка для Python 2.7. Pillow потрібен лише щоб читати/писати PNG.
RUN pip install --no-cache-dir Pyro4 netifaces py-cpuinfo==5.0.0 flask requests numpy Pillow

CMD ["./run.sh"]
