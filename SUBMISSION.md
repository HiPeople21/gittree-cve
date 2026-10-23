# Submission checklist (deadline Oct 30, 2026, 10:00 AM PT)

- [x] ConTree activated for the project (`/api/health` shows `"spawn": true`). All three presets and the demo repo are re-recorded live on ConTree.
- [ ] Backend deployed (Dockerfile) with `ALLOW_LOCAL_SANDBOX=false`, `ALLOWED_ORIGINS`, `TRUST_PROXY_HEADERS=true`.
- [ ] Frontend deployed with `NEXT_PUBLIC_API_BASE_URL`.
- [ ] Public demo URL tested from a clean browser, both live and replay.
- [ ] Repo public, `LICENSE` at root, README renders.
- [ ] Push `examples/vulnerable-demo` to its own GitHub repo. Set `GITHUB_TOKEN` (fine-grained, contents + pull requests on that repo only) and `GITHUB_PR_ALLOWED_OWNERS=<your user>` on the backend.
- [ ] Video under 3 minutes, narrated, uploaded to YouTube (public).
- [ ] `FEEDBACK.md` pasted into the feedback field.

## Video script (~2:50)

**0:00–0:30 Problem and live result**

"Dependabot bumps versions; coding agents guess. Neither proves the fix works." Pick CVE-2007-4559, press **Run case**, and let the fork lanes fill in on screen.

**0:30–1:45 Architecture, narrated over the live telemetry**

- **Tavily panel:** "Live advisories decided this run: the vulnerability class picked the strategies, severity picked three branches, and these constraints went into every prompt and the audit."
- **Fork lanes:** each lane advances through the gates as its sandbox finishes. "Each candidate runs in two network-disabled sandboxes copied from one checkpoint. Its exploit test must fail on the vulnerable code, then the patched code must pass the full suite." Point at a lane that stops at *Exploit reproduced* ("its test already passes on the vulnerable code") and at a "+ repair" lane.
- **Attack catalog (the key moment):** "Two patches passed their own tests. Then the fixed attack catalog ran: plain `../` blocked, but the symlink and hardlink payloads got through. Both were vetoed." Point at the red *missed* cells and at the lanes that stop at *Attacks blocked*. Live runs vary: if no fork is vetoed this time, run it again or narrate the lane that did fail.
- **Escalation:** "The proven exploits become the escalation's test. Super's answer is `filter='data'`, Python's built-in safe extraction, and every payload is blocked."
- **Cross-check:** "Every passing patch also has to beat the other forks' exploit tests."
- **Spend, under the verdict:** read the real number off the screen ("ten Nemotron calls, a fifth of a cent").

**1:45–2:15 Failure recovery**

Run the CWE-347 (JWT) preset — a verifier with signature checking disabled. The catalog's four forged-token payloads (attacker-signed, alg:none, HS256, tampered claims) all reproduce, and every Nano fork's cheap patch is vetoed for missing them — each lane ends at the check it failed. Escalation to Super then produces `verify_signature=True`, which blocks all four (audit 95/100) → verified. "When nothing qualifies, the verdict is a red 'No patch proposed' — it never ships an unverified patch."

**2:15–2:35 Real repo to PR**

Paste the demo repo URL, run CVE-2007-4559, then open the **Pull request** tab and click **Open draft PR on owner/repo**. Show the PR on GitHub with the patch, the new regression test, and the evidence in the description.

**2:35–2:50 Close**

In **Training data**, click **Upload dataset** to send the verified examples to Token Factory (real file ID). Then: replay mode works for judges without keys; MIT licensed; repo link.
