#!/bin/bash
set -e
cd "$(dirname "$0")"
source config.sh

gcloud config set project $PROJECT
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE

gcloud services enable artifactregistry.googleapis.com
gcloud artifacts repositories create $REPO --repository-format=docker --location=$REGION || true
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

docker build --platform linux/amd64 -t $IMAGE ../docker
docker push $IMAGE

MY_IP=$(curl -s https://api.ipify.org)
gcloud compute firewall-rules create parcs-web --network=default --direction=INGRESS \
  --action=ALLOW --rules=tcp:8080,tcp:22 --source-ranges=$MY_IP/32 --target-tags=parcs || true

create_vm() {
  gcloud compute instances create $1 \
    --machine-type=$MACHINE --tags=parcs --scopes=cloud-platform \
    --image-family=cos-stable --image-project=cos-cloud \
    --metadata-from-file=startup-script=startup.sh \
    --metadata=parcs-image=$IMAGE,parcs-args="$2"
}

create_vm $MASTER "master"

MASTER_IP=$(gcloud compute instances describe $MASTER --format="value(networkInterfaces[0].networkIP)")
echo "Внутрішня IP master: $MASTER_IP"
for w in $WORKERS; do
  create_vm $w "worker $MASTER_IP"
done

gcloud compute instances list
