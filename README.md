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

## Get the code

```bash
git clone https://github.com/FengYunCalm/openclaw-kimi-proxy.git
cd openclaw-kimi-proxy
```

If you want to inspect the current source-level behavior, start from `src/kimi_proxy.py`, `src/proxy_final.py`, and `config/openclaw.json.example`.

## Notes

- The repository currently keeps several proxy variants under `src/`.
- The shell helper in `docs/bashrc-claw.sh` is optional convenience tooling.
- This README stays at source-repository scope and does not claim any packaged or hosted distribution.

## License

MIT
