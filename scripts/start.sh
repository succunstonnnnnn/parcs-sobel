#!/bin/bash
cd "$(dirname "$0")"
source config.sh

gcloud compute instances start $ALL_VMS --zone $ZONE

MY_IP=$(curl -s https://api.ipify.org)
gcloud compute firewall-rules update parcs-web --source-ranges=$MY_IP/32

MASTER_EXT=$(gcloud compute instances describe $MASTER --zone $ZONE \
  --format="value(networkInterfaces[0].accessConfigs[0].natIP)")
echo "Чекаю, поки 4 воркери зареєструються на master $MASTER_EXT ..."
for i in $(seq 1 60); do
  n=$(curl -s -m 5 http://$MASTER_EXT:8080/api/worker | grep -o '"id"' | wc -l)
  echo "  воркерів: $n"
  [ "$n" -ge 4 ] && break
  sleep 10
done
echo "Готово. Веб-інтерфейс PARCS: http://$MASTER_EXT:8080"
