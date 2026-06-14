# Portfolio Polish Plan — dev.cwetzel.com

**Goal:** Transform the chat demo into a polished professional portfolio that communicates who Chris is,
demonstrates the infrastructure he built, and leaves a strong impression on technical visitors and recruiters.

---

## Phase 1 — Suggested Starter Questions

**Priority:** Highest  
**Effort:** Low (~1 hour)  
**Impact:** Visitors don't know what to ask. Starter chips immediately demonstrate the system's depth
and reduce abandonment from a blank chat box.

### What to build
Three to five clickable question chips rendered below the empty-state message and hidden once the
conversation starts. Clicking a chip fires it as a user message.

### Questions to include (draft)
- "What has Chris built?"
- "Tell me about the T5810 GPU setup"
- "What is psaios?"
- "What does Chris's home lab look like?"
- "What languages and tools does Chris use?"

### Files to change
- `frontend/src/components/ChatWindow.jsx` — render chips in empty state
- `frontend/src/pages/Chat.jsx` — wire chip click → sendMessage

### Notes
- Chips should disappear on first message (controlled by `messages.length === 0`)
- Style as pill buttons, consistent with existing dark theme

---

## Phase 2 — Loading / Typing Indicator

**Priority:** High  
**Effort:** Low (~1–2 hours)  
**Impact:** The pause between sending a message and the first token arriving looks like a broken page.
A visible indicator sets expectations and makes the system feel alive.

### What to build
Two distinct states:
1. **Searching** — shown immediately on send, before vLLM responds: "Searching knowledge base..."
2. **Generating** — shown once the WebSocket stream opens but before first token: animated typing dots

### Implementation
- Add a `status` field to `useChat.js` state: `idle | searching | generating`
- Set `searching` on send, `generating` on first WebSocket chunk received, `idle` on `done`
- Render a status bubble in `ChatWindow.jsx` when `status !== 'idle'`
- Animate with a simple CSS pulse or three-dot bounce (Tailwind `animate-bounce`)

### Files to change
- `frontend/src/hooks/useChat.js` — add status state, update on WS events
- `frontend/src/components/ChatWindow.jsx` — render status bubble
- `frontend/src/pages/Chat.jsx` — pass status down

---

## Phase 3 — Hero Header

**Priority:** High  
**Effort:** Low–Medium (~2–3 hours)  
**Impact:** First impression. A visitor should understand within 5 seconds who Chris is, what this system
does, and why the AI chat is impressive — not just see a blank input box.

### What to build
A compact header above the chat window containing:
- Name and one-line role: "Chris Wetzel — Infrastructure & AI Engineer"
- Two-sentence description of what the AI knows and what powers it
- Three icon links: GitHub, LinkedIn, email
- A subtle "Powered by Qwen 14B on 2× A4500 GPUs" tag — the meta-story is the portfolio piece

### Design notes
- Keep it compact — one viewport height should show header + chat input + first message
- Dark theme consistent with existing UI
- The tech stack tag communicates the depth of the build without requiring explanation

### Files to change
- `frontend/src/pages/Chat.jsx` or new `frontend/src/components/Header.jsx`
- `frontend/src/App.jsx` if layout changes are needed

---

## Phase 4 — Audit and Expand Knowledge Base

**Priority:** High  
**Effort:** Medium (~half day to full day)  
**Impact:** The model is only as good as what's in Qdrant. If key projects, case studies, or skills are
missing from the index, the AI will either hallucinate or correctly say it doesn't know — both are bad
for a portfolio demo.

### Audit steps
1. Query Qdrant for collection stats: `GET /collections/documents` — check vector count and payload fields
2. Sample 10–20 documents: review titles, sources, and content length
3. Identify gaps: résumé, GitHub projects, psaios, pscode, infrastructure case studies, skills list

### Content to add / verify is indexed
- Résumé / CV (skills, experience, education)
- psaios project description and architecture
- pscode project description
- T5810 / home lab infrastructure write-up
- Key GitHub repos (READMEs at minimum)
- `pxx_docs/` directory (already in repo, confirm indexed)
- Any case studies or blog posts

