# GitTree-CVE

**Speculative, sandbox-verified CVE remediation on Nebius Token Factory + NVIDIA Nemotron.**

Dependabot-style tools bump a version string and hope the build survives. Single-threaded coding agents mutate one working tree and can't prove their fix works. GitTree-CVE generates several candidate patches in parallel, forks one network-disabled ConTree VM per candidate from an immutable checkpoint, and only proposes a patch that is **proven to fix the exploit**:

1. **Phase A:** the candidate's regression test must *fail* on the unpatched code. Tests that pass on vulnerable code, or only fail because the test itself is broken (`NameError`, import or collection errors), are rejected.
2. **Phase B:** the patched code plus the full existing suite must *pass*. Existing test files are read-only to the models.
3. **Cross-validation:** each passing patch also runs against every *other* branch's exploit test (including tests from branches whose own patch failed). Only tests that some patch satisfies are counted, so a disputed spec doesn't count against a patch.
4. **Fixed attack catalog:** for known classes (path traversal, SQL injection), deterministic payloads written as code, not by a model, are run against the unpatched code. Every payload that succeeds there must be blocked by the patch. A model only writes a two-function adapter that binds the payloads to the repo's API. This is what catches fixes that pass their own test but still have a hole: in CVE-2007-4559, a `'..' in name` check blocks plain `../` but misses symlink and hardlink members.
5. **Audit:** Nemotron Super scores each verified patch against constraints extracted from live advisories, sees the cross-validation and catalog results, and can veto a patch that still allows the attack.

If nothing survives, the run escalates to Nemotron Ultra (up to 2 attempts) with every branch's sandbox output. When a catalog was validated, it becomes the escalation's regression test, so the model only has to make proven exploits fail. On CVE-2007-4559 this reliably produces `tar.extractall(dest, filter="data")`, the standard fix. If that fails too, the run ends with **"no patch proposed"** rather than a guess.

Track: **Coding & Agentic Engineering**. Tavily integration targets the **Best Use of Tavily** bonus.

## Architecture

```
            ┌────────────── Tavily Search + Extract (live advisories) ──────────────┐
            │                                                                        │
            ▼                                                                        │
  Nemotron 3.5 Lightning ── plan: vuln class -> strategies, severity -> branch count,  │
   (intel planner)          advisory fixed version -> target, constraints -> prompts & audit
            │
            ▼
  ConTree base checkpoint (repo + deps, networking on) ── result_image_uuid
            │
   ┌────────┼─────────┬─────────┐        Nemotron 3 Nano: one candidate per planned strategy
   ▼        ▼         ▼         ▼
 fork A   fork B    fork C    ...      each fork = 2 VM operations, networking.enabled=false:
 (Phase A disposable / Phase B retained)   unpatched+test must FAIL, patched+suite must PASS
   │        │         │                     (branch cards stream to the UI as each finishes)
   └── failed branches: 1 Nano repair round with their own stdout/stderr
            │
  cross-validation matrix: every passing patch x every satisfiable exploit test
            │
  Nemotron 3 Super audit (veto < 60/100) ──> winner ──> SFT dataset ──> Token Factory /v1/files
            │ none approved                                            (+ LoRA job when enabled)
            ▼
  Nemotron 3 Ultra escalation (all sandbox traces) ──> re-verified + re-audited, or "no patch"
```

Every model call is logged with its Token Factory completion ID, token usage and cost. The UI streams this over SSE and shows measured spend per run, typically **$0.001–0.004**.

## Where each sponsor technology lives

| Capability | File |
| - | - |
| ConTree REST: image import, `POST /v1/instances`, operation polling, `networking.enabled=false`, retained vs disposable runs, guest-NIC probe, phase-A classification, cross-checks | [`gittree-cve-backend/app/contree_client.py`](gittree-cve-backend/app/contree_client.py) |
| Docker fallback with the same checkpoint/branch model (`docker commit`, `--network none`, no capabilities) | [`gittree-cve-backend/app/docker_sandbox.py`](gittree-cve-backend/app/docker_sandbox.py) |
| Nemotron tier routing (Lightning planner, Nano fan-out + repair, Super audit, Ultra escalation), JSON mode, reasoning toggles | [`gittree-cve-backend/app/nemotron_router.py`](gittree-cve-backend/app/nemotron_router.py) |
| Tavily Search + Extract | [`gittree-cve-backend/app/tavily_intel.py`](gittree-cve-backend/app/tavily_intel.py) |
| Fixed attack payload templates + adapter contract | [`gittree-cve-backend/app/attack_catalog.py`](gittree-cve-backend/app/attack_catalog.py) |
| Pipeline, audit veto, cost ledger, run recording | [`gittree-cve-backend/app/orchestrator.py`](gittree-cve-backend/app/orchestrator.py) |
| Token Factory post-training (`/v1/files`, `/v1/fine_tuning/jobs`) | [`gittree-cve-backend/app/post_training.py`](gittree-cve-backend/app/post_training.py) |
| Rate limiting, SSE API, GitHub import | [`gittree-cve-backend/app/main.py`](gittree-cve-backend/app/main.py) |
| Zero-key replay of recorded runs | [`gittree-cve-backend/app/replay_fixtures.py`](gittree-cve-backend/app/replay_fixtures.py), [`gittree-cve-backend/data/recorded_runs/`](gittree-cve-backend/data/recorded_runs/) |
| Dashboard | [`gittree-cve-frontend/app/page.tsx`](gittree-cve-frontend/app/page.tsx) |

