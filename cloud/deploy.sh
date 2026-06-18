#!/usr/bin/env bash
# Deploy the Portfolio AI chat to production (cwetzel.com VPS).
#   Frontend: build React  -> rsync to /var/www/dev.cwetzel.com/
#   Backend:  api-proxy.py -> /opt/api-proxy/main.py (+ context_manager.py) -> restart
#
# Separate from this script:
#   - Vector index:  scripts/reindex_kb.sh         (rebuild Qdrant from committed KB)
#   - VPS infra:     cloud/setup-proxy-apache.sh    (apache vhost, cache headers, SSL)
#                    cloud/systemd/*.service         (api-proxy + SSH tunnel units)
#   - T5810 svcs:    home/setup-t5810-services.sh    (embed + rerank services)
#
# Usage:  ./cloud/deploy.sh
# Env:    CLOUD_HOST (default root@cwetzel.com)
set -euo pipefail

CLOUD="${CLOUD_HOST:-root@cwetzel.com}"
WEBROOT="/var/www/dev.cwetzel.com"
APIDIR="/opt/api-proxy"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "${HERE}/.." && pwd)"

echo "==> Building frontend"
( cd "${REPO}/frontend" && npm run build )

echo "==> Deploying frontend -> ${CLOUD}:${WEBROOT}"
rsync -avz --delete "${REPO}/frontend/dist/" "${CLOUD}:${WEBROOT}/"

echo "==> Deploying backend proxy -> ${CLOUD}:${APIDIR}"
# cloud/api-proxy.py deploys as main.py (uvicorn main:app); context_manager.py is imported by it.
scp -q "${HERE}/api-proxy.py"       "${CLOUD}:${APIDIR}/main.py"
scp -q "${HERE}/context_manager.py" "${CLOUD}:${APIDIR}/context_manager.py"
ssh "${CLOUD}" "chown apiproxy:apiproxy ${APIDIR}/main.py ${APIDIR}/context_manager.py && \
  systemctl restart api-proxy.service && sleep 2 && systemctl is-active api-proxy.service"

echo "==> Health check"
ssh "${CLOUD}" "curl -sf http://127.0.0.1:8000/health && echo" || { echo "✗ HEALTH CHECK FAILED"; exit 1; }
echo "==> Deployed: https://dev.cwetzel.com"
