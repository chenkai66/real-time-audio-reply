#!/bin/bash

# 实时语音识别系统 - 启动脚本

echo "🚀 启动实时语音识别与智能回复系统..."
echo ""

# 清理函数
cleanup() {
    echo ""
    echo "🛑 正在停止所有服务..."
    
    # 停止后端
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    
    # 停止前端
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    # 清理端口占用
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    lsof -ti:5173 | xargs kill -9 2>/dev/null
    
    echo "✅ 所有服务已停止"
    exit 0
}

# 注册清理函数
trap cleanup INT TERM EXIT

# 检查并清理端口占用
echo "🔍 检查端口占用..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  端口 8000 被占用，正在清理..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 1
fi

if lsof -ti:5173 > /dev/null 2>&1; then
    echo "⚠️  端口 5173 被占用，正在清理..."
    lsof -ti:5173 | xargs kill -9 2>/dev/null
    sleep 1
fi

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
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo "⏳ 等待后端启动..."
sleep 3

# 检查后端是否启动成功
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端启动成功"
else
    echo "❌ 后端启动失败"
    cleanup
fi

# 启动前端
echo "🎨 启动前端服务..."
cd frontend
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

# 等待前端启动
echo "⏳ 等待前端启动..."
sleep 3

echo ""
echo "✨ 系统启动成功！"
echo ""
echo "📍 后端地址: http://localhost:8000"
echo "📍 API 文档: http://localhost:8000/docs"
echo "📍 前端地址: http://localhost:5173"
echo ""
echo "💡 提示: 按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
wait

