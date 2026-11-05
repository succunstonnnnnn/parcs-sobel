#!/bin/bash
# Стартовий скрипт VM (GCP запускає його при КОЖНОМУ старті машини).
# Він читає з метаданих VM образ і аргументи та запускає PARCS-контейнер.
META=http://metadata.google.internal/computeMetadata/v1/instance/attributes
IMAGE=$(curl -s -H "Metadata-Flavor: Google" $META/parcs-image)
ARGS=$(curl -s -H "Metadata-Flavor: Google" $META/parcs-args)

# COS за замовчуванням блокує майже весь вхідний трафік (власний iptables, окремо від фаєрвола GCP).
# Дозволяємо: усе з внутрішньої мережі (воркери <-> master) і порт 8080 (веб master).
# Ззовні все одно діє фаєрвол GCP (правило parcs-web: лише ваша IP).
iptables -w -C INPUT -s 10.0.0.0/8 -j ACCEPT 2>/dev/null || iptables -w -I INPUT -s 10.0.0.0/8 -j ACCEPT
iptables -w -C INPUT -p tcp --dport 8080 -j ACCEPT 2>/dev/null || iptables -w -I INPUT -p tcp --dport 8080 -j ACCEPT

export HOME=/home/chronos                       # у COS домашня папка root недоступна для запису
docker-credential-gcr configure-docker --registries=europe-central2-docker.pkg.dev   # доступ до Artifact Registry

docker rm -f parcs 2>/dev/null                  # прибрати старий контейнер (якщо VM перезапускалась)
# --net=host: контейнер бачить мережу VM (PARCS сам визначає свою IP через hostname -I)
docker run -d --name parcs --restart=always --net=host -e PARCS_ARGS="$ARGS" $IMAGE