## How Tavily changes execution (not just context)

The Lightning planner turns Tavily results into a structured plan, and deterministic rules route from it:

- **Vulnerability class → which patch strategies run.** Injection gets parameter binding; crypto/auth gets algorithm pinning; path traversal gets input validation.
- **Severity → how many ConTree branches are forked.** Critical gets 5; medium/low gets 3.
- **Advisory fixed version → overrides the requested target version**, shown in the UI.
- **Extracted constraints → injected into every patch prompt and used as the auditor's veto rubric.**
- **No sources found → the run is marked ungrounded**, with generic strategies and no constraints.

## Run it

### Zero-key judge mode (no API keys, no spend)

```bash
cd gittree-cve-backend && ./demo.sh
```

This replays a recorded real run of CVE-2007-4559. The UI's **Zero-Key Judge Replay Mode** checkbox does the same, and live runs fall back to replay automatically when keys are missing, a rate limit is hit, or an API fails. Replays are labeled as such, and the built-in fixture is used only for CVEs that have no recording; its IDs are prefixed `fixture-`.

### Live

```bash
cd gittree-cve-backend
cp .env.example .env          # add NEBIUS_API_KEY, NEBIUS_PROJECT_ID, TAVILY_API_KEY
python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --port 8000

cd ../gittree-cve-frontend
cp .env.example .env.local    # NEXT_PUBLIC_API_BASE_URL
npm install && npm run dev
```

`GET /api/health` reports which sandbox backend is active and the project's ConTree permissions. With `SANDBOX_BACKEND=auto`, the strongest available backend is used:

1. **ConTree:** VM isolation, when `/whoami` grants `spawn`.
2. **Docker:** containers with `--network none`, all capabilities dropped and memory/CPU/PID limits. They share the host kernel, so this is weaker than a VM.
3. **Local:** only with `ALLOW_LOCAL_SANDBOX=true`. Runs on your machine, with only a network namespace (`unshare --net`) when the kernel allows it. Never enable it on a public deployment.

The UI labels every branch with the backend that ran it.

### Tests

```bash
cd gittree-cve-backend && .venv/bin/python -m pytest -q
```

26 tests, all offline: the phase-A classifier, the two-phase gate, a path-traversal guard, the ConTree REST client against a mock of the documented API, the Docker backend (skipped without a daemon), router helpers, the attack-catalog templates (they must exploit vulnerable code, catch a naive `..` check, and pass on correct fixes), and the API (SSRF guard, replay, rate-limit and concurrency fallback).

### Deploy

- **Backend:** `gittree-cve-backend/Dockerfile`, one worker. Set `ALLOWED_ORIGINS` to the frontend origin and `TRUST_PROXY_HEADERS=true` behind a proxy. For the Docker sandbox, either run the backend directly on a VM with Docker, or mount `/var/run/docker.sock` into the container. Mounting the socket gives the *backend* host-level Docker access; patch code still runs in separate restricted containers.
- **Frontend:** any Next.js host, with `NEXT_PUBLIC_API_BASE_URL` set at build time.
- **Credit protection:** `MAX_LIVE_RUNS_PER_IP_PER_DAY` and `MAX_LIVE_RUNS_GLOBAL_PER_DAY` protect the $50 credit through judging.

## Honest status

- **ConTree:** the integration follows the documented REST API and is tested against a schema-faithful mock. The project's Sandboxes permissions are still pending activation, so the recorded runs used the Docker backend, and their transcripts say so.
- **Nemotron post-training:** Nemotron models are not on Token Factory's fine-tunable list. The flywheel uploads verified examples as a real Token Factory dataset and targets `Qwen/Qwen3-Coder-30B-A3B-Instruct` (LoRA-capable). Job launch is gated behind `LORA_ENABLE_JOB_LAUNCH` and `LORA_MIN_EXAMPLES` because it spends credits.
- **Verification limits:** outside the classes with a fixed attack catalog, verification is only as strong as the generated tests, cross-validation and the auditor.

## License

MIT, see [LICENSE](LICENSE).
