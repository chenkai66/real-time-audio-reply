"""
个性化设置管理模块
支持教师自定义回复风格、快捷模板等
"""
import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


class SettingsManager:
    """设置管理器"""
    
    def __init__(self, settings_file: str = "user_settings.json"):
        """
        初始化设置管理器
        
        Args:
            settings_file: 设置文件路径
        """
        self.settings_file = Path(settings_file)
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict:
        """加载设置"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # 默认设置
        return {
            "teacher_name": "老师",
            "reply_style": "professional",  # professional, friendly, humorous
            "auto_reply": True,
            "reply_delay": 2,  # 秒
            "language": "zh-CN",
            "quick_replies": [
                "好的，我明白了",
                "这是一个很好的问题",
                "让我们一起来看看",
                "请稍等，我马上回答",
                "有其他同学有类似的疑问吗？"
            ],
            "prompt_templates": {
                "professional": "你是一位专业的教师，请用专业、清晰的语言回答学生的问题。",
                "friendly": "你是一位亲切友好的教师，请用温和、鼓励的语言回答学生的问题。",
                "humorous": "你是一位幽默风趣的教师，请用轻松、有趣的语言回答学生的问题，但要确保内容准确。"
            },
            "keywords_to_watch": [],
            "student_list": [],
            "course_topic": "",
            "notification_settings": {
                "sound_enabled": True,
                "desktop_notification": True,
                "urgent_only": False
            },
            "ui_settings": {
                "theme": "light",  # light, dark, auto
                "font_size": "medium",  # small, medium, large
                "show_timestamps": True,
                "show_token_count": True
            }
        }
    
    def _save_settings(self) -> None:
        """保存设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def get(self, key: str, default=None):
        """获取设置值"""
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value) -> None:
        """设置值"""
        keys = key.split('.')
        target = self.settings
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
        self._save_settings()
    
    def get_all(self) -> Dict:
        """获取所有设置"""
        return self.settings.copy()
    
    def reset(self) -> None:
        """重置为默认设置"""
        if self.settings_file.exists():
            self.settings_file.unlink()
        self.settings = self._load_settings()
        self._save_settings()
    
    # 快捷回复相关
    def add_quick_reply(self, text: str) -> None:
        """添加快捷回复"""
        if "quick_replies" not in self.settings:
            self.settings["quick_replies"] = []
        
        if text not in self.settings["quick_replies"]:
            self.settings["quick_replies"].append(text)
            self._save_settings()
    
    def remove_quick_reply(self, text: str) -> None:
        """移除快捷回复"""
        if "quick_replies" in self.settings and text in self.settings["quick_replies"]:
            self.settings["quick_replies"].remove(text)
            self._save_settings()
    
    def get_quick_replies(self) -> List[str]:
        """获取所有快捷回复"""
        return self.settings.get("quick_replies", [])
    
    # 学生名单相关
    def add_student(self, name: str, info: Optional[Dict] = None) -> None:
        """添加学生"""
        if "student_list" not in self.settings:
            self.settings["student_list"] = []
        
        student = {
            "name": name,
            "added_at": datetime.now().isoformat(),
            "info": info or {}
        }
        
        # 检查是否已存在
        for s in self.settings["student_list"]:
            if s["name"] == name:
                s["info"].update(info or {})
                self._save_settings()
                return
        
        self.settings["student_list"].append(student)
        self._save_settings()
    
    def remove_student(self, name: str) -> None:
        """移除学生"""
        if "student_list" in self.settings:
            self.settings["student_list"] = [
                s for s in self.settings["student_list"] if s["name"] != name
            ]
            self._save_settings()
    
    def get_students(self) -> List[Dict]:
        """获取学生列表"""
        return self.settings.get("student_list", [])
    
    # Prompt 模板相关
    def get_current_prompt(self) -> str:
        """获取当前的 Prompt 模板"""
        style = self.settings.get("reply_style", "professional")
        templates = self.settings.get("prompt_templates", {})
        return templates.get(style, templates.get("professional", ""))
    
    def set_custom_prompt(self, style: str, prompt: str) -> None:
        """设置自定义 Prompt"""
        if "prompt_templates" not in self.settings:
            self.settings["prompt_templates"] = {}
        
        self.settings["prompt_templates"][style] = prompt
        self._save_settings()
    
    # 关键词相关
    def add_keyword(self, keyword: str) -> None:
        """添加关注关键词"""
        if "keywords_to_watch" not in self.settings:
            self.settings["keywords_to_watch"] = []
        
        if keyword not in self.settings["keywords_to_watch"]:
            self.settings["keywords_to_watch"].append(keyword)
            self._save_settings()
    
    def remove_keyword(self, keyword: str) -> None:
        """移除关键词"""
        if "keywords_to_watch" in self.settings and keyword in self.settings["keywords_to_watch"]:
            self.settings["keywords_to_watch"].remove(keyword)
            self._save_settings()
    
    def get_keywords(self) -> List[str]:
        """获取所有关键词"""
        return self.settings.get("keywords_to_watch", [])


# 全局实例
settings_manager = SettingsManager()