### Re-indexing approach
- Review existing indexing scripts (check `scripts/`, `src/data/knowledge_base/`)
- Add missing documents as structured markdown files
- Re-run the indexer against the embed service (port 8005) → Qdrant

### Notes
- Chunk size matters: 512–1024 tokens per chunk with overlap works well for RAG
- Each chunk should carry `title`, `source`, and `content` in the Qdrant payload (matches what api-proxy.py expects)

---

## Phase 5 — "About This System" Tech Stack Panel

**Priority:** High  
**Effort:** Low (~1–2 hours)  
**Impact:** The infrastructure story IS the portfolio piece for a technical audience. Surfacing it
turns a chat demo into a demonstration of deep systems knowledge.

### What to build
A collapsible or always-visible panel (sidebar or below-the-fold section) listing:

```
Inference     Qwen 2.5 Coder 14B Instruct
Hardware      2× NVIDIA RTX A4500 (NVLink, 40 GB total VRAM)
Host          Dell Precision T5810 — Gentoo Linux
GPU Serving   vLLM v0.14 — tensor parallel, enforce_eager
RAG           Qdrant vector DB + BAAI bge-small-en-v1.5 embeddings
Proxy         FastAPI on cloud VPS — SSH tunnel to home GPU
Frontend      React + Vite + Tailwind CSS
```

### Design notes
- Could be a drawer, a footer, or a small "ℹ️ About this system" toggle
- Should be visible without disrupting the chat UX
- Link "View on GitHub" if the repo is public

### Files to change
- New `frontend/src/components/SystemInfo.jsx`
- `frontend/src/pages/Chat.jsx` — integrate component

---

## Phase 6 — Error Recovery / Reconnect

**Priority:** Medium  
**Effort:** Medium (~2–3 hours)  
**Impact:** WebSocket connections drop — network blips, server restarts, tunnel hiccups. Currently the
user is silently stuck with no feedback and no way to recover without a page refresh.

### What to build
- Detect WebSocket close with code 1006 (abnormal closure) in `useChat.js`
- Show an inline error message in the chat: "Connection lost — [Retry]"
- "Retry" button re-sends the last user message
- Exponential backoff reconnect: 1s → 2s → 4s, max 3 attempts before showing manual retry
- Distinguish server error (5xx from proxy) from connection drop — show different messages

### Files to change
- `frontend/src/hooks/useChat.js` — reconnect logic, error state
- `frontend/src/components/ChatWindow.jsx` — error bubble with retry button

### Notes
- The last user message should be preserved in state so retry can re-send it
- Do not auto-retry indefinitely — after 3 attempts, require manual action

---

## Phase 7 — Copy Button on Code Blocks

**Priority:** Medium  
**Effort:** Low (~1 hour)  
**Impact:** Standard expectation for any chat interface that returns code. Missing it reads as unfinished.

### What to build
A "Copy" button in the top-right corner of every fenced code block. Clicking copies the raw code
to clipboard and briefly shows "Copied ✓" confirmation.

### Implementation
- Extend the `CodeBlock` component in `ChatWindow.jsx`
- Use `navigator.clipboard.writeText()` (requires HTTPS — already satisfied on dev.cwetzel.com)
- Button: absolute-positioned top-right inside the SyntaxHighlighter wrapper div
- State: `copied` boolean per block, reset after 2 seconds

### Files to change
- `frontend/src/components/ChatWindow.jsx` — update `CodeBlock` component

---

## Phase 8 — Disable enforce_eager, Enable CUDA Graphs

**Priority:** Medium  
**Effort:** Medium (~2–4 hours including testing)  
**Impact:** `enforce_eager=1` was set in `/etc/conf.d/pscode-vllm` as a workaround for tight VRAM
during cudagraph capture. With PSCODE_GPU_UTIL=0.90 and LightDM gone, there may be enough headroom
to enable CUDA graphs and get a meaningful throughput boost (estimated 20–40% more tokens/sec).

