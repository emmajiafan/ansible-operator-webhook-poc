#!/usr/bin/bash -x

# This script can be used for manual testing with a kind cluster
# Run kind create cluster before this script

VERSION=${1:-v1.0}

export WEBHOOK_IMAGE=docker.io/fabianvf/webhooks:${VERSION} \
       OPERATOR_IMAGE=docker.io/fabianvf/validating-operator:${VERSION} \
       OPERATOR_PULL_POLICY=Never \
       KUBECONFIG=$(pwd)/config \
       K8S_AUTH_KUBECONFIG=$(pwd)/config

docker build -f build/webhooks.Dockerfile -t docker.io/fabianvf/webhooks:${VERSION} . 
docker build -f build/Dockerfile -t docker.io/fabianvf/validating-operator:${VERSION} . 
kind load docker-image docker.io/fabianvf/webhooks:${VERSION}
kind load docker-image docker.io/fabianvf/validating-operator:${VERSION}

molecule ${2:-test} -s cluster
