#!/usr/bin/env bash
# Provision the faithfulness verifier on the asrock B550 (Gentoo / OpenRC).
# ── RUN THIS AS ROOT ON asrock ──  e.g.:  sudo bash provision-verifier-asrock.sh
# (Claude staged the service code + Python deps as `chris` already; this script does
#  only the parts that need root: Ollama install + the OpenRC service.)
#
# What it does, in order:
#   1. Enable the GURU community overlay (where app-misc/ollama lives — it is NOT in
#      the main gentoo repo) and sync it.
#   2. Keyword + emerge app-misc/ollama, enable & start its OpenRC service.
#   3. Pull the 7B judge model (~4.5 GB) onto the RTX 3060 Ti.
#   4. Install the verifier-service into /opt + its OpenRC unit, start it on :8007.
#
# If you'd rather NOT add the GURU overlay, stop and tell Claude — the verifier can
# point at any OpenAI-compatible endpoint instead (JUDGE_BACKEND=openai). Review before
# running; nothing here is irreversible but it does add an overlay + a package.
set -euo pipefail

MODEL="qwen2.5:7b-instruct-q4_K_M"
STAGE="/home/chris/verifier-staging"
OPTDIR="/opt/verifier-service"

[ "$(id -u)" -eq 0 ] || { echo "Run as root (sudo)."; exit 1; }
[ -d "$STAGE" ] || { echo "Staging dir $STAGE missing — Claude should re-stage the code."; exit 1; }

echo "==> [1/4] GURU overlay (declarative repos.conf — no eselect-repository needed)"
# asrock has git but not app-eselect/eselect-repository, so add GURU the IaC way:
# a committed repos.conf entry + git sync. Idempotent.
mkdir -p /etc/portage/repos.conf
if [ ! -f /etc/portage/repos.conf/guru.conf ]; then
  cat > /etc/portage/repos.conf/guru.conf <<'CONF'
[guru]
location = /var/db/repos/guru
sync-type = git
sync-uri = https://github.com/gentoo/guru.git
auto-sync = yes
CONF
fi
emaint sync -r guru

echo "==> [2/4] app-misc/ollama"
mkdir -p /etc/portage/package.accept_keywords
echo "app-misc/ollama ~amd64" > /etc/portage/package.accept_keywords/ollama

echo "    --- build plan (review before installing) ---"
emerge -pv app-misc/ollama || true
echo "    ---------------------------------------------"
echo "    NOTE: GPU use on the 3060 Ti needs the 'cuda' USE flag, which can pull a"
echo "    large CUDA toolkit. Review the plan above. CPU-only ollama also works (slower)."
if [ "${CONFIRM:-0}" != "1" ]; then
  echo ""
  echo "    Nothing installed yet. GURU overlay is now synced. To proceed, re-run with:"
  echo "        sudo CONFIRM=1 ./provision-verifier-asrock.sh"
  echo "    (optionally first: echo 'app-misc/ollama cuda' >> /etc/portage/package.use/ollama  for GPU)"
  exit 0
fi

emerge -q app-misc/ollama
[ -f /etc/init.d/ollama ] && { rc-update add ollama default 2>/dev/null || true; rc-service ollama start || rc-service ollama restart; } \
  || echo "    NOTE: no /etc/init.d/ollama — start ollama however the ebuild documents."
echo "    waiting for ollama API..."
for _ in $(seq 1 30); do curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && break; sleep 2; done

echo "==> [3/4] pull judge model ${MODEL} (~4.5 GB)"
ollama pull "${MODEL}"

echo "==> [4/4] install verifier-service -> ${OPTDIR} (runs as chris on :8007)"
mkdir -p "${OPTDIR}"
cp "${STAGE}/verifier.py" "${STAGE}/verifier_core.py" "${OPTDIR}/"
chown -R chris:chris "${OPTDIR}"
chmod +x "${OPTDIR}/verifier.py"
cp "${STAGE}/verifier-service.openrc" /etc/init.d/verifier-service
chmod 755 /etc/init.d/verifier-service
rc-update add verifier-service default 2>/dev/null || true
rc-service verifier-service restart 2>/dev/null || rc-service verifier-service start

echo "==> health:"
sleep 2
curl -sf http://127.0.0.1:8007/health && echo || echo "UNREACHABLE — check: rc-service verifier-service status"
echo "==> Done. Tell Claude; it will run the judge-accuracy fixtures gate next."
