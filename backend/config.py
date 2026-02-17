"""
数据存储配置
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据存储目录
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# 日志目录
LOGS_DIR = DATA_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# 对话记录目录
CONVERSATIONS_DIR = DATA_DIR / "conversations"
CONVERSATIONS_DIR.mkdir(exist_ok=True)

# 会话历史目录
SESSIONS_DIR = DATA_DIR / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

# 分析报告目录
REPORTS_DIR = DATA_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# 音频文件目录（本地临时存储）
AUDIO_DIR = DATA_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

# 导出文件目录
EXPORTS_DIR = DATA_DIR / "exports"
EXPORTS_DIR.mkdir(exist_ok=True)

# 文件路径配置
SETTINGS_FILE = DATA_DIR / "settings.json"
SESSIONS_FILE = SESSIONS_DIR / "sessions.json"
CONVERSATION_CACHE_FILE = CONVERSATIONS_DIR / "current.json"

# 日志文件配置
LOG_FILE = LOGS_DIR / "app.log"
ERROR_LOG_FILE = LOGS_DIR / "error.log"
ACCESS_LOG_FILE = LOGS_DIR / "access.log"

# OSS 配置（从环境变量读取）
OSS_ENABLED = os.getenv("OSS_ENABLED", "false").lower() == "true"
OSS_BUCKET = os.getenv("OSS_BUCKET", "audio-input-data")
OSS_REGION = os.getenv("OSS_REGION", "oss-cn-beijing")
OSS_ACCESS_KEY_ID = os.getenv("ALIYUN_ACCESS_KEY_ID", "")
OSS_ACCESS_KEY_SECRET = os.getenv("ALIYUN_ACCESS_KEY_SECRET", "")

# OSS 存储路径前缀
OSS_AUDIO_PREFIX = "audio/"
OSS_CONVERSATIONS_PREFIX = "conversations/"
OSS_REPORTS_PREFIX = "reports/"
OSS_EXPORTS_PREFIX = "exports/"

# 数据保留策略
CONVERSATION_RETENTION_DAYS = 30  # 对话记录保留天数
SESSION_RETENTION_DAYS = 90  # 会话历史保留天数
LOG_RETENTION_DAYS = 7  # 日志保留天数
AUDIO_RETENTION_HOURS = 24  # 音频文件保留小时数

# 自动备份配置
AUTO_BACKUP_ENABLED = True
BACKUP_INTERVAL_HOURS = 24
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

print(f"""
📁 数据存储配置
================
数据目录: {DATA_DIR}
日志目录: {LOGS_DIR}
对话记录: {CONVERSATIONS_DIR}
会话历史: {SESSIONS_DIR}
分析报告: {REPORTS_DIR}
音频文件: {AUDIO_DIR}
导出文件: {EXPORTS_DIR}
备份目录: {BACKUP_DIR}

OSS 存储: {'✅ 已启用' if OSS_ENABLED else '❌ 未启用'}
""")

