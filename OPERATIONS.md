# Portfolio AI - Operations & Monitoring

**Status:** MVP Infrastructure Complete (GATE 2.5)  
**Endpoint:** https://dev.cwetzel.com  
**Stack:** React (frontend) → Apache (proxy) → FastAPI (backend) → pscode vLLM (inference)

---

## System Status

### Services (cwetzel.com)

| Service | Port | Status | Auto-start | Restart |
|---------|------|--------|-----------|---------|
| api-proxy | 8000 | ✅ Running | ✅ Enabled | Always |
| apache2 | 80/443 | ✅ Running | ✅ Enabled | On-failure |
| portfolio-ai-tunnel | 8001/8004/8005/8006/6333/8007 | ✅ Running | ✅ Enabled | Always |
| portfolio-health.timer | — | ✅ Running | ✅ Enabled | Timer (5 min) |

### Services (T5810)

| Service | Port | Status | Usage |
|---------|------|--------|-------|
| pscode vLLM | 8004 | ✅ Running | BF16, 16K context, 18GB/GPU |
| Qdrant | 6333 | ✅ Running | Vector DB — `home/qdrant/qdrant.openrc` (IaC) |
| embed-service | 8005 | ✅ Running | BAAI/bge-base-en-v1.5, 768-d (CPU) |
| rerank-service | 8006 | ✅ Running | bge-reranker-base (CPU) |

### Services (asrock B550 — verifier node)

| Service | Port | Status | Usage |
|---------|------|--------|-------|
| verifier-service | 8007 | ✅ Running | Out-of-band faithfulness judge (fail-open). Binds `VERIFIER_BIND` (LAN IP, not 0.0.0.0); reached via the tunnel's `-L 8007`. |

---

## Monitoring Commands

### Check all services running

```bash
# Quick status
ssh root@cwetzel.com "systemctl status api-proxy apache2 portfolio-ai-tunnel"

# Port status
ssh root@cwetzel.com "ss -tlnp | grep -E ':(8000|80|443)'"
```

### Check vLLM connectivity

```bash
# From cwetzel.com
ssh root@cwetzel.com "curl -s http://ai.cwetzel.com:8004/v1/models | head -c 100"

# From T5810 (for debugging)
ssh root@t5810.local "curl -s http://localhost:8004/v1/models | head -c 100"
```

### Check tunnel status

```bash
# Tunnel process
ssh root@cwetzel.com "ps aux | grep ssh | grep -v grep | grep tunnel"

# Tunnel logs (last 20 lines)
ssh root@cwetzel.com "journalctl -u portfolio-ai-tunnel -n 20 --no-pager"
```

### Check proxy logs

```bash
# Real-time FastAPI logs
ssh root@cwetzel.com "journalctl -u api-proxy -f"

# Real-time Apache logs
ssh root@cwetzel.com "tail -f /var/log/apache2/access.log"
```

---

## Automated Health Monitoring & Alerting

**Motivation:** the 2026-06-14 outage — Qdrant crash-looped and latched off, so every query
answered *"I don't have that documented in my knowledge base"* — went undetected because nothing
paged a human and the per-service `/health` endpoints all return a trivial `{"status":"ok"}` that
can't see a Qdrant serving 0 points. This layer fixes that.

**Design:** monitor + **alert only** (no auto-restart of stateful services — a blind respawn loop
is what hid the outage). One deep VPS-side aggregator covers every failure mode reachable through
the tunnel; an external dead-man's switch covers the VPS itself dying; a home-side canary is the
second, public-path vantage.

### Components

