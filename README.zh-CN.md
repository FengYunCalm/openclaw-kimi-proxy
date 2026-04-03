# OpenClaw Kimi Proxy

[English](README.md) | 简体中文

这是一个给 OpenClaw 使用的小型 HTTP 代理。它会把请求转发到 Kimi Coding API，补上当前仓库脚本里依赖的 Kimi CLI 请求头，并在请求到达上游之前改写不兼容的聊天消息载荷。

## 这个仓库解决什么问题

当前这套代理主要是为了解决 OpenClaw 接 Kimi Coding API 时的两个现实兼容性问题：

- 因 Kimi 特定访问检查导致的 403 请求
- 需要在转发前改写的消息载荷格式

现有代理脚本会处理两类仓库中已出现的请求改写：

- `developer` 角色改写为 `system`
- 数组形式的 `content` 改写为字符串形式的 `content`

## 仓库结构

- `src/` — 代理实现与实验性变体
- `config/openclaw.json.example` — 指向本地代理的 OpenClaw 配置示例
- `docs/bashrc-claw.sh` — 可选的 shell 辅助脚本，用于一起启动代理与 OpenClaw

## 获取源码

```bash
git clone https://github.com/FengYunCalm/openclaw-kimi-proxy.git
cd openclaw-kimi-proxy
```

如果你要看当前源码行为，优先从 `src/kimi_proxy.py`、`src/proxy_final.py` 和 `config/openclaw.json.example` 开始。

## 说明

- 当前仓库在 `src/` 下保留了多个代理变体。
- `docs/bashrc-claw.sh` 只是便捷脚本。
- 这个 README 只停留在源码仓库层面，不声明打包分发或托管部署渠道。

## 许可证

MIT
