#!/bin/bash
# Зупиняє всі VM (обчислення не оплачуються, лишаються тільки диски).
cd "$(dirname "$0")"
source config.sh
gcloud compute instances stop $ALL_VMS --zone $ZONE