| Component | Where | Schedule | What it catches |
|-----------|-------|----------|-----------------|
| `scripts/health_aggregate.py` (`portfolio-health.timer`) | VPS | every 5 min | cheap probes: proxy, vLLM (`/v1/models`), **Qdrant points_count**, embed, rerank, verifier (`--no-smoke` — no LLM load) |
| `portfolio-health-heartbeat.timer` | VPS | daily 12:00 UTC | full run **incl. E2E WS query**; sends one "all green" ntfy/day so silence never means "monitor dead"; feeds healthchecks.io |
| `portfolio-health-alert.service` | VPS | `OnFailure=` | monitor-of-monitor: pages if the probe process itself crashes |
| healthchecks.io ping | external | on every green run | dead-man's switch — alerts if the VPS/monitor stops pinging |
| `scripts/selftest-canary.sh` (cron) | T5810 | every 30 min | public Apache→proxy→tunnel path (SSL/DNS) from the home network |

**Alert channel:** ntfy.sh push to a private topic. Config (not in the repo):
`/etc/default/portfolio-health` on the VPS (`NTFY_URL`, `HEALTHCHECKS_URL`) and
`/etc/portfolio-canary.env` on the T5810 (`NTFY_URL`). Alerts fire **only on state transitions**
(healthy→down pages; down→healthy sends "recovered") — a sustained outage is not re-paged every cycle.

### Severity map (what pages vs. what doesn't)

| Signal | Severity | Pages? |
|--------|----------|--------|
| tunnel down / proxy / vLLM / embed down | CRITICAL | yes |
| **Qdrant up but points_count == 0** (the outage signature) | CRITICAL | yes |
| E2E smoke: a grounded question returns the fallback | CRITICAL | yes |
| rerank down (fails open to cosine order) | DEGRADED | heartbeat only |
| verifier / Ollama down (fail-open, chat unaffected) | INFO | no |

### Provisioning / commands

```bash
# Install/refresh the VPS monitor (deploys scripts + systemd units, seeds config):
./cloud/setup-health-monitor.sh

# One-off manual probe (prints per-service status; exit 1 if any CRITICAL):
ssh root@cwetzel.com "cd /opt/portfolio-health && python3 health_aggregate.py"

# Monitor logs:
ssh root@cwetzel.com "journalctl -u portfolio-health.service -n 30 --no-pager"

# Install the durable Qdrant unit on the T5810 (see runbook below):
./home/setup-qdrant.sh
```

---

## Restart Procedures

### Restart specific service

```bash
# FastAPI proxy
ssh root@cwetzel.com "systemctl restart api-proxy"

# Apache
ssh root@cwetzel.com "systemctl restart apache2"

# SSH tunnel
ssh root@cwetzel.com "systemctl restart portfolio-ai-tunnel"
```

### Full stack restart (if needed)

```bash
ssh root@cwetzel.com "systemctl restart portfolio-ai-tunnel api-proxy apache2"
sleep 5
# Verify
ssh root@cwetzel.com "systemctl status api-proxy apache2 portfolio-ai-tunnel"
```

---

## Performance Metrics

### Response latency (from user browser)

- Frontend load: <1s (static HTML + Tailwind CDN)
- API response: <2s (vLLM p50 latency <100ms + network overhead)
- WebSocket streaming: Real-time token generation

### System load

```bash
# cwetzel.com (1 core, 1GB RAM)
ssh root@cwetzel.com "uptime && free -h"

# T5810 (44 cores, lots of RAM)
ssh root@t5810.local "uptime && nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv"
```

### Tunnel health

```bash
ssh root@cwetzel.com "journalctl -u portfolio-ai-tunnel --since='1 hour ago' | grep -i 'error\|fail' || echo 'No errors in last hour'"
```

---

## Troubleshooting

### Frontend not loading

```bash
# Check Apache vhost
ssh root@cwetzel.com "apache2ctl configtest"
ssh root@cwetzel.com "ls -la /var/www/dev.cwetzel.com/"

# Check SSL cert
ssh root@cwetzel.com "openssl s_client -connect dev.cwetzel.com:443 -brief"
```

### Chat not responding

