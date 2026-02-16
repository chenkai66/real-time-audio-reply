"""
测试对话导出模块
"""
import pytest
import json
from datetime import datetime
from backend.core.exporter import ConversationExporter
from backend.core.conversation import ConversationHistory
from backend.core.role import Role


@pytest.fixture
def history_with_data():
    """创建带数据的对话历史"""
    history = ConversationHistory()
    history.add_turn(Role.TEACHER, "今天我们学习 Python")
    history.add_turn(Role.STUDENT, "什么是 Python？")
    history.add_turn(Role.TEACHER, "Python 是一种编程语言")
    history.add_turn(Role.STUDENT, "如何学习 Python？")
    return history


class TestConversationExporter:
    """测试 ConversationExporter 类"""
    
    def test_init(self, history_with_data):
        """测试初始化"""
        exporter = ConversationExporter(history_with_data)
        assert exporter.history == history_with_data
    
    def test_export_to_json(self, history_with_data):
        """测试导出为 JSON"""
        exporter = ConversationExporter(history_with_data)
        result = exporter.export_to_json()
        
        assert isinstance(result, str)
        data = json.loads(result)
        
        assert "export_time" in data
        assert "conversations" in data
        assert "stats" in data
        assert len(data["conversations"]) == 4
    
    def test_export_to_json_without_stats(self, history_with_data):
        """测试导出 JSON 不包含统计"""
        exporter = ConversationExporter(history_with_data)
        result = exporter.export_to_json(include_stats=False)
        
        data = json.loads(result)
        assert "stats" not in data
    
    def test_export_to_txt(self, history_with_data):
        """测试导出为文本"""
        exporter = ConversationExporter(history_with_data)
        result = exporter.export_to_txt()
        
        assert isinstance(result, str)
        assert "对话记录" in result
        assert "教师" in result
        assert "学生" in result
        assert "Python" in result
        assert "统计信息" in result
    
    def test_export_to_txt_without_timestamp(self, history_with_data):
        """测试导出文本不包含时间戳"""
        exporter = ConversationExporter(history_with_data)
        result = exporter.export_to_txt(include_timestamp=False)
        
        assert isinstance(result, str)
        assert "[" not in result  # 时间戳格式 [HH:MM:SS]
    
    def test_export_to_markdown(self, history_with_data):
        """测试导出为 Markdown"""
        exporter = ConversationExporter(history_with_data)
        result = exporter.export_to_markdown()
        
        assert isinstance(result, str)
        assert "# 对话记录" in result
        assert "### 教师" in result
        assert "### 学生" in result
        assert "## 统计信息" in result
    
    def test_export_to_html(self, history_with_data):
        """测试导出为 HTML"""
        exporter = ConversationExporter(history_with_data)
        result = exporter.export_to_html()
        
        assert isinstance(result, str)
        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "对话记录" in result
        assert "class='conversation teacher'" in result
        assert "class='conversation student'" in result
    
    def test_search_conversations(self, history_with_data):
        """测试搜索对话"""
        exporter = ConversationExporter(history_with_data)
        results = exporter.search_conversations("Python")
        
        assert len(results) == 4  # 4 条包含 Python 的对话
    
    def test_search_conversations_case_sensitive(self, history_with_data):
        """测试区分大小写搜索"""
        exporter = ConversationExporter(history_with_data)
        results = exporter.search_conversations("python", case_sensitive=True)
        
        assert len(results) == 0  # 没有小写的 python
    
    def test_search_conversations_no_match(self, history_with_data):
        """测试搜索无匹配"""
        exporter = ConversationExporter(history_with_data)
        results = exporter.search_conversations("Java")
        
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

