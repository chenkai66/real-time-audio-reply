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
from backend.core.exporter import ConversationExporter
from backend.core.analyzer import ConversationAnalyzer, smart_reminder
from backend.core.settings_manager import settings_manager
from backend.core.session_history import session_history
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


@app.get("/api/export/{format}")
async def export_conversation(format: str):
    """
    导出对话历史
    
    Args:
        format: 导出格式 (json/txt/markdown/html)
    """
    exporter = ConversationExporter(conversation_history)
    
    if format == "json":
        content = exporter.export_to_json()
        media_type = "application/json"
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    elif format == "txt":
        content = exporter.export_to_txt()
        media_type = "text/plain"
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    elif format == "markdown":
        content = exporter.export_to_markdown()
        media_type = "text/markdown"
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    elif format == "html":
        content = exporter.export_to_html()
        media_type = "text/html"
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    else:
        raise HTTPException(status_code=400, detail="不支持的格式")
    
    from fastapi.responses import Response
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/api/search")
async def search_conversations(keyword: str, case_sensitive: bool = False):
    """
    搜索对话
    
    Args:
        keyword: 搜索关键词
        case_sensitive: 是否区分大小写
    """
    exporter = ConversationExporter(conversation_history)
    results = exporter.search_conversations(keyword, case_sensitive)
    
    return {
        "keyword": keyword,
        "count": len(results),
        "results": [turn.to_dict() for turn in results]
    }


@app.get("/api/analysis/participation")
async def analyze_participation():
    """分析参与度"""
    analyzer = ConversationAnalyzer(conversation_history)
    return analyzer.analyze_participation()


@app.get("/api/analysis/questions")
async def analyze_questions():
    """分析学生提问"""
    analyzer = ConversationAnalyzer(conversation_history)
    return analyzer.analyze_questions()


@app.get("/api/analysis/keywords")
async def analyze_keywords(top_n: int = 10):
    """
    分析高频关键词
    
    Args:
        top_n: 返回前 N 个关键词
    """
    analyzer = ConversationAnalyzer(conversation_history)
    keywords = analyzer.analyze_keywords(top_n)
    
    return {
        "keywords": [{"word": word, "count": count} for word, count in keywords]
    }


@app.get("/api/analysis/quality")
async def analyze_quality():
    """分析互动质量"""
    analyzer = ConversationAnalyzer(conversation_history)
    return analyzer.analyze_interaction_quality()


@app.get("/api/analysis/report")
async def generate_report():
    """生成课堂分析报告"""
    analyzer = ConversationAnalyzer(conversation_history)
    report = analyzer.generate_summary_report()
    
    return {
        "report": report,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/reminder/keyword")
async def add_reminder_keyword(keyword: str):
    """添加提醒关键词"""
    smart_reminder.add_keyword(keyword)
    return {"message": f"已添加关键词: {keyword}"}


@app.delete("/api/reminder/keyword")
async def remove_reminder_keyword(keyword: str):
    """移除提醒关键词"""
    smart_reminder.remove_keyword(keyword)
    return {"message": f"已移除关键词: {keyword}"}


@app.get("/api/reminder/unanswered")
async def get_unanswered_questions():
    """获取未回答的问题"""
    return {
        "questions": smart_reminder.get_unanswered_questions()
    }


# ==================== 个性化设置 API ====================

@app.get("/api/settings")
async def get_settings():
    """获取所有设置"""
    return settings_manager.get_all()


@app.get("/api/settings/{key}")
async def get_setting(key: str):
    """获取指定设置"""
    value = settings_manager.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="设置不存在")
    return {"key": key, "value": value}


@app.post("/api/settings/{key}")
async def update_setting(key: str, value: dict):
    """更新设置"""
    settings_manager.set(key, value.get("value"))
    return {"message": f"设置 {key} 已更新"}


@app.post("/api/settings/reset")
async def reset_settings():
    """重置所有设置"""
    settings_manager.reset()
    return {"message": "设置已重置为默认值"}


# 快捷回复
@app.get("/api/quick-replies")
async def get_quick_replies():
    """获取快捷回复列表"""
    return {"replies": settings_manager.get_quick_replies()}


@app.post("/api/quick-replies")
async def add_quick_reply(text: str):
    """添加快捷回复"""
    settings_manager.add_quick_reply(text)
    return {"message": f"已添加快捷回复: {text}"}


