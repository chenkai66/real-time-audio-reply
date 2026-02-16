#!/usr/bin/env python
"""
模拟对话测试脚本
演示完整的教师-学生对话流程
"""
import asyncio
import websockets
import json
import time

async def test_conversation():
    uri = "ws://localhost:8000/ws/audio"
    
    print("🚀 连接到 WebSocket 服务器...")
    
    async with websockets.connect(uri) as websocket:
        # 接收连接确认
        message = await websocket.recv()
        data = json.loads(message)
        print(f"✅ {data['message']}\n")
        
        # 模拟对话场景
        conversations = [
            {
                "text": "同学们好，今天我们来学习 Python 的基础语法。首先，我们来了解什么是变量。",
                "is_final": True,
                "expected_role": "teacher"
            },
            {
                "text": "老师，我不太明白什么是变量，能详细解释一下吗？",
                "is_final": True,
                "expected_role": "student"
            },
            {
                "text": "好的，让我们继续学习 Python 的数据类型。",
                "is_final": True,
                "expected_role": "teacher"
            },
            {
                "text": "Python 有哪些基本的数据类型呢？",
                "is_final": True,
                "expected_role": "student"
            }
        ]
        
        for i, conv in enumerate(conversations, 1):
            print(f"\n{'='*60}")
            print(f"📝 对话 {i}: {conv['text'][:50]}...")
            print(f"{'='*60}")
            
            # 发送转写文本
            await websocket.send(json.dumps({
                "type": "transcript",
                "text": conv["text"],
                "is_final": conv["is_final"]
            }))
            
            # 接收响应
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    
                    if data["type"] == "status":
                        print(f"   ⏳ 状态: {data.get('status', '')} - {data.get('message', data.get('text', ''))}")
                    
                    elif data["type"] == "role_identified":
                        role = data["role"]
                        role_name = {"teacher": "教师", "student": "学生", "unknown": "未知"}[role]
                        print(f"   👤 识别角色: {role_name}")
                        print(f"   💬 内容: {data['text']}")
                        
                        # 如果是学生提问，等待回复
                        if role == "student":
                            continue
                        else:
                            break
                    
                    elif data["type"] == "reply":
                        print(f"   🤖 AI 回复: {data['text']}")
                        break
                    
                    elif data["type"] == "error":
                        print(f"   ❌ 错误: {data['message']}")
                        break
                    
                    elif data["type"] == "stats":
                        stats = data["data"]
                        print(f"   📊 统计: {stats['total_turns']} 轮对话, {stats['total_tokens']} tokens")
                        break
                
                except asyncio.TimeoutError:
                    print("   ⏰ 等待超时")
                    break
            
            # 等待一下再发送下一条
            await asyncio.sleep(1)
        
        print(f"\n{'='*60}")
        print("✨ 对话测试完成！")
        print(f"{'='*60}\n")
        
        # 获取最终统计
        await websocket.send(json.dumps({"type": "ping"}))
        message = await websocket.recv()
        print(f"💓 心跳测试: {json.loads(message)['type']}")

if __name__ == "__main__":
    print("🎓 实时语音识别与智能回复系统 - 对话测试\n")
    asyncio.run(test_conversation())

