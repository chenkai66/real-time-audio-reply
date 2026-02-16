"""
测试音频处理工具
"""
import pytest
import numpy as np
from backend.utils.audio import AudioProcessor, audio_processor


class TestAudioProcessor:
    """测试 AudioProcessor 类"""
    
    def test_init(self):
        """测试初始化"""
        processor = AudioProcessor()
        assert processor.sample_rate == 16000
        assert processor.channels == 1
        
        processor2 = AudioProcessor(sample_rate=8000, channels=2)
        assert processor2.sample_rate == 8000
        assert processor2.channels == 2
    
    def test_bytes_to_numpy(self):
        """测试字节流转 numpy"""
        processor = AudioProcessor()
        # 创建测试数据：10 个 16-bit 整数
        test_data = np.array([100, 200, -100, -200, 0, 1000, -1000, 5000, -5000, 0], dtype=np.int16)
        audio_bytes = test_data.tobytes()
        
        result = processor.bytes_to_numpy(audio_bytes)
        assert isinstance(result, np.ndarray)
        assert len(result) == len(test_data)
        np.testing.assert_array_equal(result, test_data)
    
    def test_numpy_to_bytes(self):
        """测试 numpy 转字节流"""
        processor = AudioProcessor()
        test_data = np.array([100, 200, -100, -200, 0], dtype=np.int16)
        
        result = processor.numpy_to_bytes(test_data)
        assert isinstance(result, bytes)
        assert len(result) == len(test_data) * 2  # 16-bit = 2 bytes
        
        # 转回来验证
        recovered = processor.bytes_to_numpy(result)
        np.testing.assert_array_equal(recovered, test_data)
    
    def test_calculate_rms_silence(self):
        """测试静音的 RMS"""
        processor = AudioProcessor()
        silence = np.zeros(1000, dtype=np.int16)
        rms = processor.calculate_rms(silence)
        assert rms == 0.0
    
    def test_calculate_rms_signal(self):
        """测试有信号的 RMS"""
        processor = AudioProcessor()
        # 创建一个简单的正弦波
        t = np.linspace(0, 1, 16000)
        signal = (np.sin(2 * np.pi * 440 * t) * 10000).astype(np.int16)
        
        rms = processor.calculate_rms(signal)
        assert rms > 0
        assert rms < 1.0
    
    def test_detect_silence_true(self):
        """测试检测静音（真）"""
        processor = AudioProcessor()
        silence = np.zeros(1000, dtype=np.int16)
        assert processor.detect_silence(silence) is True
    
    def test_detect_silence_false(self):
        """测试检测静音（假）"""
        processor = AudioProcessor()
        # 创建有信号的音频
        signal = np.random.randint(-1000, 1000, 1000, dtype=np.int16)
        assert processor.detect_silence(signal) is False
    
    def test_normalize_volume(self):
        """测试音量归一化"""
        processor = AudioProcessor()
        # 创建一个低音量信号
        signal = np.array([10, 20, -10, -20, 0] * 100, dtype=np.int16)
        
        normalized = processor.normalize_volume(signal)
        assert isinstance(normalized, np.ndarray)
        assert len(normalized) == len(signal)
        
        # 归一化后的 RMS 应该更大
        original_rms = processor.calculate_rms(signal)
        normalized_rms = processor.calculate_rms(normalized)
        assert normalized_rms > original_rms
    
    def test_normalize_volume_empty(self):
        """测试空数组归一化"""
        processor = AudioProcessor()
        empty = np.array([], dtype=np.int16)
        result = processor.normalize_volume(empty)
        assert len(result) == 0
    
    def test_normalize_volume_zero(self):
        """测试全零数组归一化"""
        processor = AudioProcessor()
        zeros = np.zeros(100, dtype=np.int16)
        result = processor.normalize_volume(zeros)
        np.testing.assert_array_equal(result, zeros)
    
    def test_apply_noise_gate(self):
        """测试噪声门"""
        processor = AudioProcessor()
        # 创建混合信号：大信号 + 小噪声
        signal = np.concatenate([
            np.array([1000, 2000, -1000, -2000] * 10, dtype=np.int16),  # 大信号
            np.array([10, 20, -10, -20] * 10, dtype=np.int16)  # 小噪声
        ])
        
        gated = processor.apply_noise_gate(signal, threshold=0.05)
        assert isinstance(gated, np.ndarray)
        assert len(gated) == len(signal)
    
    def test_resample_same_rate(self):
        """测试相同采样率重采样"""
        processor = AudioProcessor()
        signal = np.array([100, 200, 300, 400, 500], dtype=np.int16)
        
        resampled = processor.resample(signal, 16000, 16000)
        np.testing.assert_array_equal(resampled, signal)
    
    def test_resample_downsample(self):
        """测试降采样"""
        processor = AudioProcessor()
        signal = np.array([100, 200, 300, 400, 500, 600, 700, 800], dtype=np.int16)
        
        # 从 16000 降到 8000（减半）
        resampled = processor.resample(signal, 16000, 8000)
        assert len(resampled) == len(signal) // 2
    
    def test_resample_upsample(self):
        """测试升采样"""
        processor = AudioProcessor()
        signal = np.array([100, 200, 300, 400], dtype=np.int16)
        
        # 从 8000 升到 16000（加倍）
        resampled = processor.resample(signal, 8000, 16000)
        assert len(resampled) == len(signal) * 2
    
    def test_global_instance(self):
        """测试全局实例"""
        assert audio_processor is not None
        assert audio_processor.sample_rate == 16000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