```bash
# Check FastAPI health
ssh root@cwetzel.com "curl -s http://127.0.0.1:8000/health"

# Check vLLM via tunnel
ssh root@cwetzel.com "curl -s -m 5 http://ai.cwetzel.com:8004/v1/models | head -c 50"

# Check tunnel connectivity
ssh root@cwetzel.com "journalctl -u portfolio-ai-tunnel -n 5 --no-pager"
```

### Every query answers "I don't have that documented" (Qdrant latched off — 2026-06-14 outage class)

Signature: the site loads and streams, but **every** answer is the fallback refusal. Root cause is
almost always retrieval returning empty — usually Qdrant down or serving 0 points.

```bash
# 1. Confirm which stage is broken (from the VPS, through the tunnel):
ssh root@cwetzel.com "cd /opt/portfolio-health && python3 health_aggregate.py"
#    Look for: [CRITICAL] Qdrant unreachable  OR  points_count=0

# 2. On the T5810, inspect + recover Qdrant:
ssh root@ai.cwetzel.com "tail -n 30 /var/log/qdrant.log"     # look for PermissionDenied on ./snapshots
ssh root@ai.cwetzel.com "rc-service qdrant status"
ssh root@ai.cwetzel.com "rc-service qdrant zap && rc-service qdrant start"   # zap clears a crashed/latched state

# 3. Verify it came back green with points:
ssh root@ai.cwetzel.com "curl -s http://127.0.0.1:6333/collections/documents | head -c 300"
#    Expect: status:green, points_count > 0

# 4. If it crash-loops on a PermissionDenied for ./snapshots/tmp, the OLD init bug is present.
#    Install the durable unit (correct CWD + logging, clears the stale root-owned /snapshots):
./home/setup-qdrant.sh

# 5. If Qdrant is green but points_count is 0, the collection is empty — rebuild the index:
./scripts/reindex_kb.sh
```

The durable fix (`home/qdrant/qdrant.openrc`) sets the daemon's CWD to `/home/chris/qdrant-data`
so its relative `./snapshots` cleanup can never again hit the root-owned `/snapshots`, and uses
`output_log`/`error_log` instead of a shell redirect passed as bogus argv.

### High latency or timeouts

```bash
# Check T5810 GPU memory
ssh root@t5810.local "nvidia-smi"

# Check T5810 load
ssh root@t5810.local "uptime"

# Check network between cwetzel.com and T5810
ssh root@cwetzel.com "ping -c 1 98.110.86.95"
```

---

## Deployment Checklist

### Initial Setup ✅

- [x] SSH tunnel (cwetzel.com ↔ T5810)
- [x] FastAPI proxy running
- [x] Apache vhost configured
- [x] SSL certificate issued
- [x] Frontend deployed

### Manual QA ⏳

- [ ] Load https://dev.cwetzel.com in browser
- [ ] Click "Start Chat"
- [ ] Type a question (e.g., "What is RAG?")
- [ ] Confirm response streams in real-time
- [ ] Check no JavaScript errors (DevTools console)
- [ ] Test mobile responsiveness

### Performance Validation ⏳

- [ ] Measure first-token latency (should be <100ms)
- [ ] Measure sustained throughput (should be >50 tokens/sec)
- [ ] Monitor for any connection drops over 5 min conversation
- [ ] Check system load on T5810 during sustained usage

### Production Checklist (Later)

- [x] Set up monitoring/alerting (deep health aggregator + ntfy + healthchecks.io dead-man's switch; see "Automated Health Monitoring & Alerting")
- [ ] Configure log rotation
- [ ] Set up automated backups
- [ ] Prepare runbooks for common incidents
- [ ] Plan capacity scaling
- [ ] DNS cutover to cwetzel.com

---

## Uptime Target

**MVP:** 99%+ uptime (auto-restart on failure)  
**Goal:** All services remain running across reboots

---

## Contact

For infrastructure issues, check logs above. For model issues (vLLM), contact whoever manages pscode (T5810).

**Last Updated:** 2026-07-02
