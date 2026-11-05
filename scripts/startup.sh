#!/bin/bash
META=http://metadata.google.internal/computeMetadata/v1/instance/attributes
IMAGE=$(curl -s -H "Metadata-Flavor: Google" $META/parcs-image)
ARGS=$(curl -s -H "Metadata-Flavor: Google" $META/parcs-args)

iptables -w -C INPUT -s 10.0.0.0/8 -j ACCEPT 2>/dev/null || iptables -w -I INPUT -s 10.0.0.0/8 -j ACCEPT
iptables -w -C INPUT -p tcp --dport 8080 -j ACCEPT 2>/dev/null || iptables -w -I INPUT -p tcp --dport 8080 -j ACCEPT

export HOME=/home/chronos
docker-credential-gcr configure-docker --registries=europe-central2-docker.pkg.dev

docker rm -f parcs 2>/dev/null
docker run -d --name parcs --restart=always --net=host -e PARCS_ARGS="$ARGS" $IMAGE
