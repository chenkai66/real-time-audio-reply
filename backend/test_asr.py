"""
测试 ASR 服务
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.asr_service import DashScopeASR
import numpy as np


async def test_asr():
    """测试 ASR 服务"""
    
    print("🧪 测试 DashScope ASR 服务")
    print("=" * 50)
    
    # 检查 API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误: DASHSCOPE_API_KEY 未设置")
        print("请在 .env 文件中设置有效的 API Key")
        return
    
    print(f"✅ API Key: {api_key[:10]}...")
    
    # 创建 ASR 实例
    asr = DashScopeASR(api_key)
    
    # 设置回调
    results = []
    
    async def on_result(result):
        text = result.get("text", "")
        is_final = result.get("is_final", False)
        confidence = result.get("confidence", 0)
        
        print(f"\n{'[最终]' if is_final else '[中间]'} {text} (置信度: {confidence:.2f})")
        
        if is_final:
            results.append(text)
    
    async def on_error(error):
        print(f"\n❌ 错误: {error}")
    
    asr.set_result_callback(on_result)
    asr.set_error_callback(on_error)
    
    try:
        # 连接
        print("\n📡 正在连接...")
        await asr.connect()
        
        # 开始识别
        print("🎤 开始识别...")
        await asr.start_recognition(sample_rate=16000)
        
        # 模拟发送音频数据（静音）
        print("📤 发送测试音频数据...")
        
        # 生成 5 秒的静音音频（用于测试连接）
        sample_rate = 16000
        duration = 5  # 秒
        chunk_size = 3200  # 200ms
        
        for i in range(int(sample_rate * duration / chunk_size)):
            # 生成静音数据
            audio_chunk = np.zeros(chunk_size, dtype=np.int16)
            audio_bytes = audio_chunk.tobytes()
            
            await asr.send_audio(audio_bytes)
            await asyncio.sleep(0.2)  # 200ms
            
            if i % 5 == 0:
                print(f"  已发送 {i * chunk_size / sample_rate:.1f} 秒")
        
        print("\n✅ 测试音频发送完成")
        
        # 等待识别结果
        print("⏳ 等待识别结果...")
        await asyncio.sleep(2)
        
        # 停止识别
        print("\n🛑 停止识别...")
        await asr.stop_recognition()
        
        # 断开连接
        print("📴 断开连接...")
        await asr.disconnect()
        
        # 显示结果
        print("\n" + "=" * 50)
        print("📊 测试结果:")
        if results:
            for i, text in enumerate(results, 1):
                print(f"  {i}. {text}")
        else:
            print("  (无识别结果 - 这是正常的，因为发送的是静音)")
        
        print("\n✅ ASR 服务测试完成！")
        print("\n💡 提示:")
        print("  - 如果连接成功，说明 API Key 有效")
        print("  - 如果能发送音频，说明 WebSocket 通信正常")
        print("  - 实际使用时，需要发送真实的语音数据")
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_asr())

