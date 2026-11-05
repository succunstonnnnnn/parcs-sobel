#!/bin/bash
# ВИДАЛЯЄ ВСЕ, що створив setup.sh: VM, правило фаєрвола, репозиторій образів. Незворотно!
cd "$(dirname "$0")"
source config.sh
read -p "Видалити всі VM, фаєрвол і репозиторій $REPO? Введіть yes: " answer
[ "$answer" = "yes" ] || { echo "Скасовано"; exit 1; }
gcloud compute instances delete $ALL_VMS --zone $ZONE --quiet
gcloud compute firewall-rules delete parcs-web --quiet
gcloud artifacts repositories delete $REPO --location=$REGION --quiet
echo "Усе видалено."
