# Submission checklist (deadline Oct 30, 2026, 10:00 AM PT)

- [ ] ConTree activated for the project (`/api/health` shows `"spawn": true`). Then re-record `data/recorded_runs/*.json` with `SANDBOX_BACKEND=contree` so replays show real ConTree image UUIDs. Docker-backed recordings are already in place as the fallback.
- [ ] Backend deployed (Dockerfile) with `ALLOW_LOCAL_SANDBOX=false`, `ALLOWED_ORIGINS`, `TRUST_PROXY_HEADERS=true`.
- [ ] Frontend deployed with `NEXT_PUBLIC_API_BASE_URL`.
- [ ] Public demo URL tested from a clean browser, both live and replay.
- [ ] Repo public, `LICENSE` at root, README renders.
- [ ] Video under 3 minutes, narrated, uploaded to YouTube (public).
- [ ] `FEEDBACK.md` pasted into the feedback field.

## Video script (~2:50)

**0:00–0:30 Problem and live result**

"Dependabot bumps versions; coding agents guess. Neither proves the fix works." Pick CVE-2007-4559, press Run, and let the branch tree fill in on screen.

**0:30–1:45 Architecture, narrated over the live telemetry**

- **Tavily panel:** "Live advisories decided this run: the vulnerability class picked the strategies, severity picked three branches, and these constraints went into every prompt and the audit."
- **Branch cards:** they fill in live as each finishes. "Each candidate runs in two network-disabled sandboxes forked from one checkpoint. Phase A must fail on vulnerable code; Phase B must pass the full suite." Point at a *Trivial Test Rejected* card and a "+ repair" card.
- **Attack catalog (the key moment):** "Two patches passed their own tests. Then the fixed attack catalog ran: plain `../` blocked, but the symlink and hardlink payloads got through. Both were vetoed." Point at the MISSED cells.
- **Escalation:** "The proven exploits become the escalation's test. Super's answer is `filter='data'`, Python's built-in safe extraction, and every payload is blocked."
- **Matrix:** "Every passing patch also has to beat the other branches' exploits."
- **Cost KPI:** "Seven Nemotron calls: under a fifth of a cent."

**1:45–2:30 Failure recovery**

Run the PyJWT preset. Show the repair round, then escalation to Ultra, then either a verified patch or the "No patch proposed" banner. "It never ships an unverified patch."

**2:30–2:50 Close**

Show the LoRA panel uploading the verified dataset to Token Factory (real file ID). Then: replay mode works for judges without keys; MIT licensed; repo link.
