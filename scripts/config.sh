#!/bin/bash
# Спільні налаштування для всіх скриптів (змінюйте тут).
PROJECT=project-91744d99-04e8-40e9-9db
REGION=europe-central2
ZONE=europe-central2-a
MACHINE=e2-medium                      # 2 vCPU, 4 ГБ - дешево, але вистачає
REPO=parcs                             # репозиторій образів в Artifact Registry
IMAGE=$REGION-docker.pkg.dev/$PROJECT/$REPO/parcs-sobel-node:latest
MASTER=parcs-master
WORKERS="parcs-worker-1 parcs-worker-2 parcs-worker-3 parcs-worker-4"
ALL_VMS="$MASTER $WORKERS"