@app.delete("/api/quick-replies")
async def remove_quick_reply(text: str):
    """删除快捷回复"""
    settings_manager.remove_quick_reply(text)
    return {"message": f"已删除快捷回复: {text}"}


# 学生管理
@app.get("/api/students")
async def get_students():
    """获取学生列表"""
    return {"students": settings_manager.get_students()}


@app.post("/api/students")
async def add_student(name: str, info: dict = None):
    """添加学生"""
    settings_manager.add_student(name, info)
    return {"message": f"已添加学生: {name}"}


@app.delete("/api/students/{name}")
async def remove_student(name: str):
    """删除学生"""
    settings_manager.remove_student(name)
    return {"message": f"已删除学生: {name}"}


# Prompt 模板
@app.get("/api/prompt/current")
async def get_current_prompt():
    """获取当前 Prompt 模板"""
    return {
        "style": settings_manager.get("reply_style"),
        "prompt": settings_manager.get_current_prompt()
    }


@app.post("/api/prompt/custom")
async def set_custom_prompt(style: str, prompt: str):
    """设置自定义 Prompt"""
    settings_manager.set_custom_prompt(style, prompt)
    return {"message": f"已设置 {style} 风格的 Prompt"}


# ==================== 课堂会话管理 API ====================

@app.post("/api/session/start")
async def start_session(topic: str = ""):
    """开始新的课堂会话"""
    session = session_history.start_session(topic)
    return {
        "message": "课堂会话已开始",
        "session": session.to_dict()
    }


@app.post("/api/session/end")
async def end_session():
    """结束当前课堂会话"""
    if not session_history.current_session:
        raise HTTPException(status_code=400, detail="没有进行中的会话")
    
    session_history.end_session(conversation_history)
    return {"message": "课堂会话已结束"}


@app.get("/api/session/current")
async def get_current_session():
    """获取当前会话信息"""
    if not session_history.current_session:
        return {"session": None}
    
    return {"session": session_history.current_session.to_dict()}


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """获取指定会话"""
    session = session_history.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return {"session": session.to_dict()}


@app.get("/api/sessions/recent")
async def get_recent_sessions(days: int = 7):
    """获取最近的会话"""
    sessions = session_history.get_recent_sessions(days)
    return {
        "sessions": [s.to_dict() for s in sessions],
        "count": len(sessions)
    }


@app.get("/api/sessions/all")
async def get_all_sessions():
    """获取所有会话"""
    sessions = session_history.get_all_sessions()
    return {
        "sessions": [s.to_dict() for s in sessions],
        "count": len(sessions)
    }


@app.get("/api/sessions/statistics")
async def get_session_statistics(days: int = 30):
    """获取会话统计数据"""
    stats = session_history.get_statistics(days)
    return stats


@app.get("/api/sessions/compare")
async def compare_sessions(session_id1: str, session_id2: str):
    """对比两个会话"""
    comparison = session_history.compare_sessions(session_id1, session_id2)
    if not comparison:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return comparison


@app.post("/api/session/{session_id}/note")
async def add_session_note(session_id: str, note: str):
    """为会话添加备注"""
    session_history.add_note(session_id, note)
    return {"message": "备注已添加"}


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
    try:
        await manager.connect(websocket)
        logger.info("WebSocket 连接已建立")
        
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket 连接成功"
        })
        
        logger.info("开始接收消息循环")
        
        while True:
            # 接收消息
            logger.debug("等待接收消息...")
            data = await websocket.receive_json()
            logger.info(f"收到消息: {data}")
            message_type = data.get("type")
            
            if message_type == "transcript":
                # 收到转写文本
                await handle_transcript(websocket, data)
            
            elif message_type == "audio":
                # 收到音频数据（暂时不处理，后续可用于声纹识别）
                pass
            
            elif message_type == "start_listening":
                # 开始监听
                logger.info("开始监听音频")
                await websocket.send_json({
                    "type": "status",
                    "status": "listening",
                    "message": "开始监听"
                })
            
            elif message_type == "stop_listening":
                # 停止监听
                logger.info("停止监听音频")
                await websocket.send_json({
                    "type": "status",
                    "status": "stopped",
                    "message": "停止监听"
                })
            
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
        logger.info("WebSocket 连接断开")
    
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}", exc_info=True)
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

