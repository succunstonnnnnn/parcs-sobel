#!/bin/bash
cd "$(dirname "$0")"
source config.sh
gcloud compute instances stop $ALL_VMS --zone $ZONE
