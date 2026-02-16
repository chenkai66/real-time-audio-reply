"""
角色识别模块
用于区分教师和学生的发言
"""
from typing import Optional, Dict, List
from enum import Enum
import numpy as np
from backend.services.openai_service import openai_service
from backend.utils.audio import AudioProcessor


class Role(str, Enum):
    """角色枚举"""
    TEACHER = "teacher"
    STUDENT = "student"
    UNKNOWN = "unknown"


class VoiceFeature:
    """声纹特征（简化版）"""
    
    def __init__(self, pitch: float, energy: float, speech_rate: float):
        """
        初始化声纹特征
        
        Args:
            pitch: 音高
            energy: 能量
            speech_rate: 语速
        """
        self.pitch = pitch
        self.energy = energy
        self.speech_rate = speech_rate
    
    def distance(self, other: 'VoiceFeature') -> float:
        """
        计算与另一个特征的距离
        
        Args:
            other: 另一个声纹特征
            
        Returns:
            欧氏距离
        """
        return np.sqrt(
            (self.pitch - other.pitch) ** 2 +
            (self.energy - other.energy) ** 2 +
            (self.speech_rate - other.speech_rate) ** 2
        )


class RoleIdentifier:
    """角色识别器"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        """
        初始化角色识别器
        
        Args:
            similarity_threshold: 声纹相似度阈值
        """
        self.similarity_threshold = similarity_threshold
        self.role_features: Dict[Role, List[VoiceFeature]] = {
            Role.TEACHER: [],
            Role.STUDENT: []
        }
        self.audio_processor = AudioProcessor()
    
    async def identify_by_content(self, text: str, context: Optional[str] = None) -> Role:
        """
        通过内容识别角色
        
        Args:
            text: 语音转写文本
            context: 上下文信息
            
        Returns:
            识别的角色
        """
        if not openai_service:
            return Role.UNKNOWN
        
        system_prompt = """你是一个角色识别助手。根据对话内容判断说话人是教师还是学生。

判断规则：
1. 教师通常：讲解知识、回答问题、引导讨论、布置任务
2. 学生通常：提出问题、请求解释、表达困惑、回答教师提问

请只回复 "teacher" 或 "student"，不要有其他内容。"""
        
        prompt = f"对话内容：{text}"
        if context:
            prompt = f"上下文：{context}\n\n当前对话：{text}"
        
        try:
            response = await openai_service.simple_chat(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            response = response.strip().lower()
            if "teacher" in response:
                return Role.TEACHER
            elif "student" in response:
                return Role.STUDENT
            else:
                return Role.UNKNOWN
        except Exception as e:
            print(f"角色识别错误: {e}")
            return Role.UNKNOWN
    
    def extract_voice_features(self, audio_data: np.ndarray) -> VoiceFeature:
        """
        提取声纹特征（简化版）
        
        Args:
            audio_data: 音频数据
            
        Returns:
            声纹特征
        """
        # 简化的特征提取
        # 实际应用中应该使用更复杂的算法（如 MFCC）
        
        # 音高估算（基于零交叉率）
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_data)))) / 2
        pitch = zero_crossings / len(audio_data) * 16000  # 归一化
        
        # 能量
        energy = self.audio_processor.calculate_rms(audio_data)
        
        # 语速估算（基于能量变化）
        energy_changes = np.sum(np.abs(np.diff(audio_data.astype(float))))
        speech_rate = energy_changes / len(audio_data)
        
        return VoiceFeature(pitch, energy, speech_rate)
    
    def identify_by_voice(self, audio_data: np.ndarray) -> Optional[Role]:
        """
        通过声纹识别角色
        
        Args:
            audio_data: 音频数据
            
        Returns:
            识别的角色，如果无法识别返回 None
        """
        if not audio_data.size:
            return None
        
        feature = self.extract_voice_features(audio_data)
        
        # 与已知角色特征比较
        best_role = None
        min_distance = float('inf')
        
        for role, features in self.role_features.items():
            if not features:
                continue
            
            # 计算与该角色所有特征的平均距离
            distances = [feature.distance(f) for f in features]
            avg_distance = np.mean(distances)
            
            if avg_distance < min_distance:
                min_distance = avg_distance
                best_role = role
        
        # 如果距离太大，说明不匹配
        if min_distance > (1 - self.similarity_threshold):
            return None
        
        return best_role
    
    async def identify(
        self,
        text: str,
        audio_data: Optional[np.ndarray] = None,
        context: Optional[str] = None
    ) -> Role:
        """
        综合识别角色（声纹 + 内容）
        
        Args:
            text: 语音转写文本
            audio_data: 音频数据（可选）
            context: 上下文信息（可选）
            
        Returns:
            识别的角色
        """
        # 先尝试声纹识别
        if audio_data is not None and audio_data.size > 0:
            voice_role = self.identify_by_voice(audio_data)
            if voice_role:
                return voice_role
        
        # 声纹识别失败，使用内容识别
        content_role = await self.identify_by_content(text, context)
        return content_role
    
    def register_role(self, role: Role, audio_data: np.ndarray) -> None:
        """
        注册角色的声纹特征
        
        Args:
            role: 角色
            audio_data: 音频数据
        """
        if not audio_data.size:
            return
        
        feature = self.extract_voice_features(audio_data)
        self.role_features[role].append(feature)
        
        # 限制特征数量，避免内存占用过大
        if len(self.role_features[role]) > 10:
            self.role_features[role].pop(0)
    
    def clear_role_features(self, role: Optional[Role] = None) -> None:
        """
        清除角色特征
        
        Args:
            role: 要清除的角色，如果为 None 则清除所有
        """
        if role:
            self.role_features[role] = []
        else:
            for r in Role:
                if r != Role.UNKNOWN:
                    self.role_features[r] = []


# 全局实例
role_identifier = RoleIdentifier()

