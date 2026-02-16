"""
测试角色识别模块
"""
import pytest
import numpy as np
from backend.core.role import Role, RoleIdentifier, VoiceFeature


class TestVoiceFeature:
    """测试 VoiceFeature 类"""
    
    def test_init(self):
        """测试初始化"""
        feature = VoiceFeature(pitch=100.0, energy=0.5, speech_rate=1.0)
        assert feature.pitch == 100.0
        assert feature.energy == 0.5
        assert feature.speech_rate == 1.0
    
    def test_distance_same(self):
        """测试相同特征的距离"""
        f1 = VoiceFeature(100.0, 0.5, 1.0)
        f2 = VoiceFeature(100.0, 0.5, 1.0)
        assert f1.distance(f2) == 0.0
    
    def test_distance_different(self):
        """测试不同特征的距离"""
        f1 = VoiceFeature(100.0, 0.5, 1.0)
        f2 = VoiceFeature(110.0, 0.6, 1.1)
        distance = f1.distance(f2)
        assert distance > 0
        assert distance < 20  # 应该是一个合理的值


class TestRoleIdentifier:
    """测试 RoleIdentifier 类"""
    
    def test_init(self):
        """测试初始化"""
        identifier = RoleIdentifier()
        assert identifier.similarity_threshold == 0.8
        assert len(identifier.role_features[Role.TEACHER]) == 0
        assert len(identifier.role_features[Role.STUDENT]) == 0
    
    def test_extract_voice_features(self):
        """测试声纹特征提取"""
        identifier = RoleIdentifier()
        
        # 创建测试音频（正弦波）
        t = np.linspace(0, 1, 16000)
        audio = (np.sin(2 * np.pi * 440 * t) * 10000).astype(np.int16)
        
        feature = identifier.extract_voice_features(audio)
        assert isinstance(feature, VoiceFeature)
        assert feature.pitch > 0
        assert feature.energy > 0
        assert feature.speech_rate > 0
    
    def test_extract_voice_features_silence(self):
        """测试静音的特征提取"""
        identifier = RoleIdentifier()
        silence = np.zeros(1000, dtype=np.int16)
        
        feature = identifier.extract_voice_features(silence)
        assert feature.energy == 0.0
    
    def test_register_role(self):
        """测试注册角色"""
        identifier = RoleIdentifier()
        
        # 创建测试音频
        audio = np.random.randint(-1000, 1000, 1000, dtype=np.int16)
        
        identifier.register_role(Role.TEACHER, audio)
        assert len(identifier.role_features[Role.TEACHER]) == 1
    
    def test_register_role_limit(self):
        """测试角色特征数量限制"""
        identifier = RoleIdentifier()
        
        # 注册超过 10 个特征
        for i in range(15):
            audio = np.random.randint(-1000, 1000, 1000, dtype=np.int16)
            identifier.register_role(Role.TEACHER, audio)
        
        # 应该只保留最新的 10 个
        assert len(identifier.role_features[Role.TEACHER]) == 10
    
    def test_identify_by_voice_no_features(self):
        """测试没有已知特征时的声纹识别"""
        identifier = RoleIdentifier()
        audio = np.random.randint(-1000, 1000, 1000, dtype=np.int16)
        
        result = identifier.identify_by_voice(audio)
        assert result is None
    
    def test_identify_by_voice_with_features(self):
        """测试有已知特征时的声纹识别"""
        identifier = RoleIdentifier()
        
        # 注册教师特征
        teacher_audio = np.random.randint(-1000, 1000, 1000, dtype=np.int16)
        identifier.register_role(Role.TEACHER, teacher_audio)
        
        # 使用相似的音频测试（这里用相同的，实际应该相似但不同）
        result = identifier.identify_by_voice(teacher_audio)
        # 由于是完全相同的音频，应该能识别出来
        assert result == Role.TEACHER
    
    def test_clear_role_features_single(self):
        """测试清除单个角色特征"""
        identifier = RoleIdentifier()
        
        audio = np.random.randint(-1000, 1000, 1000, dtype=np.int16)
        identifier.register_role(Role.TEACHER, audio)
        identifier.register_role(Role.STUDENT, audio)
        
        identifier.clear_role_features(Role.TEACHER)
        assert len(identifier.role_features[Role.TEACHER]) == 0
        assert len(identifier.role_features[Role.STUDENT]) == 1
    
    def test_clear_role_features_all(self):
        """测试清除所有角色特征"""
        identifier = RoleIdentifier()
        
        audio = np.random.randint(-1000, 1000, 1000, dtype=np.int16)
        identifier.register_role(Role.TEACHER, audio)
        identifier.register_role(Role.STUDENT, audio)
        
        identifier.clear_role_features()
        assert len(identifier.role_features[Role.TEACHER]) == 0
        assert len(identifier.role_features[Role.STUDENT]) == 0
    
    @pytest.mark.asyncio
    async def test_identify_by_content_teacher(self):
        """测试通过内容识别教师（需要 API）"""
        identifier = RoleIdentifier()
        
        # 典型的教师发言
        text = "今天我们来学习 Python 的基础语法，首先是变量的定义。"
        
        # 这个测试需要真实的 API，如果没有配置会返回 UNKNOWN
        role = await identifier.identify_by_content(text)
        assert role in [Role.TEACHER, Role.UNKNOWN]
    
    @pytest.mark.asyncio
    async def test_identify_by_content_student(self):
        """测试通过内容识别学生（需要 API）"""
        identifier = RoleIdentifier()
        
        # 典型的学生提问
        text = "老师，我不太明白这个变量是什么意思，能再解释一下吗？"
        
        role = await identifier.identify_by_content(text)
        assert role in [Role.STUDENT, Role.UNKNOWN]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

