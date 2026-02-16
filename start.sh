#!/bin/bash

# 实时语音识别系统 - 启动脚本

echo "🚀 启动实时语音识别与智能回复系统..."
echo ""

# 检查 Python
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到 Python"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js"
    exit 1
fi

# 检查环境变量
if [ ! -f .env ]; then
    echo "⚠️  警告: 未找到 .env 文件，请从 .env.example 复制并配置"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 启动后端
echo "📦 启动后端服务..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "🎨 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✨ 系统启动成功！"
echo ""
echo "📍 后端地址: http://localhost:8000"
echo "📍 前端地址: http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

