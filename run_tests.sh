#!/bin/bash

# 运行所有测试

echo "🧪 运行测试套件..."
echo ""

# 运行单元测试
echo "📝 运行单元测试..."
python -m pytest tests/unit/ -v --cov=backend --cov-report=term-missing

if [ $? -ne 0 ]; then
    echo "❌ 单元测试失败"
    exit 1
fi

echo ""
echo "📝 运行集成测试..."
python -m pytest tests/integration/ -v

if [ $? -ne 0 ]; then
    echo "❌ 集成测试失败"
    exit 1
fi

echo ""
echo "✅ 所有测试通过！"