### Steps
1. Set `PSCODE_ENFORCE_EAGER=0` in `/etc/conf.d/pscode-vllm`
2. Restart `pscode-vllm` and monitor logs for cudagraph capture errors
3. If capture fails with OOM: try reducing `PSCODE_GPU_UTIL` to 0.85 first, then retry
4. If capture succeeds: benchmark token throughput before and after
5. If unstable: revert to `PSCODE_ENFORCE_EAGER=1`

### Risk
Low — easy to revert. CUDA graph capture happens at startup, failure is logged clearly.

### Files to change
- `/etc/conf.d/pscode-vllm` on T5810 (server-side, not in repo)

---

## Phase 9 — Parallelize RAG Search with Stream Start

**Priority:** Medium  
**Effort:** Medium (~2–3 hours)  
**Impact:** Currently `api-proxy.py` runs RAG (embed query → Qdrant search) sequentially before opening
the vLLM stream. The embed + search adds 200–500ms of latency the user feels as a blank pause after
sending. Parallelizing or pipelining this removes that gap.

### Option A — Parallel embed + pre-warm (recommended)
Start the vLLM connection while the RAG search is in flight. Hold the stream until the system prompt
with context is assembled, then send. The TCP connection setup time is hidden behind the RAG latency.

### Option B — Stream a status message first
Open the stream immediately, send a synthetic `searching...` chunk to the frontend, then inject the
real content once RAG completes. More complex, lower actual latency gain.

### Option A implementation
- In `websocket_chat`, wrap `search_knowledge_base()` and the `httpx.AsyncClient` setup in
  `asyncio.gather()` so they run concurrently
- Only the actual POST to `/v1/chat/completions` must wait for the context docs

### Files to change
- `cloud/api-proxy.py` — refactor WebSocket handler

---

## Phase 10 — Mobile Polish

**Priority:** Medium  
**Effort:** Medium (~2–3 hours)  
**Impact:** Many portfolio visitors will check on a phone. The current layout (max-w-2xl bubbles,
fixed-width panels) may be awkward or broken on small screens.

### What to audit
- Chat bubble max-width on mobile (should be ~90vw not fixed 2xl)
- Input area: textarea height, send button tap target (minimum 44×44px)
- Header (Phase 3): should collapse gracefully on small screens
- System info panel (Phase 5): should be hidden or collapsed by default on mobile
- Suggested chips (Phase 1): should wrap cleanly, not overflow

### Implementation approach
- Add responsive Tailwind classes (`sm:`, `md:`) where currently missing
- Test with Chrome DevTools device simulation at 375px (iPhone SE) and 390px (iPhone 15)
- Verify the WebSocket chat works on mobile Safari (some quirks with WS + SSL)

### Files to change
- `frontend/src/components/ChatWindow.jsx`
- `frontend/src/components/Header.jsx` (Phase 3)
- `frontend/src/pages/Chat.jsx`

---

## Summary Table

| Phase | Item | Effort | Files |
|---|---|---|---|
| 1 | Suggested starter questions | Low | ChatWindow.jsx, Chat.jsx |
| 2 | Loading / typing indicator | Low | useChat.js, ChatWindow.jsx |
| 3 | Hero header | Low–Med | Header.jsx (new), Chat.jsx |
| 4 | Audit + expand knowledge base | Medium | Knowledge base content + indexer |
| 5 | "About this system" panel | Low | SystemInfo.jsx (new), Chat.jsx |
| 6 | Error recovery / reconnect | Medium | useChat.js, ChatWindow.jsx |
| 7 | Copy button on code blocks | Low | ChatWindow.jsx |
| 8 | Disable enforce_eager / CUDA graphs | Medium | /etc/conf.d/pscode-vllm (T5810) |
| 9 | Parallelize RAG + stream start | Medium | cloud/api-proxy.py |
| 10 | Mobile polish | Medium | ChatWindow.jsx, Chat.jsx, Header.jsx |
