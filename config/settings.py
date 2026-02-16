"""
配置管理模块
从环境变量加载配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # API Keys
    dashscope_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    openai_model: str = "qwen-plus"
    
    # 阿里云 OSS
    aliyun_access_key_id: Optional[str] = None
    aliyun_access_key_secret: Optional[str] = None
    oss_bucket: str = "audio-input-data"
    oss_region: str = "oss-cn-beijing"
    
    # 应用配置
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    
    # 音频配置
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    audio_chunk_size: int = 3200
    
    # 压缩策略配置
    l1_cache_size: int = 2
    l2_cache_size: int = 3
    compression_threshold: int = 3000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()

