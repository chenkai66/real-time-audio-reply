"""
WebSocket 路由处理
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.websocket.manager import manager
from backend.core.role import RoleIdentifier
from backend.core.generator import ReplyGenerator
from backend.core.conversation import conversation_history
from backend.services.asr_service import asr_service
import json
import logging
import numpy as np

logger = logging.getLogger(__name__)

router = APIRouter()

# 初始化服务
role_identifier = RoleIdentifier()
reply_generator = ReplyGenerator()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket 端点"""
    await manager.connect(websocket, user_id)
    
    # 创建 ASR 会话
    asr = None
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理不同类型的消息
            message_type = message.get("type")
            
            if message_type == "start_listening":
                # 开始监听 - 创建 ASR 会话
                if not asr:
                    asr = await asr_service.create_session(user_id)
                    
                    # 设置 ASR 回调
                    asr.set_result_callback(
                        lambda result: handle_asr_result(user_id, result)
                    )
                    asr.set_error_callback(
                        lambda error: manager.send_error(user_id, f"ASR 错误: {error}")
                    )
                    
                    # 开始识别
                    await asr.start_recognition(sample_rate=16000)
                    await manager.send_status(user_id, "listening", "正在监听...")
            
            elif message_type == "stop_listening":
                # 停止监听
                if asr:
                    await asr.stop_recognition()
                    await manager.send_status(user_id, "idle", "已停止监听")
            
            elif message_type == "audio":
                # 处理音频数据
                await handle_audio(user_id, message.get("data", []), asr)
            
            elif message_type == "transcript":
                # 处理文本输入（用于测试）
                await handle_transcript(user_id, message.get("text", ""), message.get("role"))
            
            elif message_type == "ping":
                # 心跳响应
                await manager.send_message(user_id, {"type": "pong"})
            
            else:
                logger.warning(f"未知消息类型: {message_type}")
    
    except WebSocketDisconnect:
        # 清理 ASR 会话
        if asr:
            await asr_service.remove_session(user_id)
        await manager.disconnect(user_id)
        logger.info(f"WebSocket 连接断开: {user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
        await manager.send_error(user_id, str(e))
        if asr:
            await asr_service.remove_session(user_id)
        await manager.disconnect(user_id)


async def handle_audio(user_id: str, audio_data: list, asr=None):
    """
    处理音频数据
    
    Args:
        user_id: 用户ID
        audio_data: 音频数据（Int16 数组）
        asr: ASR 实例
    """
    if not audio_data:
        return
    
    session = manager.get_session(user_id)
    if not session:
        return
    
    try:
        # 将音频数据转换为字节
        audio_array = np.array(audio_data, dtype=np.int16)
        audio_bytes = audio_array.tobytes()
        
        # 发送到 ASR 服务
        if asr and asr.is_running:
            await asr.send_audio(audio_bytes)
            logger.debug(f"发送音频数据: {len(audio_bytes)} 字节")
        else:
            # ASR 未启动，暂存音频数据
            session["audio_buffer"].extend(audio_data)
            
            # 当缓冲区达到一定大小时记录
            if len(session["audio_buffer"]) > 16000:  # 约 1 秒
                logger.info(f"收到音频数据: {len(session['audio_buffer'])} 样本（ASR 未启动）")
                session["audio_buffer"] = []
    
    except Exception as e:
        logger.error(f"处理音频失败: {e}")
        await manager.send_error(user_id, f"音频处理失败: {str(e)}")


async def handle_asr_result(user_id: str, result: dict):
    """
    处理 ASR 识别结果
    
    Args:
        user_id: 用户ID
        result: 识别结果
            - text: 识别文本
            - is_final: 是否为最终结果
            - confidence: 置信度
    """
    text = result.get("text", "")
    is_final = result.get("is_final", False)
    
    if not text:
        return
    
    logger.info(f"ASR 结果 ({'最终' if is_final else '中间'}): {text}")
    
    # 如果是最终结果，进行完整处理
    if is_final:
        await handle_transcript(user_id, text, role=None)
    else:
        # 中间结果，只发送给前端显示
        await manager.send_message(user_id, {
            "type": "transcript_partial",
            "text": text,
            "timestamp": None
        })


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

