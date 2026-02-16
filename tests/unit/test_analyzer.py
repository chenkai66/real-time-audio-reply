"""
测试智能分析模块
"""
import pytest
from datetime import datetime, timedelta
from backend.core.analyzer import ConversationAnalyzer, SmartReminder
from backend.core.conversation import ConversationHistory
from backend.core.role import Role


@pytest.fixture
def history_with_data():
    """创建带数据的对话历史"""
    history = ConversationHistory()
    history.add_turn(Role.TEACHER, "今天我们学习 Python 编程")
    history.add_turn(Role.STUDENT, "什么是 Python？")
    history.add_turn(Role.TEACHER, "Python 是一种编程语言")
    history.add_turn(Role.STUDENT, "如何学习 Python 编程？")
    history.add_turn(Role.TEACHER, "可以从基础语法开始学习")
    return history


class TestConversationAnalyzer:
    """测试 ConversationAnalyzer 类"""
    
    def test_init(self, history_with_data):
        """测试初始化"""
        analyzer = ConversationAnalyzer(history_with_data)
        assert analyzer.history == history_with_data
    
    def test_analyze_participation(self, history_with_data):
        """测试参与度分析"""
        analyzer = ConversationAnalyzer(history_with_data)
        result = analyzer.analyze_participation()
        
        assert result["teacher_turns"] == 3
        assert result["student_turns"] == 2
        assert result["teacher_percentage"] == 60.0
        assert result["student_percentage"] == 40.0
        assert result["teacher_tokens"] > 0
        assert result["student_tokens"] > 0
    
    def test_analyze_questions(self, history_with_data):
        """测试提问分析"""
        analyzer = ConversationAnalyzer(history_with_data)
        result = analyzer.analyze_questions()
        
        assert result["total_questions"] == 2
        assert len(result["questions"]) == 2
        assert result["avg_question_length"] > 0
    
    def test_analyze_keywords(self, history_with_data):
        """测试关键词分析"""
        analyzer = ConversationAnalyzer(history_with_data)
        keywords = analyzer.analyze_keywords(top_n=5)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        
        # 检查格式
        for word, count in keywords:
            assert isinstance(word, str)
            assert isinstance(count, int)
            assert count > 0
    
    def test_analyze_interaction_quality(self, history_with_data):
        """测试互动质量分析"""
        analyzer = ConversationAnalyzer(history_with_data)
        result = analyzer.analyze_interaction_quality()
        
        assert "avg_response_time" in result
        assert "interaction_rate" in result
        assert "total_interactions" in result
        assert result["total_interactions"] == 5
    
    def test_generate_summary_report(self, history_with_data):
        """测试生成总结报告"""
        analyzer = ConversationAnalyzer(history_with_data)
        report = analyzer.generate_summary_report()
        
        assert isinstance(report, str)
        assert "课堂互动分析报告" in report
        assert "参与度分析" in report
        assert "提问分析" in report
        assert "高频关键词" in report
        assert "互动质量" in report
        assert "综合评价" in report


class TestSmartReminder:
    """测试 SmartReminder 类"""
    
    def test_init(self):
        """测试初始化"""
        reminder = SmartReminder()
        assert len(reminder.keywords) == 0
        assert len(reminder.unanswered_questions) == 0
    
    def test_add_keyword(self):
        """测试添加关键词"""
        reminder = SmartReminder()
        reminder.add_keyword("Python")
        
        assert "python" in reminder.keywords
    
    def test_remove_keyword(self):
        """测试移除关键词"""
        reminder = SmartReminder()
        reminder.add_keyword("Python")
        reminder.remove_keyword("Python")
        
        assert "python" not in reminder.keywords
    
    def test_check_keywords_match(self):
        """测试检查关键词（匹配）"""
        reminder = SmartReminder()
        reminder.add_keyword("Python")
        reminder.add_keyword("编程")
        
        matched = reminder.check_keywords("我想学习 Python 编程")
        
        assert len(matched) == 2
        assert "python" in matched
        assert "编程" in matched
    
    def test_check_keywords_no_match(self):
        """测试检查关键词（无匹配）"""
        reminder = SmartReminder()
        reminder.add_keyword("Python")
        
        matched = reminder.check_keywords("我想学习 Java")
        
        assert len(matched) == 0
    
    def test_add_unanswered_question(self):
        """测试添加未回答问题"""
        reminder = SmartReminder()
        reminder.add_unanswered_question("什么是 Python？", datetime.now())
        
        assert len(reminder.unanswered_questions) == 1
        assert reminder.unanswered_questions[0]["question"] == "什么是 Python？"
    
    def test_mark_as_answered(self):
        """测试标记为已回答"""
        reminder = SmartReminder()
        reminder.add_unanswered_question("问题1", datetime.now())
        reminder.add_unanswered_question("问题2", datetime.now())
        
        reminder.mark_as_answered(0)
        
        assert len(reminder.unanswered_questions) == 1
        assert reminder.unanswered_questions[0]["question"] == "问题2"
    
    def test_get_unanswered_questions(self):
        """测试获取未回答问题"""
        reminder = SmartReminder()
        reminder.add_unanswered_question("问题1", datetime.now())
        reminder.add_unanswered_question("问题2", datetime.now())
        
        questions = reminder.get_unanswered_questions()
        
        assert len(questions) == 2
        assert isinstance(questions, list)
    
    def test_check_urgent_question_true(self):
        """测试检查紧急问题（是）"""
        reminder = SmartReminder()
        
        assert reminder.check_urgent_question("紧急！我不懂这个问题") is True
        assert reminder.check_urgent_question("急，需要帮助") is True
        assert reminder.check_urgent_question("我不会做") is True
    
    def test_check_urgent_question_false(self):
        """测试检查紧急问题（否）"""
        reminder = SmartReminder()
        
        assert reminder.check_urgent_question("什么是 Python？") is False
        assert reminder.check_urgent_question("请问如何学习") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

