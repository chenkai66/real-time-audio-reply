"""
测试个性化设置管理模块
"""
import pytest
import json
from pathlib import Path
from backend.core.settings_manager import SettingsManager


@pytest.fixture
def temp_settings_file(tmp_path):
    """创建临时设置文件"""
    return tmp_path / "test_settings.json"


@pytest.fixture
def manager(temp_settings_file):
    """创建设置管理器实例"""
    return SettingsManager(str(temp_settings_file))


class TestSettingsManager:
    """测试 SettingsManager 类"""
    
    def test_init_with_defaults(self, manager):
        """测试初始化默认设置"""
        assert manager.get("teacher_name") == "老师"
        assert manager.get("reply_style") == "professional"
        assert manager.get("auto_reply") is True
        assert manager.get("language") == "zh-CN"
    
    def test_get_setting(self, manager):
        """测试获取设置"""
        assert manager.get("teacher_name") == "老师"
        assert manager.get("reply_delay") == 2
    
    def test_get_nested_setting(self, manager):
        """测试获取嵌套设置"""
        assert manager.get("notification_settings.sound_enabled") is True
        assert manager.get("ui_settings.theme") == "light"
    
    def test_get_nonexistent_setting(self, manager):
        """测试获取不存在的设置"""
        assert manager.get("nonexistent") is None
        assert manager.get("nonexistent", "default") == "default"
    
    def test_set_setting(self, manager):
        """测试设置值"""
        manager.set("teacher_name", "张老师")
        assert manager.get("teacher_name") == "张老师"
    
    def test_set_nested_setting(self, manager):
        """测试设置嵌套值"""
        manager.set("ui_settings.theme", "dark")
        assert manager.get("ui_settings.theme") == "dark"
    
    def test_get_all(self, manager):
        """测试获取所有设置"""
        all_settings = manager.get_all()
        assert isinstance(all_settings, dict)
        assert "teacher_name" in all_settings
        assert "reply_style" in all_settings
    
    def test_reset(self, manager):
        """测试重置设置"""
        manager.set("teacher_name", "张老师")
        manager.reset()
        assert manager.get("teacher_name") == "老师"
    
    def test_add_quick_reply(self, manager):
        """测试添加快捷回复"""
        manager.add_quick_reply("测试回复")
        replies = manager.get_quick_replies()
        assert "测试回复" in replies
    
    def test_add_duplicate_quick_reply(self, manager):
        """测试添加重复快捷回复"""
        manager.add_quick_reply("测试回复")
        manager.add_quick_reply("测试回复")
        replies = manager.get_quick_replies()
        assert replies.count("测试回复") == 1
    
    def test_remove_quick_reply(self, manager):
        """测试移除快捷回复"""
        manager.add_quick_reply("测试回复")
        manager.remove_quick_reply("测试回复")
        replies = manager.get_quick_replies()
        assert "测试回复" not in replies
    
    def test_get_quick_replies(self, manager):
        """测试获取快捷回复列表"""
        replies = manager.get_quick_replies()
        assert isinstance(replies, list)
        assert len(replies) > 0
    
    def test_add_student(self, manager):
        """测试添加学生"""
        manager.add_student("张三", {"grade": "高一"})
        students = manager.get_students()
        assert len(students) == 1
        assert students[0]["name"] == "张三"
        assert students[0]["info"]["grade"] == "高一"
    
    def test_add_duplicate_student(self, manager):
        """测试添加重复学生"""
        manager.add_student("张三", {"grade": "高一"})
        manager.add_student("张三", {"class": "1班"})
        students = manager.get_students()
        assert len(students) == 1
        assert students[0]["info"]["grade"] == "高一"
        assert students[0]["info"]["class"] == "1班"
    
    def test_remove_student(self, manager):
        """测试移除学生"""
        manager.add_student("张三")
        manager.remove_student("张三")
        students = manager.get_students()
        assert len(students) == 0
    
    def test_get_students(self, manager):
        """测试获取学生列表"""
        manager.add_student("张三")
        manager.add_student("李四")
        students = manager.get_students()
        assert len(students) == 2
    
    def test_get_current_prompt(self, manager):
        """测试获取当前 Prompt"""
        prompt = manager.get_current_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_get_current_prompt_different_styles(self, manager):
        """测试不同风格的 Prompt"""
        manager.set("reply_style", "friendly")
        prompt1 = manager.get_current_prompt()
        
        manager.set("reply_style", "humorous")
        prompt2 = manager.get_current_prompt()
        
        assert prompt1 != prompt2
    
    def test_set_custom_prompt(self, manager):
        """测试设置自定义 Prompt"""
        custom_prompt = "这是自定义的 Prompt"
        manager.set_custom_prompt("custom", custom_prompt)
        manager.set("reply_style", "custom")
        
        assert manager.get_current_prompt() == custom_prompt
    
    def test_add_keyword(self, manager):
        """测试添加关键词"""
        manager.add_keyword("重要")
        keywords = manager.get_keywords()
        assert "重要" in keywords
    
    def test_remove_keyword(self, manager):
        """测试移除关键词"""
        manager.add_keyword("重要")
        manager.remove_keyword("重要")
        keywords = manager.get_keywords()
        assert "重要" not in keywords
    
    def test_get_keywords(self, manager):
        """测试获取关键词列表"""
        manager.add_keyword("重要")
        manager.add_keyword("考试")
        keywords = manager.get_keywords()
        assert len(keywords) == 2
    
    def test_persistence(self, temp_settings_file):
        """测试设置持久化"""
        manager1 = SettingsManager(str(temp_settings_file))
        manager1.set("teacher_name", "张老师")
        manager1.add_quick_reply("测试")
        
        # 创建新实例，应该加载保存的设置
        manager2 = SettingsManager(str(temp_settings_file))
        assert manager2.get("teacher_name") == "张老师"
        assert "测试" in manager2.get_quick_replies()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

