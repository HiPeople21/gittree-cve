# GitTree-CVE

**Speculative, sandbox-verified CVE remediation on Nebius Token Factory + NVIDIA Nemotron.**

![GitTree-CVE replaying a recorded ConTree run of CVE-2007-4559: one fork stopped by its own tests, two re-checked with the attack catalog, one verified and selected](docs/screenshot.png)

Dependabot-style tools bump a version string and hope the build survives. Single-threaded coding agents mutate one working tree and can't prove their fix works. GitTree-CVE generates several candidate patches in parallel, forks one network-disabled ConTree VM per candidate from an immutable checkpoint, and only proposes a patch that is **proven to fix the exploit**:

1. **Phase A:** the candidate's regression test must *fail* on the unpatched code. Tests that pass on vulnerable code, or only fail because the test itself is broken (`NameError`, import or collection errors, or a model answer that couldn't be parsed), are rejected.
2. **Phase B:** the patched code plus the full existing suite must *pass*, and pytest must report every regression test as passed (an exit code of 0 alone is not a pass). The gate reads pytest's output the same way whatever the repository's own pytest config sets (`-q`, `-x`, `--color=yes`, `--tb=no`, `testpaths`, `python_files`).
3. **Patch policy:** a patch may only change the repository's code. These are dropped before anything runs, and listed on the fork with the reason:
   - changes to tests (including files the repository's `python_files` setting collects), `conftest.py` and pytest configuration (including the pytest sections of `pyproject.toml`/`setup.cfg`);
   - interpreter start-up hooks, package metadata and compiled files;
   - a new module that would shadow the standard library, the test runner or one of the repository's own modules from any directory that can be on `sys.path` (test folders, `pythonpath`, `src/`, package directories, the repository root), including a module placed beside a namespace package of the same name;
   - repository code that starts referring to pytest.
4. **Cross-validation:** when at least two branches have a working exploit test of their own, each passing patch also runs against every *other* branch's exploit test (including tests from branches whose own patch failed). Only tests that some patch satisfies are counted, so a disputed spec doesn't count against a patch.
5. **Fixed attack catalog:** for three classes, deterministic payloads written as code, not by a model, are run against the unpatched code. Every payload that succeeds there must be blocked by the patch:
   - **Path traversal** (`tarfile`): `../`, nested `../`, absolute paths, symlink and hardlink members.
   - **SQL injection:** tautology, comment truncation, `UNION`, boolean bypass, keyword-free operator tautologies (`x'<>'y`, `x' IS NOT 'y`, `x' GLOB '*`), a tautology without spaces, a numeric-context tautology (`0 OR 1=1`) and a double-quoted one. These catch the usual keyword, whitespace and operator blacklists that still let a quote through.
   - **JWT signature verification:** a token signed by the wrong RSA key, `alg: none`, HS256 with an attacker secret, tampered claims, HS256 keyed with the server's public key (key confusion), an attacker key embedded in the header (`jwk`), a server-signed token that expired 30 days ago, and a forged token for an ordinary user with no `exp` claim (so a fix that checks signatures only on admin tokens, or only on tokens that carry an expiry, is caught).

   Each class also has a **legitimate-use control**: a normal archive member is extracted, the rows the adapter inserted are found, a token the server really signed is accepted. A patch that breaks it, for example by rejecting everything, gets no credit for any payload.

   A model writes only a small adapter that binds the payloads to the repo's API. A **probe check** confirms at runtime (by profiling which code runs, not by reading imports) that the adapter really calls the repository's code. Otherwise the catalog is discarded and the run says why.

   This is what catches fixes that pass their own test but still have a hole. In our live runs of CVE-2007-4559, Nano patches with a `'..' in name` check passed their own tests, but the catalog showed they missed symlink and hardlink members, and vetoed them.
6. **Audit:** Nemotron Super scores each verified patch against constraints extracted from live advisories, sees the cross-validation and catalog results, and can veto a patch that still allows the attack.

A fork whose patch is right but whose own regression test gave no usable evidence (broken, already passing on the vulnerable code, or failing the same way on the vulnerable and the patched code) is not thrown away. When the catalog validated, the fork is **re-checked** with the catalog as its regression test, before any repair round; the fork is then shown as "re-checked with attack suite". Forks that still fail get one Nano repair round with their own sandbox output.

If nothing survives, the run escalates (up to 2 attempts) with every branch's sandbox output and the reason each was rejected. It goes to Nemotron Ultra, or to Super when `BUDGET_SAVER_DISABLE_ULTRA=true`. When a catalog was validated, it becomes the escalation's regression test, so the model only has to make proven exploits fail. If that fails too, the run ends with **"no patch proposed"** rather than a guess.

**Real repositories in, draft PRs out.** Paste a public GitHub repo URL. GitTree-CVE imports its Python sources and dependencies (read in memory, never extracted to disk), including the pytest plugins it declares (each kept only if pytest still starts with it), and runs the pipeline against the project's own test suite. It can then open a **draft PR** containing:
- the verified patch;
- a regression test file;
- a body citing the evidence: sandbox exit codes, attack-catalog results (or why the catalog did not apply), the audit score and the advisory constraints.

A PR can only carry a patch this server verified (looked up by `run_id`), and only for repo owners on `GITHUB_PR_ALLOWED_OWNERS`. [`examples/vulnerable-demo`](examples/vulnerable-demo) is a ready-made target.

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
   ▼        ▼         ▼         ▼        (+ the attack-catalog adapter, validated on the unpatched code)
 fork A   fork B    fork C    ...      each fork = 2 VM operations, networking.enabled=false:
 (Phase A disposable / Phase B retained)   unpatched+test must FAIL, patched+suite must PASS
   │        │         │                     (fork lanes stream to the UI as each finishes)
   └── re-check: forks whose own test gave no evidence, against the validated attack catalog
            │
  repair: up to 3 failed forks get 1 Nano round with their own stdout/stderr (then re-checked too)
            │
  cross-validation matrix: every passing patch x every satisfiable exploit test
            │
  attack catalog: reproduced payloads must be blocked, legitimate use must keep working
            │
  Nemotron 3 Super audit (veto < 60/100) ──> winner ──> SFT dataset ──> Token Factory /v1/files
            │ none approved                (only if verified with      (+ LoRA job when enabled)
            ▼                               its own regression test)
  escalation (Ultra, or Super on a budget; all sandbox traces) ──> re-verified + re-audited, or "no patch"
```

Every model call is logged with its Token Factory completion ID, token usage and cost. The UI streams this over SSE and shows measured spend per run. In the recorded runs it was **$0.0018–0.0026**. In our other live runs, one that escalated to Super cost $0.0044, and runs that escalated twice and still proposed no patch cost about a cent.

## Where each sponsor technology lives

| Capability | File |
| - | - |
| ConTree REST: image import, `POST /v1/instances`, operation polling, `networking.enabled=false`, retained vs disposable runs, guest-NIC probe, phase-A classification, Phase B integrity, cross-checks | [`gittree-cve-backend/app/contree_client.py`](gittree-cve-backend/app/contree_client.py) |
| Docker fallback with the same checkpoint/branch model (`docker commit`, `--network none`, no capabilities) | [`gittree-cve-backend/app/docker_sandbox.py`](gittree-cve-backend/app/docker_sandbox.py) |
| What a patch may change | [`gittree-cve-backend/app/patch_policy.py`](gittree-cve-backend/app/patch_policy.py) |
| Nemotron tier routing (Lightning planner, Nano fan-out + repair + catalog adapter, Super audit, Ultra escalation), JSON mode, reasoning toggles | [`gittree-cve-backend/app/nemotron_router.py`](gittree-cve-backend/app/nemotron_router.py) |
| Tavily Search + Extract | [`gittree-cve-backend/app/tavily_intel.py`](gittree-cve-backend/app/tavily_intel.py) |
| Fixed attack payloads, legitimate-use controls, probe checks, adapter contract | [`gittree-cve-backend/app/attack_catalog.py`](gittree-cve-backend/app/attack_catalog.py) |
| Pipeline, catalog gate, re-check, audit veto, cost ledger, run recording | [`gittree-cve-backend/app/orchestrator.py`](gittree-cve-backend/app/orchestrator.py) |
| Token Factory post-training (`/v1/files`, `/v1/fine_tuning/jobs`) | [`gittree-cve-backend/app/post_training.py`](gittree-cve-backend/app/post_training.py) |
| GitHub repo import (budgeted, in-memory) and draft PRs | [`gittree-cve-backend/app/github_repo.py`](gittree-cve-backend/app/github_repo.py) |
| Rate limiting, SSE API, PR endpoint (verified runs only) | [`gittree-cve-backend/app/main.py`](gittree-cve-backend/app/main.py) |
| Zero-key replay of recorded runs | [`gittree-cve-backend/app/replay_fixtures.py`](gittree-cve-backend/app/replay_fixtures.py), [`gittree-cve-backend/data/recorded_runs/`](gittree-cve-backend/data/recorded_runs/) |
| Dashboard | [`gittree-cve-frontend/app/page.tsx`](gittree-cve-frontend/app/page.tsx), fork lanes in [`case-tree.tsx`](gittree-cve-frontend/app/case-tree.tsx) |

## How Tavily changes execution (not just context)

The Lightning planner turns Tavily results into a structured plan, and deterministic rules route from it:

- **Vulnerability class → which patch strategies run** (and which attack catalog applies). Injection gets parameter binding; crypto/auth gets algorithm pinning; path traversal gets input validation. A CWE id fixes the class directly (CWE-22, CWE-89, CWE-347, ...).
- **Severity → how many ConTree branches are forked.** Critical gets 5; medium/low gets 3.
- **Advisory fixed version → overrides the requested target version**, shown in the UI.
- **Extracted constraints → injected into every patch prompt and used as the auditor's veto rubric.** For a CWE, the search asks for secure-coding guidance on the weakness. Pages about a specific CVE or security advisory in the library are left out, since they describe the library's own bugs, not your code; Tavily's summary goes with them, because it was written over them too. Constraints like "upgrade the package to version X" are dropped (a weakness in your code has no fixed version).
- **No sources found → the run is marked ungrounded**, with generic strategies and no constraints.

## Run it

### Zero-key judge mode (no API keys, no spend)

```bash
cd gittree-cve-backend && ./demo.sh
```

This replays a recorded real run of CVE-2007-4559. The UI's **Replay a recorded run** checkbox does the same. Live runs fall back to replay automatically when keys are missing, a rate limit is hit, or an API fails. Replays are labeled as such and use none of the live-run allowance.

Replay never invents a run: a CVE or code with no recording (even a one-character edit to a preset) shows **"Not run"**.

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

The UI shows the backend that ran the case under the verdict, and each fork's sandbox image and network interfaces in its detail view.

### Tests

```bash
cd gittree-cve-backend && .venv/bin/python -m pytest -q
```

437 tests, all offline (one, for the Docker backend, is skipped when no Docker daemon is running). They cover:
- the phase-A classifier and Phase B integrity checks, including repositories whose pytest config adds `-q`, `-x`, `--color=yes`, `--tb=no` or options pytest cannot start with, or narrows collection with `testpaths` (globs too) or `python_files`;
- the patch policy, with each blocked vector run through the real gate, including shadow copies of the code under test in nested packages, mirrored layouts and `pythonpath` directories;
- the ConTree REST client against a mock of the documented API, and the Docker backend (skipped without a daemon);
- router helpers and prompts;
- the attack catalog: every class must exploit vulnerable code; correct fixes are approved; naive fixes, keyword blacklists, reject-everything patches and re-implementing adapters are caught, including a src/ layout;
- the orchestrator's gate semantics, re-check, repair and escalation paths;
- end-to-end runs on the presets with scripted models and the real local runner;
- GitHub URL parsing and the draft-PR flow against a mock GitHub API (allowlist, verified-runs-only, exact API sequence);
- the API: SSRF guard, replay, recordings keyed by CVE and code, NO_RECORDING, rate-limit and concurrency fallback.

### Deploy

- **Backend:** `gittree-cve-backend/Dockerfile`, one worker. Set `ALLOWED_ORIGINS` to the frontend origin and `TRUST_PROXY_HEADERS=true` behind a proxy.
  - For the Docker sandbox, either run the backend directly on a VM with Docker, or mount `/var/run/docker.sock` into the container.
  - Mounting the socket gives the *backend* host-level Docker access; patch code still runs in separate restricted containers.
- **Frontend:** any Next.js host, with `NEXT_PUBLIC_API_BASE_URL` set at build time.
- **Credit protection:** `MAX_LIVE_RUNS_PER_IP_PER_DAY` and `MAX_LIVE_RUNS_GLOBAL_PER_DAY` protect the $50 credit through judging.

## Honest status

- **ConTree:** all recorded runs in `data/recorded_runs/` are live ConTree runs recorded on Oct 24, 2026 (image import, checkpoint chaining, network-disabled forks).
  - Each recording is keyed by CVE and a hash of the code, so a run on other code never replaces a preset's replay.
  - Runs that end with no patch are recorded too, and replays show them as they happened, but they never replace a verified recording of the same code.
  - The offline tests also cover the REST client against a mock of the documented API.
- **Live runs vary.** What Tavily returns and how the models sample change the outcome. Across our live runs on Oct 24 (while the code was still changing), the CVE-2007-4559 preset was verified in 2 of 6 runs and the demo repo in 3 of 4; the CWE-347 and CWE-89 presets were verified in all 5 runs each. The tarfile runs were verified when a patch used `tarfile`'s `filter='data'`. Patches with manual path checks blocked `..` but missed symlink and hardlink members; the catalog vetoed them, and those runs ended with "no patch proposed".
- **Nemotron post-training:** Nemotron models are not on Token Factory's fine-tunable list. The flywheel uploads verified examples as a real Token Factory dataset and targets `Qwen/Qwen3-Coder-30B-A3B-Instruct` (LoRA-capable).
  - Only winners verified with their own model-written regression test become examples. A winner verified with the attack catalog is not added, since its test was not model output.
  - Job launch is gated behind `LORA_ENABLE_JOB_LAUNCH` and `LORA_MIN_EXAMPLES` because it spends credits.
- **Verification limits:**
  - Outside the three catalog classes, verification is only as strong as the generated tests, cross-validation and the auditor.
  - The JWT catalog's legitimate-use control is an RS256 token verified with a PEM public key, so it fits RS256 verifiers. A correct fix to an HS256-only verifier, or one that newly requires `iss`/`aud`, is vetoed by the control (fails closed). A verifier that doesn't return the claims as a mapping makes the catalog unusable (discarded, with the reason shown).
  - The SQL payloads catch common blacklists, not every possible one. A filter written against this exact list (for example, one that also blocks the words `IS` and `GLOB`) can still pass while `LIKE` or `!=` get through. Parameter binding is the fix the catalog is built to confirm.
  - A fix that moves the value into another quoting context with broken escaping (for example `repr()` or `json.dumps()` quoting) can get past the SQL payloads, since only payloads that reproduce in the original context are enforced.
  - A lookup that returns a raw one-row aggregate (`COUNT(*)`, `EXISTS`) reads as "found" even when the value is 0, so a correct fix to such code is vetoed (fails closed).
  - The SQL control proves that a row the adapter inserted is still found. If the adapter's setup leaves nothing the lookup can find, the control is unusable, and only the repository's own suite stops a patch that rejects every lookup.
  - The catalog's payloads use fixed identities and values. A model that sees the catalog source could special-case them; the audit and cross-validation are the remaining checks against that.
  - An adapter that reaches the repository's code but then re-implements part of the logic itself makes the catalog judge the adapter, not the repository: every patch is vetoed or the catalog is discarded (fails closed).
  - The patch policy stops a patch from changing *how* tests run, but the patched code itself runs in the same process as the tests. Code deliberately written to fake test results from inside the functions it changes is not caught by the policy; the catalog, cross-validation and the audit still see its behaviour.
  - A correct patch whose own regression test checks the wrong thing (an assertion that fails on both sides, or a "valid token" fixture the fix rightly rejects) is not re-checked with the catalog. If no other fork is approved, the escalation still gets the catalog as its test.
  - A custom `test_command` that adds its own `-q` flags hides pytest's final summary, so its runs never count as a pass (fails closed).

## License

MIT, see [LICENSE](LICENSE).
