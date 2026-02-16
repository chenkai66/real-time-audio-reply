"""
FastAPI 主应用
提供 WebSocket 和 REST API 接口
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import asyncio
import json
from datetime import datetime

from config.settings import settings
from backend.core.role import Role, role_identifier
from backend.core.conversation import conversation_history
from backend.core.generator import reply_generator
from backend.utils.audio import audio_processor
from backend.utils.logger import setup_logging, get_logger
from backend.utils.middleware import RequestTracingMiddleware, ErrorHandlingMiddleware, RateLimitMiddleware
from backend.utils.metrics import global_metrics, Timer
from backend.utils.cache import global_cache

# 配置日志
setup_logging(
    level="INFO" if settings.debug else "WARNING",
    structured=True
)

logger = get_logger(__name__)

app = FastAPI(
    title="实时语音识别与智能回复系统",
    description="用于在线授课场景的 AI 助教系统",
    version="0.1.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加中间件
app.add_middleware(RequestTracingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """接受连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_message(self, message: Dict, websocket: WebSocket):
        """发送消息到指定客户端"""
        await websocket.send_json(message)
    
    async def broadcast(self, message: Dict):
        """广播消息到所有客户端"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"广播消息失败: {e}")


manager = ConnectionManager()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "实时语音识别与智能回复系统 API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/stats")
async def get_stats():
    """获取系统统计信息"""
    with Timer(global_metrics, "api.stats.duration"):
        return {
            "conversation": conversation_history.get_stats(),
            "connections": len(manager.active_connections),
            "cache": global_cache.get_stats(),
            "metrics": global_metrics.get_all_stats(window_seconds=300)
        }


@app.post("/api/conversation/clear")
async def clear_conversation():
    """清空对话历史"""
    with Timer(global_metrics, "api.clear.duration"):
        conversation_history.clear()
        role_identifier.clear_role_features()
        global_cache.clear()
        logger.info("对话历史已清空")
        return {"message": "对话历史已清空"}


@app.get("/api/conversation/history")
async def get_conversation_history():
    """获取对话历史"""
    return {
        "l1_cache": [turn.to_dict() for turn in conversation_history.l1_cache],
        "l2_cache": [summary.to_dict() for summary in conversation_history.l2_cache],
        "stats": conversation_history.get_stats()
    }


@app.post("/api/test/generate")
async def test_generate(question: str, context: str = None):
    """测试回复生成（用于调试）"""
    with Timer(global_metrics, "api.generate.duration"):
        try:
            logger.info(f"测试生成回复: {question[:50]}...")
            reply = await reply_generator.generate(
                question=question,
                context=context,
                conversation_history=conversation_history
            )
            global_metrics.record("api.generate.success", 1)
            return {"reply": reply}
        except Exception as e:
            global_metrics.record("api.generate.error", 1)
            logger.error(f"生成回复失败: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/audio")
async def websocket_audio_endpoint(websocket: WebSocket):
    """
    音频 WebSocket 端点
    接收音频数据和转写文本，返回识别结果和回复
    """
    await manager.connect(websocket)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket 连接成功"
        })
        
        while True:
            # 接收消息
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "transcript":
                # 收到转写文本
                await handle_transcript(websocket, data)
            
            elif message_type == "audio":
                # 收到音频数据（暂时不处理，后续可用于声纹识别）
                pass
            
            elif message_type == "ping":
                # 心跳
                await websocket.send_json({"type": "pong"})
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"未知的消息类型: {message_type}"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket 连接断开")
    
    except Exception as e:
        print(f"WebSocket 错误: {e}")
        manager.disconnect(websocket)
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass


async def handle_transcript(websocket: WebSocket, data: Dict):
    """
    处理转写文本
    
    Args:
        websocket: WebSocket 连接
        data: 消息数据
    """
    text = data.get("text", "")
    is_final = data.get("is_final", False)
    
    if not text:
        return
    
    # 发送识别中状态
    await websocket.send_json({
        "type": "status",
        "status": "processing",
        "text": text
    })
    
    # 识别角色
    role = await role_identifier.identify(text)
    
    # 添加到对话历史
    conversation_history.add_turn(role, text)
    
    # 发送角色识别结果
    await websocket.send_json({
        "type": "role_identified",
        "role": role.value,
        "text": text,
        "timestamp": datetime.now().isoformat()
    })
    
    # 如果是学生提问且是最终结果，生成回复
    if role == Role.STUDENT and is_final:
        # 检查是否为有效问题
        if not reply_generator.is_valid_question(text):
            await websocket.send_json({
                "type": "status",
                "status": "skipped",
                "message": "不是有效的问题，跳过回复"
            })
            return
        
        # 发送生成中状态
        await websocket.send_json({
            "type": "status",
            "status": "generating",
            "message": "正在生成回复..."
        })
        
        try:
            # 生成回复
            reply = await reply_generator.generate(
                question=text,
                conversation_history=conversation_history
            )
            
            # 将回复添加到历史
            conversation_history.add_turn(Role.TEACHER, reply)
            
            # 发送回复
            await websocket.send_json({
                "type": "reply",
                "text": reply,
                "question": text,
                "timestamp": datetime.now().isoformat()
            })
            
            # 发送统计信息
            await websocket.send_json({
                "type": "stats",
                "data": conversation_history.get_stats()
            })
        
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": f"生成回复失败: {str(e)}"
            })


@app.websocket("/ws/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    """
    流式回复 WebSocket 端点
    支持流式输出回复内容
    """
    await manager.connect(websocket)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "流式 WebSocket 连接成功"
        })
        
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "generate":
                # 流式生成回复
                question = data.get("question", "")
                
                if not question:
                    await websocket.send_json({
                        "type": "error",
                        "message": "问题不能为空"
                    })
                    continue
                
                # 发送开始标记
                await websocket.send_json({
                    "type": "stream_start",
                    "question": question
                })
                
                try:
                    # 流式生成
                    async for chunk in reply_generator.generate_stream(
                        question=question,
                        conversation_history=conversation_history
                    ):
                        await websocket.send_json({
                            "type": "stream_chunk",
                            "chunk": chunk
                        })
                    
                    # 发送结束标记
                    await websocket.send_json({
                        "type": "stream_end"
                    })
                
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"流式生成失败: {str(e)}"
                    })
            
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    
    except Exception as e:
        print(f"流式 WebSocket 错误: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        log_level="info"
    )

