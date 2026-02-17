"""
WebSocket 路由处理
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.websocket.manager import manager
from backend.core.role import RoleIdentifier
from backend.core.generator import ReplyGenerator
from backend.core.conversation import conversation_history
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 初始化服务
role_identifier = RoleIdentifier()
reply_generator = ReplyGenerator()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket 端点"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理不同类型的消息
            message_type = message.get("type")
            
            if message_type == "audio":
                # 处理音频数据
                await handle_audio(user_id, message.get("data", []))
            
            elif message_type == "transcript":
                # 处理文本输入（用于测试）
                await handle_transcript(user_id, message.get("text", ""), message.get("role"))
            
            elif message_type == "ping":
                # 心跳响应
                await manager.send_message(user_id, {"type": "pong"})
            
            else:
                logger.warning(f"未知消息类型: {message_type}")
    
    except WebSocketDisconnect:
        await manager.disconnect(user_id)
        logger.info(f"WebSocket 连接断开: {user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
        await manager.send_error(user_id, str(e))
        await manager.disconnect(user_id)


async def handle_audio(user_id: str, audio_data: list):
    """
    处理音频数据
    
    TODO: 集成 ASR 服务
    当前版本：暂存音频数据，等待 ASR 集成
    """
    session = manager.get_session(user_id)
    if not session:
        return
    
    # 暂存音频数据
    session["audio_buffer"].extend(audio_data)
    
    # 当缓冲区达到一定大小时，可以发送到 ASR 服务
    # 这里先简单记录
    if len(session["audio_buffer"]) > 16000:  # 约 1 秒的音频
        logger.info(f"收到音频数据: {len(session['audio_buffer'])} 样本")
        session["audio_buffer"] = []  # 清空缓冲区
        
        # TODO: 发送到 ASR 服务进行识别
        # 当前版本：发送状态更新
        await manager.send_status(user_id, "processing", "正在识别语音...")


async def handle_transcript(user_id: str, text: str, role: str = None):
    """
    处理转写结果（或文本输入）
    
    Args:
        user_id: 用户ID
        text: 文本内容
        role: 角色（如果已知）
    """
    if not text:
        return
    
    try:
        # 1. 角色识别
        await manager.send_status(user_id, "processing", "正在识别角色...")
        
        if not role:
            role = role_identifier.identify_role(text)
        
        # 2. 添加到对话历史
        conversation_history.add_turn(role, text)
        
        # 3. 发送转写结果
        await manager.send_transcript(user_id, text, role)
        
        # 4. 如果是学生提问，生成回复
        if role == "student" and role_identifier.is_question(text):
            await manager.send_status(user_id, "generating", "正在生成回复...")
            
            # 获取上下文
            context = conversation_history.get_context()
            
            # 生成回复
            reply = await reply_generator.generate_reply(text, context)
            
            # 添加回复到历史
            conversation_history.add_turn("teacher", reply)
            
            # 发送回复
            await manager.send_reply(user_id, reply)
        
        logger.info(f"处理完成: {role} - {text[:50]}...")
    
    except Exception as e:
        logger.error(f"处理转写失败: {e}")
        await manager.send_error(user_id, f"处理失败: {str(e)}")

