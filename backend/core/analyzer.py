"""
智能分析模块
提供课堂质量分析、学生参与度统计等功能
"""
from typing import Dict, List, Tuple
from collections import Counter
from datetime import datetime, timedelta
from backend.core.conversation import ConversationHistory
from backend.core.role import Role
from backend.utils.token import token_counter


class ConversationAnalyzer:
    """对话分析器"""
    
    def __init__(self, history: ConversationHistory):
        """
        初始化分析器
        
        Args:
            history: 对话历史实例
        """
        self.history = history
    
    def analyze_participation(self) -> Dict:
        """
        分析参与度
        
        Returns:
            参与度分析结果
        """
        teacher_count = 0
        student_count = 0
        teacher_tokens = 0
        student_tokens = 0
        
        for turn in self.history.l1_cache:
            if turn.role == Role.TEACHER:
                teacher_count += 1
                teacher_tokens += turn.tokens
            elif turn.role == Role.STUDENT:
                student_count += 1
                student_tokens += turn.tokens
        
        total_count = teacher_count + student_count
        
        return {
            "teacher_turns": teacher_count,
            "student_turns": student_count,
            "teacher_percentage": teacher_count / total_count * 100 if total_count > 0 else 0,
            "student_percentage": student_count / total_count * 100 if total_count > 0 else 0,
            "teacher_tokens": teacher_tokens,
            "student_tokens": student_tokens,
            "avg_teacher_tokens": teacher_tokens / teacher_count if teacher_count > 0 else 0,
            "avg_student_tokens": student_tokens / student_count if student_count > 0 else 0,
        }
    
    def analyze_questions(self) -> Dict:
        """
        分析学生提问
        
        Returns:
            提问分析结果
        """
        questions = []
        question_keywords = ["什么", "为什么", "如何", "怎么", "哪", "吗", "呢", "?", "？"]
        
        for turn in self.history.l1_cache:
            if turn.role == Role.STUDENT:
                # 判断是否为问题
                is_question = any(keyword in turn.text for keyword in question_keywords)
                if is_question:
                    questions.append({
                        "text": turn.text,
                        "timestamp": turn.timestamp,
                        "tokens": turn.tokens
                    })
        
        return {
            "total_questions": len(questions),
            "questions": questions,
            "avg_question_length": sum(q["tokens"] for q in questions) / len(questions) if questions else 0,
        }
    
    def analyze_keywords(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        分析高频关键词
        
        Args:
            top_n: 返回前 N 个关键词
            
        Returns:
            关键词列表 [(词, 频率)]
        """
        # 简单的分词（按空格和标点分割）
        words = []
        
        for turn in self.history.l1_cache:
            # 移除标点符号
            text = turn.text
            for punct in "，。！？、；：""''（）【】《》":
                text = text.replace(punct, " ")
            
            # 分词
            tokens = text.split()
            
            # 过滤停用词和短词
            stop_words = {"的", "了", "是", "在", "我", "你", "他", "她", "它", "们", "这", "那", "有", "和", "与"}
            words.extend([w for w in tokens if len(w) > 1 and w not in stop_words])
        
        # 统计频率
        counter = Counter(words)
        return counter.most_common(top_n)
    
    def analyze_interaction_quality(self) -> Dict:
        """
        分析互动质量
        
        Returns:
            互动质量分析
        """
        # 计算平均响应时间
        response_times = []
        
        for i in range(len(self.history.l1_cache) - 1):
            current = self.history.l1_cache[i]
            next_turn = self.history.l1_cache[i + 1]
            
            # 如果是学生提问后教师回复
            if current.role == Role.STUDENT and next_turn.role == Role.TEACHER:
                time_diff = (next_turn.timestamp - current.timestamp).total_seconds()
                response_times.append(time_diff)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # 计算互动频率
        if self.history.l1_cache:
            first_time = self.history.l1_cache[0].timestamp
            last_time = self.history.l1_cache[-1].timestamp
            duration = (last_time - first_time).total_seconds() / 60  # 分钟
            interaction_rate = len(self.history.l1_cache) / duration if duration > 0 else 0
        else:
            interaction_rate = 0
        
        return {
            "avg_response_time": avg_response_time,
            "interaction_rate": interaction_rate,  # 每分钟互动次数
            "total_interactions": len(self.history.l1_cache),
        }
    
    def generate_summary_report(self) -> str:
        """
        生成课堂总结报告
        
        Returns:
            总结报告文本
        """
        participation = self.analyze_participation()
        questions = self.analyze_questions()
        keywords = self.analyze_keywords(5)
        quality = self.analyze_interaction_quality()
        
        lines = []
        lines.append("=" * 60)
        lines.append("课堂互动分析报告")
        lines.append("=" * 60)
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        lines.append("【参与度分析】")
        lines.append(f"  教师发言: {participation['teacher_turns']} 次 ({participation['teacher_percentage']:.1f}%)")
        lines.append(f"  学生发言: {participation['student_turns']} 次 ({participation['student_percentage']:.1f}%)")
        lines.append(f"  教师平均发言长度: {participation['avg_teacher_tokens']:.0f} tokens")
        lines.append(f"  学生平均发言长度: {participation['avg_student_tokens']:.0f} tokens")
        lines.append("")
        
        lines.append("【提问分析】")
        lines.append(f"  学生提问总数: {questions['total_questions']} 个")
        lines.append(f"  平均问题长度: {questions['avg_question_length']:.0f} tokens")
        lines.append("")
        
        lines.append("【高频关键词】")
        for word, count in keywords:
            lines.append(f"  {word}: {count} 次")
        lines.append("")
        
        lines.append("【互动质量】")
        lines.append(f"  平均响应时间: {quality['avg_response_time']:.1f} 秒")
        lines.append(f"  互动频率: {quality['interaction_rate']:.1f} 次/分钟")
        lines.append(f"  总互动次数: {quality['total_interactions']} 次")
        lines.append("")
        
        lines.append("【综合评价】")
        # 简单的评分逻辑
        score = 0
        if participation['student_percentage'] > 30:
            score += 25
            lines.append("  ✓ 学生参与度良好")
        else:
            lines.append("  ✗ 学生参与度偏低，建议增加互动")
        
        if questions['total_questions'] > 3:
            score += 25
            lines.append("  ✓ 学生提问积极")
        else:
            lines.append("  ✗ 学生提问较少，建议鼓励提问")
        
        if quality['avg_response_time'] < 10:
            score += 25
            lines.append("  ✓ 响应及时")
        else:
            lines.append("  ✗ 响应时间较长，建议提高响应速度")
        
        if quality['interaction_rate'] > 2:
            score += 25
            lines.append("  ✓ 互动频率适中")
        else:
            lines.append("  ✗ 互动频率偏低，建议增加互动")
        
        lines.append("")
        lines.append(f"【总体评分】{score}/100")
        
        if score >= 80:
            lines.append("  评级: 优秀 ⭐⭐⭐⭐⭐")
        elif score >= 60:
            lines.append("  评级: 良好 ⭐⭐⭐⭐")
        elif score >= 40:
            lines.append("  评级: 及格 ⭐⭐⭐")
        else:
            lines.append("  评级: 需改进 ⭐⭐")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


class SmartReminder:
    """智能提醒器"""
    
    def __init__(self):
        """初始化提醒器"""
        self.keywords = set()  # 关键词集合
        self.unanswered_questions = []  # 未回答的问题
    
    def add_keyword(self, keyword: str) -> None:
        """添加关键词"""
        self.keywords.add(keyword.lower())
    
    def remove_keyword(self, keyword: str) -> None:
        """移除关键词"""
        self.keywords.discard(keyword.lower())
    
    def check_keywords(self, text: str) -> List[str]:
        """
        检查文本中是否包含关键词
        
        Args:
            text: 要检查的文本
            
        Returns:
            匹配的关键词列表
        """
        text_lower = text.lower()
        matched = []
        
        for keyword in self.keywords:
            if keyword in text_lower:
                matched.append(keyword)
        
        return matched
    
    def add_unanswered_question(self, question: str, timestamp: datetime) -> None:
        """添加未回答的问题"""
        self.unanswered_questions.append({
            "question": question,
            "timestamp": timestamp
        })
    
    def mark_as_answered(self, index: int) -> None:
        """标记问题为已回答"""
        if 0 <= index < len(self.unanswered_questions):
            self.unanswered_questions.pop(index)
    
    def get_unanswered_questions(self) -> List[Dict]:
        """获取所有未回答的问题"""
        return self.unanswered_questions.copy()
    
    def check_urgent_question(self, text: str) -> bool:
        """
        检查是否为紧急问题
        
        Args:
            text: 问题文本
            
        Returns:
            是否紧急
        """
        urgent_keywords = ["紧急", "急", "不懂", "不会", "错误", "问题", "帮助", "救命"]
        text_lower = text.lower()
        
        return any(keyword in text_lower for keyword in urgent_keywords)


# 全局实例
smart_reminder = SmartReminder()

