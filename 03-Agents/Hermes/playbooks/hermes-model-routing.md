# Hermes Model Routing

Purpose: Keep Hermes on MiniMax by default while preserving OpenRouter as an explicit secondary route for model experiments, one-off debugging, and free-model checks.

## Default Policy

- Default provider: `minimax`
- Default model: `MiniMax-M2.7`
- Default base URL: `https://api.minimax.io/anthropic`
- OpenRouter must not be configured with the MiniMax base URL.
- Do not switch the default provider to OpenRouter without Piet's explicit approval.
- Do not replace the Hermes token/credentials with the Piet/OpenClaw Discord token.

## Why `/model` Failed On 2026-05-02

Hermes was configured with:

```yaml
provider: openrouter
default: openrouter/meta-llama/llama-3.3-70b-instruct:free
base_url: https://api.minimax.io/anthropic
```

This mixed two incompatible routes:

- `provider: openrouter` should call OpenRouter.
- `base_url: https://api.minimax.io/anthropic` points to MiniMax.
- OpenRouter model IDs normally do not use an extra `openrouter/` prefix for provider-owned models.

Observed invalid ID:

```text
openrouter/meta-llama/llama-3.3-70b-instruct:free
```

Observed valid OpenRouter IDs:

```text
nvidia/nemotron-3-super-120b-a12b:free
meta-llama/llama-3.3-70b-instruct:free
openrouter/auto
minimax/minimax-m2.7
```

Verified OpenRouter free candidates:

| Model | Status | Note |
|---|---|---|
| `nvidia/nemotron-3-super-120b-a12b:free` | OK | Verified by Piet on 2026-05-02 |
| `meta-llama/llama-3.3-70b-instruct:free` | Valid ID, rate-limited | Returned 429 during local smoke test on 2026-05-02 |

## OpenRouter Usage

Use OpenRouter only when needed for a specific test or model comparison.

Preferred first checks:

```bash
hermes auth list
hermes fallback list
hermes model --help
```

Small one-off smoke test:

```bash
hermes -z "Antworte nur: OK" --provider openrouter --model nvidia/nemotron-3-super-120b-a12b:free
```

If the free model is unavailable, rate-limited, or removed, use:

```bash
hermes -z "Antworte nur: OK" --provider openrouter --model openrouter/auto
```

Automatic fallback is currently configured for OpenAI Codex OAuth:

```yaml
fallback_providers:
- provider: openai-codex
  model: gpt-5.5
```

This means MiniMax stays primary and GPT-5.5 via `openai-codex` is tried only when the primary fails with a fallback-eligible error.

If Piet explicitly wants OpenRouter as an additional automatic fallback, use:

```bash
hermes fallback add
```

Then select provider `openrouter` and a verified model ID. Do not add OpenRouter automatic fallback silently because it changes runtime and cost behavior.

## MiniMax Portal Note

If Piet specifically wants MiniMax via portal OAuth instead of the direct MiniMax API-key route, check:

```bash
hermes auth list
hermes status
```

If `minimax-oauth` is not logged in, Piet must complete the interactive login:

```bash
hermes auth add minimax-oauth
```

Until then, use the configured direct MiniMax provider if `MINIMAX_API_KEY` is present.

## Change Gate

Before changing model defaults:

1. Create a timestamped backup of `/home/piet/.hermes/config.yaml`.
2. Change only the required `model:` fields.
3. Run `hermes status`.
4. Run a tiny smoke test with the target provider/model.
5. Restart `hermes-gateway.service` only if the Discord gateway must pick up the new default.
6. Post-check Discord connectivity and avoid repeated restarts if Discord returns 429 during command sync.
