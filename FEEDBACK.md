# Platform feedback (draft for the Devpost feedback field)

These are concrete issues we hit while building GitTree-CVE against Nebius Token Factory and NVIDIA Nemotron, all reproduced in October 2026.

## Token Factory Sandboxes (ConTree)

1. **Activation state is invisible until you call `/whoami`.**
   - **What happened:** a fresh project's API key authenticates fine, but `GET /sandboxes/v1/whoami` returns every permission as `false` (`spawn`, `list`, `import`, ...). `GET /v1/images` returns `403 Insufficient permissions: list`.
   - **Why it hurts:** neither the console nor the error message says that Sandboxes needs activation by email (contree@nebius.com).
   - **Suggestion:** a console banner, or a 403 body that says "Sandboxes not activated for project X".
2. **The base URL is inconsistent across docs.**
   - The REST reference says `https://api.tokenfactory.nebius.com/sandboxes/v1`.
   - The networking cookbook builds `.../sandboxes` and then appends `v1/instances`.
   - The OpenAPI `servers` entry is `{baseUrl}/v1` with `baseUrl=.../sandboxes`.
   - All three are compatible, but it took reading three pages to be sure.
3. **The Python SDK (0.3.6) has no networking control.**
   - `Image.run()` has no networking parameter, so `networking.enabled=false` is REST-only.
   - We had to drop to raw REST for the core security property of our app.
4. **`files` in a spawn request needs pre-uploaded file UUIDs.**
   - Injecting a handful of small source files therefore needs an upload round trip first.
   - We base64-encode files into the shell command instead. An inline `content` option for small files would help agent workloads.
5. **Bare Docker refs fail without a clear error.**
   - `"image": "python:3.11-slim"` is not valid; it must be a UUID, `tag:...`, or an imported OCI ref.
   - A 400 that suggests `tag:` or `/images/import` would save time.

## Token Factory inference

6. **Nemotron 3.5 Lightning reasons by default.**
   - With a 700-token cap it spent most of the budget in `reasoning_content` and returned truncated JSON.
   - `extra_body={"chat_template_kwargs": {"enable_thinking": false}}` fixes it.
   - This switch isn't documented on the model card or in the model list. Nemotron 3 Nano does not reason by default, so the tiers behave differently under identical requests.
7. **`response_format={"type": "json_object"}` + thinking off gave reliable JSON on Nano and Lightning.** Worth stating explicitly in the docs.
8. **Super with thinking enabled hit `finish_reason=length` at 12k tokens** on a code-repair prompt after ~68 s. Guidance on sensible reasoning budgets for agentic code tasks would help.

## Post-training

9. **No Nemotron model is fine-tunable on Token Factory.**
   - The hackathon materials and third-party write-ups suggest LoRA on Nemotron Nano, but the supported-models page lists only DeepSeek, Gemma, GPT-OSS, Qwen and Llama.
   - We targeted Qwen3-Coder-30B-A3B. Nemotron Nano LoRA support would make an all-NVIDIA flywheel possible.
10. **Dataset upload worked first try** with the conversational `messages` format (last message from `assistant`); the file ID came back in under a second.
