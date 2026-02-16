"""
课堂统计和历史记录模块
记录每次课堂的详细数据，支持历史查询和对比
"""
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from backend.core.conversation import ConversationHistory
from backend.core.analyzer import ConversationAnalyzer


class ClassSession:
    """课堂会话"""
    
    def __init__(self, session_id: str, topic: str = ""):
        """
        初始化课堂会话
        
        Args:
            session_id: 会话ID
            topic: 课堂主题
        """
        self.session_id = session_id
        self.topic = topic
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.conversation_count = 0
        self.teacher_count = 0
        self.student_count = 0
        self.question_count = 0
        self.total_tokens = 0
        self.keywords: Dict[str, int] = {}
        self.quality_score = 0
        self.notes = ""
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "topic": self.topic,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_minutes": self.get_duration_minutes(),
            "conversation_count": self.conversation_count,
            "teacher_count": self.teacher_count,
            "student_count": self.student_count,
            "question_count": self.question_count,
            "total_tokens": self.total_tokens,
            "keywords": self.keywords,
            "quality_score": self.quality_score,
            "notes": self.notes
        }
    
    def get_duration_minutes(self) -> float:
        """获取持续时间（分钟）"""
        end = self.end_time or datetime.now()
        duration = (end - self.start_time).total_seconds() / 60
        return round(duration, 2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ClassSession':
        """从字典创建"""
        session = cls(data["session_id"], data.get("topic", ""))
        session.start_time = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            session.end_time = datetime.fromisoformat(data["end_time"])
        session.conversation_count = data.get("conversation_count", 0)
        session.teacher_count = data.get("teacher_count", 0)
        session.student_count = data.get("student_count", 0)
        session.question_count = data.get("question_count", 0)
        session.total_tokens = data.get("total_tokens", 0)
        session.keywords = data.get("keywords", {})
        session.quality_score = data.get("quality_score", 0)
        session.notes = data.get("notes", "")
        return session


class SessionHistory:
    """课堂历史记录管理"""
    
    def __init__(self, history_file: str = "session_history.json"):
        """
        初始化历史记录管理器
        
        Args:
            history_file: 历史记录文件路径
        """
        self.history_file = Path(history_file)
        self.sessions: List[ClassSession] = []
        self.current_session: Optional[ClassSession] = None
        self._load_history()
    
    def _load_history(self) -> None:
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = [ClassSession.from_dict(s) for s in data]
            except Exception as e:
                print(f"加载历史记录失败: {e}")
    
    def _save_history(self) -> None:
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                data = [s.to_dict() for s in self.sessions]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def start_session(self, topic: str = "") -> ClassSession:
        """开始新的课堂会话"""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session = ClassSession(session_id, topic)
        return self.current_session
    
    def end_session(self, conversation_history: ConversationHistory) -> None:
        """结束当前课堂会话"""
        if not self.current_session:
            return
        
        # 更新会话数据
        self.current_session.end_time = datetime.now()
        
        # 分析对话数据
        analyzer = ConversationAnalyzer(conversation_history)
        
        # 参与度
        participation = analyzer.analyze_participation()
        self.current_session.teacher_count = participation["teacher_turns"]
        self.current_session.student_count = participation["student_turns"]
        self.current_session.conversation_count = participation["teacher_turns"] + participation["student_turns"]
        self.current_session.total_tokens = participation["teacher_tokens"] + participation["student_tokens"]
        
        # 提问
        questions = analyzer.analyze_questions()
        self.current_session.question_count = questions["total_questions"]
        
        # 关键词
        keywords = analyzer.analyze_keywords(10)
        self.current_session.keywords = {word: count for word, count in keywords}
        
        # 质量评分（简化版）
        quality = analyzer.analyze_interaction_quality()
        score = 0
        if participation["student_percentage"] > 30:
            score += 25
        if questions["total_questions"] > 3:
            score += 25
        if quality["avg_response_time"] < 10:
            score += 25
        if quality["interaction_rate"] > 2:
            score += 25
        self.current_session.quality_score = score
        
        # 保存到历史
        self.sessions.append(self.current_session)
        self._save_history()
        
        self.current_session = None
    
    def get_session(self, session_id: str) -> Optional[ClassSession]:
        """获取指定会话"""
        for session in self.sessions:
            if session.session_id == session_id:
                return session
        return None
    
    def get_recent_sessions(self, days: int = 7) -> List[ClassSession]:
        """获取最近N天的会话"""
        cutoff = datetime.now() - timedelta(days=days)
        return [s for s in self.sessions if s.start_time >= cutoff]
    
    def get_all_sessions(self) -> List[ClassSession]:
        """获取所有会话"""
        return self.sessions.copy()
    
    def get_statistics(self, days: int = 30) -> Dict:
        """获取统计数据"""
        sessions = self.get_recent_sessions(days)
        
        if not sessions:
            return {
                "total_sessions": 0,
                "total_duration": 0,
                "avg_duration": 0,
                "total_conversations": 0,
                "avg_conversations": 0,
                "total_questions": 0,
                "avg_questions": 0,
                "avg_quality_score": 0
            }
        
        total_duration = sum(s.get_duration_minutes() for s in sessions)
        total_conversations = sum(s.conversation_count for s in sessions)
        total_questions = sum(s.question_count for s in sessions)
        total_quality = sum(s.quality_score for s in sessions)
        
        return {
            "total_sessions": len(sessions),
            "total_duration": round(total_duration, 2),
            "avg_duration": round(total_duration / len(sessions), 2),
            "total_conversations": total_conversations,
            "avg_conversations": round(total_conversations / len(sessions), 2),
            "total_questions": total_questions,
            "avg_questions": round(total_questions / len(sessions), 2),
            "avg_quality_score": round(total_quality / len(sessions), 2)
        }
    
    def compare_sessions(self, session_id1: str, session_id2: str) -> Dict:
        """对比两个会话"""
        s1 = self.get_session(session_id1)
        s2 = self.get_session(session_id2)
        
        if not s1 or not s2:
            return {}
        
        return {
            "session1": s1.to_dict(),
            "session2": s2.to_dict(),
            "comparison": {
                "duration_diff": s2.get_duration_minutes() - s1.get_duration_minutes(),
                "conversation_diff": s2.conversation_count - s1.conversation_count,
                "question_diff": s2.question_count - s1.question_count,
                "quality_diff": s2.quality_score - s1.quality_score
            }
        }
    
    def add_note(self, session_id: str, note: str) -> None:
        """为会话添加备注"""
        session = self.get_session(session_id)
        if session:
            session.notes = note
            self._save_history()


# 全局实例
session_history = SessionHistory()

