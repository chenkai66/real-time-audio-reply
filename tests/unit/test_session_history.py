"""
测试课堂会话历史模块
"""
import pytest
from datetime import datetime, timedelta
from backend.core.session_history import ClassSession, SessionHistory
from backend.core.conversation import ConversationHistory
from backend.core.role import Role


@pytest.fixture
def temp_history_file(tmp_path):
    """创建临时历史文件"""
    return tmp_path / "test_history.json"


@pytest.fixture
def history(temp_history_file):
    """创建会话历史实例"""
    return SessionHistory(str(temp_history_file))


@pytest.fixture
def conversation_with_data():
    """创建带数据的对话历史"""
    conv = ConversationHistory()
    conv.add_turn(Role.TEACHER, "今天我们学习 Python")
    conv.add_turn(Role.STUDENT, "什么是 Python？")
    conv.add_turn(Role.TEACHER, "Python 是一种编程语言")
    conv.add_turn(Role.STUDENT, "如何学习 Python？")
    conv.add_turn(Role.TEACHER, "可以从基础语法开始")
    return conv


class TestClassSession:
    """测试 ClassSession 类"""
    
    def test_init(self):
        """测试初始化"""
        session = ClassSession("test_001", "Python 基础")
        assert session.session_id == "test_001"
        assert session.topic == "Python 基础"
        assert session.conversation_count == 0
    
    def test_to_dict(self):
        """测试转换为字典"""
        session = ClassSession("test_001", "Python 基础")
        data = session.to_dict()
        
        assert data["session_id"] == "test_001"
        assert data["topic"] == "Python 基础"
        assert "start_time" in data
        assert "duration_minutes" in data
    
    def test_get_duration_minutes(self):
        """测试获取持续时间"""
        session = ClassSession("test_001")
        session.start_time = datetime.now() - timedelta(minutes=30)
        session.end_time = datetime.now()
        
        duration = session.get_duration_minutes()
        assert 29 <= duration <= 31  # 允许小误差
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "session_id": "test_001",
            "topic": "Python 基础",
            "start_time": datetime.now().isoformat(),
            "conversation_count": 10,
            "teacher_count": 6,
            "student_count": 4,
            "quality_score": 75
        }
        
        session = ClassSession.from_dict(data)
        assert session.session_id == "test_001"
        assert session.topic == "Python 基础"
        assert session.conversation_count == 10
        assert session.quality_score == 75


class TestSessionHistory:
    """测试 SessionHistory 类"""
    
    def test_init(self, history):
        """测试初始化"""
        assert isinstance(history.sessions, list)
        assert history.current_session is None
    
    def test_start_session(self, history):
        """测试开始会话"""
        session = history.start_session("Python 基础")
        
        assert session is not None
        assert history.current_session == session
        assert session.topic == "Python 基础"
    
    def test_end_session(self, history, conversation_with_data):
        """测试结束会话"""
        history.start_session("Python 基础")
        history.end_session(conversation_with_data)
        
        assert history.current_session is None
        assert len(history.sessions) == 1
        
        session = history.sessions[0]
        assert session.end_time is not None
        assert session.conversation_count > 0
    
    def test_get_session(self, history, conversation_with_data):
        """测试获取指定会话"""
        history.start_session("Python 基础")
        session_id = history.current_session.session_id
        history.end_session(conversation_with_data)
        
        retrieved = history.get_session(session_id)
        assert retrieved is not None
        assert retrieved.session_id == session_id
    
    def test_get_nonexistent_session(self, history):
        """测试获取不存在的会话"""
        session = history.get_session("nonexistent")
        assert session is None
    
    def test_get_recent_sessions(self, history, conversation_with_data):
        """测试获取最近会话"""
        # 创建多个会话
        for i in range(3):
            history.start_session(f"课程 {i}")
            history.end_session(conversation_with_data)
        
        recent = history.get_recent_sessions(days=7)
        assert len(recent) == 3
    
    def test_get_all_sessions(self, history, conversation_with_data):
        """测试获取所有会话"""
        for i in range(3):
            history.start_session(f"课程 {i}")
            history.end_session(conversation_with_data)
        
        all_sessions = history.get_all_sessions()
        assert len(all_sessions) == 3
    
    def test_get_statistics(self, history, conversation_with_data):
        """测试获取统计数据"""
        # 创建会话
        history.start_session("Python 基础")
        # 添加一点延迟确保有持续时间
        import time
        time.sleep(0.1)
        history.end_session(conversation_with_data)
        
        stats = history.get_statistics(days=30)
        
        assert stats["total_sessions"] == 1
        assert stats["total_duration"] >= 0  # 允许为0或更大
        assert stats["avg_duration"] >= 0
        assert stats["total_conversations"] > 0
    
    def test_get_statistics_empty(self, history):
        """测试空统计数据"""
        stats = history.get_statistics(days=30)
        
        assert stats["total_sessions"] == 0
        assert stats["total_duration"] == 0
    
    def test_compare_sessions(self, history, conversation_with_data):
        """测试对比会话"""
        # 创建两个会话
        history.start_session("课程 1")
        session_id1 = history.current_session.session_id
        history.end_session(conversation_with_data)
        
        history.start_session("课程 2")
        session_id2 = history.current_session.session_id
        history.end_session(conversation_with_data)
        
        comparison = history.compare_sessions(session_id1, session_id2)
        
        assert "session1" in comparison
        assert "session2" in comparison
        assert "comparison" in comparison
        assert "duration_diff" in comparison["comparison"]
    
    def test_compare_nonexistent_sessions(self, history):
        """测试对比不存在的会话"""
        comparison = history.compare_sessions("id1", "id2")
        assert comparison == {}
    
    def test_add_note(self, history, conversation_with_data):
        """测试添加备注"""
        history.start_session("Python 基础")
        session_id = history.current_session.session_id
        history.end_session(conversation_with_data)
        
        history.add_note(session_id, "这是一堂很好的课")
        
        session = history.get_session(session_id)
        assert session.notes == "这是一堂很好的课"
    
    def test_persistence(self, temp_history_file, conversation_with_data):
        """测试持久化"""
        # 创建第一个实例并添加会话
        history1 = SessionHistory(str(temp_history_file))
        history1.start_session("Python 基础")
        history1.end_session(conversation_with_data)
        
        # 创建第二个实例，应该加载保存的数据
        history2 = SessionHistory(str(temp_history_file))
        assert len(history2.sessions) == 1
        assert history2.sessions[0].topic == "Python 基础"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

