"""
音频处理工具
"""
import numpy as np
from typing import Optional, Tuple
import struct


class AudioProcessor:
    """音频处理器"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        """
        初始化音频处理器
        
        Args:
            sample_rate: 采样率
            channels: 声道数
        """
        self.sample_rate = sample_rate
        self.channels = channels
    
    def bytes_to_numpy(self, audio_bytes: bytes) -> np.ndarray:
        """
        将字节流转换为 numpy 数组
        
        Args:
            audio_bytes: PCM 音频字节流
            
        Returns:
            numpy 数组
        """
        # 假设是 16-bit PCM
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        return audio_array
    
    def numpy_to_bytes(self, audio_array: np.ndarray) -> bytes:
        """
        将 numpy 数组转换为字节流
        
        Args:
            audio_array: numpy 数组
            
        Returns:
            PCM 音频字节流
        """
        return audio_array.astype(np.int16).tobytes()
    
    def normalize_volume(self, audio_array: np.ndarray, target_db: float = -20.0) -> np.ndarray:
        """
        音量归一化
        
        Args:
            audio_array: 音频数组
            target_db: 目标音量（dB）
            
        Returns:
            归一化后的音频数组
        """
        if len(audio_array) == 0:
            return audio_array
        
        # 计算当前 RMS
        rms = np.sqrt(np.mean(audio_array.astype(float) ** 2))
        
        if rms == 0:
            return audio_array
        
        # 计算目标 RMS
        target_rms = 10 ** (target_db / 20) * 32768
        
        # 归一化
        scale = target_rms / rms
        normalized = audio_array * scale
        
        # 防止溢出
        normalized = np.clip(normalized, -32768, 32767)
        
        return normalized.astype(np.int16)
    
    def apply_noise_gate(self, audio_array: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """
        应用噪声门（简单降噪）
        
        Args:
            audio_array: 音频数组
            threshold: 阈值（0-1）
            
        Returns:
            处理后的音频数组
        """
        # 归一化到 -1 到 1
        normalized = audio_array.astype(float) / 32768.0
        
        # 应用噪声门
        mask = np.abs(normalized) > threshold
        gated = normalized * mask
        
        # 转回 int16
        return (gated * 32768).astype(np.int16)
    
    def calculate_rms(self, audio_array: np.ndarray) -> float:
        """
        计算音频的 RMS（均方根）值
        
        Args:
            audio_array: 音频数组
            
        Returns:
            RMS 值（0-1）
        """
        if len(audio_array) == 0:
            return 0.0
        
        normalized = audio_array.astype(float) / 32768.0
        rms = np.sqrt(np.mean(normalized ** 2))
        return float(rms)
    
    def detect_silence(self, audio_array: np.ndarray, threshold: float = 0.01) -> bool:
        """
        检测是否为静音
        
        Args:
            audio_array: 音频数组
            threshold: 静音阈值
            
        Returns:
            是否为静音
        """
        rms = self.calculate_rms(audio_array)
        return rms < threshold
    
    def resample(self, audio_array: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """
        重采样（简单线性插值）
        
        Args:
            audio_array: 原始音频数组
            orig_sr: 原始采样率
            target_sr: 目标采样率
            
        Returns:
            重采样后的音频数组
        """
        if orig_sr == target_sr:
            return audio_array
        
        duration = len(audio_array) / orig_sr
        target_length = int(duration * target_sr)
        
        # 使用线性插值
        indices = np.linspace(0, len(audio_array) - 1, target_length)
        resampled = np.interp(indices, np.arange(len(audio_array)), audio_array)
        
        return resampled.astype(np.int16)


# 全局实例
audio_processor = AudioProcessor()

