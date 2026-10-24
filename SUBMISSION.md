# Submission checklist (deadline Oct 30, 2026, 10:00 AM PT)

- [x] ConTree activated for the project (`/api/health` shows `"spawn": true`). All three presets and the demo repo were re-recorded live on ConTree on Oct 24.
- [ ] Backend deployed (Dockerfile) with `ALLOW_LOCAL_SANDBOX=false`, `ALLOWED_ORIGINS`, `TRUST_PROXY_HEADERS=true`.
- [ ] Frontend deployed with `NEXT_PUBLIC_API_BASE_URL`.
- [ ] Public demo URL tested from a clean browser, both live and replay.
- [ ] Repo public, `LICENSE` at root, README renders.
- [ ] Push `examples/vulnerable-demo` to its own GitHub repo. Set `GITHUB_TOKEN` (fine-grained, contents + pull requests on that repo only) and `GITHUB_PR_ALLOWED_OWNERS=<your user>` on the backend. A draft PR has not been opened end to end yet: do one before recording.
- [ ] Video under 3 minutes, narrated, uploaded to YouTube (public).
- [ ] `FEEDBACK.md` pasted into the feedback field.

## Video script (~2:50)

Record the first two segments from replays: they are real ConTree runs and play back exactly as they happened, so the narration below matches the screen. The pull request segment has to be live (a replay cannot open a PR), and live runs vary: narrate what the run actually does.

**0:00–0:20 Problem**

"Dependabot bumps versions; coding agents guess. Neither proves the fix works. GitTree-CVE has Nemotron write several patches in parallel and only proposes one that sandboxes prove fixes the exploit."

**0:20–1:10 CVE-2007-4559, replayed (tarfile path traversal)**

Tick **Replay a recorded run**, pick the CVE-2007-4559 preset, press **Run case**.

- **Advisory evidence:** "Live advisories decided this run. The vulnerability class picked the strategies, medium severity picked three forks, and these requirements, including tarfile's `filter='data'`, went into every prompt and into the audit."
- **Forks:** "Each fork runs in two network-disabled ConTree VMs copied from one checkpoint. Its exploit test must fail on the vulnerable code, then the patched code must pass the full suite." Point at #5: "this patch failed its own regression test, even after a repair round."
- "#2 and #4 wrote the right patch but unusable tests: one fails the same way before and after the fix, the other already passes on the vulnerable code. Instead of throwing them away, GitTree re-checks them with the fixed attack catalog." Point at the *re-checked with attack suite* tags.
- **Attacks:** "These payloads are code, not model output. Four of them work on the vulnerable code: parent-directory traversal, an absolute path, a symlink and a hardlink. Both patches block all four and still extract a normal archive."
- **Verdict:** "Super's audit picks #2, `filter='data'`, 95 out of 100." Read the spend under the verdict: "$0.0018, seven Nemotron calls."

**1:10–1:40 CWE-347, replayed (JWT signature not verified)**

Pick the CWE-347 preset (replay still ticked), press **Run case**.

- "A weakness, not a CVE: this verifier calls `jwt.decode` with signature checking turned off. Tavily searched for secure-coding guidance and left out four pages about PyJWT's own vulnerabilities, and its summary with them: they say nothing about this code. The requirements come from the guidance pages."
- **Attacks:** "Eight forged tokens work on the vulnerable code: the wrong signer, `alg: none`, key confusion, an embedded key, an expired token, a forged ordinary user. A token the server really signed must still be accepted."
- **Forks:** "None of the five forks wrote a test that proves anything: four crash on the vulnerable code, one fails the same way before and after the fix. Instead of throwing the patches away, the re-check runs each against the catalog: all five block all eight forged tokens and still accept the real one. The audit picks #4, the smallest change: `verify_signature` from False to True."

**1:40–2:30 Real repo to pull request (live)**

Paste the demo repo URL, press **Import**, untick **Replay a recorded run**, press **Run case**. Cut the wait in editing.

- Narrate the lanes as they finish. If every Nano fork fails, the run escalates: "the attack catalog becomes the escalation's regression test". In an earlier recorded run of this repo, every Nano fork failed and Super's escalation, `filter='data'`, blocked all four payloads; in the current recording, three forks were rescued by the re-check instead.
- On the verified fork, open the **Pull request** tab and click **Open draft PR on owner/repo**. Show the PR on GitHub: the patch, the regression test file, and the evidence in the description.
- If the live run ends with **No patch proposed**, say so: "it never ships an unverified patch". Run it again for the PR.

**2:30–2:50 Close**

"Every model call is logged with its Token Factory completion ID and cost; a run costs a fraction of a cent. Judges can replay every recorded run without keys. MIT licensed." Show the repo link.
