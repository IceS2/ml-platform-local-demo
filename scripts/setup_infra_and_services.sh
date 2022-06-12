#!/bin/bash

# Init KinD Cluster
kind create cluster \
  --name default \
  --config infrastructure/k8s_cluster.yaml

kubectl config use-context kind-default

# Add Ingress Controller
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --version v4.0.6 \
  -f services/nginx_ingress/values.yaml

kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# Add Observability Services
# Using ELK Stack
helm repo add elastic https://helm.elastic.co

# Elasticsearch
helm upgrade --install elasticsearch elastic/elasticsearch \
  --namespace observability --create-namespace \
  -f services/observability/elasticsearch/values.yaml

kubectl wait --namespace observability \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=elasticsearch \
  --timeout=300s

# Filebeat
helm upgrade --install filebeat elastic/filebeat \
  --namespace observability \
  -f services/observability/filebeat/values.yaml

# Logstash
helm upgrade --install logstash elastic/logstash \
  --namespace observability \
  -f services/observability/logstash/values.yaml

# Kibana
helm upgrade --install kibana elastic/kibana \
  --namespace observability \
  -f services/observability/kibana/values.yaml

# Add Model Registry Database
helm repo add bitnami https://charts.bitnami.com/bitnami

helm upgrade --install model-registry bitnami/postgresql \
  --namespace model-registry --create-namespace \
  -f services/model_registry/values.yaml

kubectl wait --namespace model-registry \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/instance=model-registry \
  --timeout=300s

