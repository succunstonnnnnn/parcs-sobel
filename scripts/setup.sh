#!/bin/bash
# Створює все в Google Cloud: репозиторій образів, фаєрвол, 1 master + 4 workers.
set -e                                  # зупинитись при першій помилці
cd "$(dirname "$0")"
source config.sh

gcloud config set project $PROJECT
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE

# 1. Репозиторій для Docker-образу (потрібен, бо в образі є numpy, якого немає в стандартному)
gcloud services enable artifactregistry.googleapis.com
gcloud artifacts repositories create $REPO --repository-format=docker --location=$REGION || true
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

# 2. Збираємо образ (платформа linux/amd64 - як у віртуалок) і заливаємо
docker build --platform linux/amd64 -t $IMAGE ../docker
docker push $IMAGE

# 3. Фаєрвол: вебінтерфейс (8080) і ssh (22) лише з вашої IP. Між VM все вже дозволено правилом default-allow-internal.
MY_IP=$(curl -s https://api.ipify.org)
gcloud compute firewall-rules create parcs-web --network=default --direction=INGRESS \
  --action=ALLOW --rules=tcp:8080,tcp:22 --source-ranges=$MY_IP/32 --target-tags=parcs || true

# 4. Функція створення VM. Це звичайна VM з Container-Optimized OS (в ній вже є Docker);
#    образ і аргументи PARCS передаємо через метадані, а startup.sh запускає контейнер.
#    --scopes=cloud-platform дозволяє VM завантажити образ з Artifact Registry.
#    (Спосіб з README "create-with-container" Google вже вимкнув.)
create_vm() {   # $1 = ім'я VM, $2 = аргументи PARCS
  gcloud compute instances create $1 \
    --machine-type=$MACHINE --tags=parcs --scopes=cloud-platform \
    --image-family=cos-stable --image-project=cos-cloud \
    --metadata-from-file=startup-script=startup.sh \
    --metadata=parcs-image=$IMAGE,parcs-args="$2"
}

create_vm $MASTER "master"

# 5. Беремо ВНУТРІШНЮ IP master (вона не змінюється після stop/start) і передаємо воркерам
MASTER_IP=$(gcloud compute instances describe $MASTER --format="value(networkInterfaces[0].networkIP)")
echo "Внутрішня IP master: $MASTER_IP"
for w in $WORKERS; do
  create_vm $w "worker $MASTER_IP"
done

gcloud compute instances list
