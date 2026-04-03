# OpenClaw Kimi Proxy

English | [简体中文](README.zh-CN.md)

A small HTTP proxy for OpenClaw that forwards requests to the Kimi Coding API, adds the headers expected by Kimi CLI, and rewrites incompatible chat message payloads before they reach the upstream endpoint.

## Why this repository exists

OpenClaw currently needs a compatibility layer for two practical issues in front of the Kimi Coding API:

- 403 requests caused by Kimi-specific access checks
- message payloads that need rewriting before they are accepted upstream

The current proxy code normalizes two request patterns that appear in this repository's scripts:

- `developer` role → `system`
- array `content` → string `content`

## Repository layout

- `src/` — proxy implementations and experimental variants
- `config/openclaw.json.example` — sample OpenClaw provider configuration pointing to the local proxy
- `docs/bashrc-claw.sh` — optional shell helper for starting the proxy and OpenClaw together

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/FengYunCalm/openclaw-kimi-proxy.git
cd openclaw-kimi-proxy
```

### 2. Prepare your OpenClaw config

Use `config/openclaw.json.example` as a starting point. The important fields are:

```json
{
  "models": {
    "providers": {
      "kimi-coding": {
        "baseUrl": "http://localhost:20000",
        "apiKey": "YOUR_KIMI_API_KEY_HERE"
      }
    }
  }
}
```

### 3. Start the proxy

```bash
python src/kimi_proxy.py
```

The current minimal proxy listens on port `20000` and forwards traffic to `https://api.kimi.com/coding/v1`.

### 4. Verify the proxy

```bash
curl http://localhost:20000/models \
  -H "Authorization: Bearer YOUR_KIMI_API_KEY_HERE"
```

## Notes

- The repository currently keeps several proxy variants under `src/`.
- The shell helper in `docs/bashrc-claw.sh` is optional convenience tooling, not a required part of the proxy runtime.
- This repository is documentation- and script-focused; there is no packaged release flow in the current tree.

## License

MIT
