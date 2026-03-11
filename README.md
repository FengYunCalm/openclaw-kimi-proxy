# OpenClaw Kimi Proxy

解决 OpenClaw 使用 Kimi Coding API 时的 403 白名单和 Message ordering conflict 问题。

## 🎯 问题背景

OpenClaw 使用 Kimi Coding API 时遇到两个问题：
1. **403 白名单限制** - Kimi Coding 对新用户启用了白名单
2. **Message ordering conflict** - OpenClaw 的 transcript policy 与 Kimi API 的消息格式不兼容

## 🚀 解决方案

通过本地 HTTP 代理拦截和修改 API 请求/响应：

1. **绕过 403 白名单** - 添加 Kimi CLI 特定的 HTTP Headers
2. **修复消息格式** - 自动转换不兼容的消息格式
   - `developer` → `system` 角色
   - 数组 `content` → 字符串 `content`

## 📦 安装

### 1. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/openclaw-kimi-proxy.git
cd openclaw-kimi-proxy
```

### 2. 安装依赖

需要 Python 3.6+：

```bash
python3 --version
```

### 3. 配置

复制配置示例：

```bash
# 复制 OpenClaw 配置
cp config/openclaw.json.example ~/.openclaw/openclaw.json

# 编辑配置，填入你的 API Key
nano ~/.openclaw/openclaw.json
```

在配置中修改：
```json
{
  "models": {
    "providers": {
      "kimi-coding": {
        "baseUrl": "http://localhost:20000",
        "apiKey": "sk-kimi-你的API密钥"
      }
    }
  }
}
```

### 4. 启动代理

#### 方法一：手动启动

```bash
python3 src/kimi_proxy.py
```

#### 方法二：使用快捷命令（推荐）

将以下内容添加到 `~/.bashrc` 或 `~/.zshrc`：

```bash
claw() {
    local KIMI_API_KEY="sk-kimi-你的API密钥"
    
    # 检查代理是否运行
    if curl -s http://localhost:20000/models \
        -H "Authorization: Bearer $KIMI_API_KEY" \
        --connect-timeout 2 > /dev/null 2>&1; then
        echo "✅ 代理已在运行"
    else
        echo "🔄 启动 Kimi 代理..."
        nohup python3 ~/openclaw-kimi-proxy/src/kimi_proxy.py > /tmp/kimi-proxy.log 2>&1 &
        sleep 3
        if curl -s http://localhost:20000/models \
            -H "Authorization: Bearer $KIMI_API_KEY" \
            --connect-timeout 2 > /dev/null 2>&1; then
            echo "✅ 代理已启动"
        else
            echo "❌ 代理启动失败"
            return 1
        fi
    fi
    
    # 启动网关
    echo "🔄 启动 OpenClaw 网关..."
    openclaw gateway
}
```

然后使用：
```bash
claw
```

## 📝 使用说明

### 基本使用

启动代理后，正常使用 OpenClaw：

```bash
openclaw agent -m "你好" --agent main
```

### 测试代理

```bash
# 测试模型列表
curl http://localhost:20000/models \
  -H "Authorization: Bearer sk-kimi-你的API密钥"

# 测试对话
curl http://localhost:20000/chat/completions \
  -H "Authorization: Bearer sk-kimi-你的API密钥" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "k2p5",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

## 🔧 故障排除

### 代理启动失败

```bash
# 检查端口占用
netstat -ano | grep 20000

# 杀掉占用进程
pkill -f kimi_proxy
```

### Message ordering conflict 错误

确保代理正在运行：
```bash
curl http://localhost:20000/models -H "Authorization: Bearer 你的API密钥"
```

如果返回模型列表，说明代理正常。

### 403 错误

检查 API Key 是否正确配置在 `~/.openclaw/openclaw.json` 中。

## 🏗️ 项目结构

```
.
├── src/
│   └── kimi_proxy.py          # 主代理脚本
├── config/
│   └── openclaw.json.example  # OpenClaw 配置示例
├── docs/
│   └── TROUBLESHOOTING.md     # 故障排除指南
├── README.md                  # 本文件
└── LICENSE                    # 开源协议
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 开源协议

MIT License

## 🙏 致谢

- OpenClaw 团队
- Kimi/Moonshot AI

## ⚠️ 免责声明

本项目仅供学习和研究使用。使用 Kimi API 请遵守 Moonshot AI 的使用条款。
