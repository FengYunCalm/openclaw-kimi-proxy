# claw() 函数 - 用于快速启动 OpenClaw + Kimi 代理
# 将此文件内容添加到你的 ~/.bashrc 或 ~/.zshrc 中

claw() {
    local KIMI_API_KEY="YOUR_KIMI_API_KEY_HERE"
    
    # 检查代理是否运行
    if curl -s http://localhost:20000/models \
        -H "Authorization: Bearer $KIMI_API_KEY" \
        --connect-timeout 2 > /dev/null 2>&1; then
        echo "✅ 代理已在运行"
    else
        echo "🔄 启动 Kimi 代理..."
        nohup python3 ~/openclaw-kimi-proxy/src/proxy_final.py > /tmp/kimi-proxy.log 2>&1 &
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

# 可选：添加别名
alias claw-stop='pkill -f kimi_proxy'
alias claw-log='tail -f /tmp/kimi-proxy.log'
alias claw-status='curl -s http://localhost:20000/models -H "Authorization: Bearer YOUR_KIMI_API_KEY_HERE" | head -20'
