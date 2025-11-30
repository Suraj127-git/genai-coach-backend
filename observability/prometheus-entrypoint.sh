#!/bin/sh
set -e

# Replace environment variable in config
sed "s/\${GRAFANA_TOKEN}/$GRAFANA_TOKEN/g" /etc/prometheus/prometheus.yml > /tmp/prometheus.yml

# Start Prometheus
exec prometheus \
  --config.file=/tmp/prometheus.yml \
  --storage.tsdb.path=/prometheus \
  --web.enable-lifecycle \
  --web.listen-address=:9090