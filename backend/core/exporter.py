"""
对话导出模块
支持多种格式导出对话历史
"""
import json
from typing import List, Dict
from datetime import datetime
from backend.core.conversation import ConversationHistory, ConversationTurn
from backend.core.role import Role


class ConversationExporter:
    """对话导出器"""
    
    def __init__(self, history: ConversationHistory):
        """
        初始化导出器
        
        Args:
            history: 对话历史实例
        """
        self.history = history
    
    def export_to_json(self, include_stats: bool = True) -> str:
        """
        导出为 JSON 格式
        
        Args:
            include_stats: 是否包含统计信息
            
        Returns:
            JSON 字符串
        """
        data = {
            "export_time": datetime.now().isoformat(),
            "conversations": [turn.to_dict() for turn in self.history.l1_cache],
            "summaries": [summary.to_dict() for summary in self.history.l2_cache],
        }
        
        if include_stats:
            data["stats"] = self.history.get_stats()
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def export_to_txt(self, include_timestamp: bool = True) -> str:
        """
        导出为纯文本格式
        
        Args:
            include_timestamp: 是否包含时间戳
            
        Returns:
            文本字符串
        """
        lines = []
        lines.append("=" * 60)
        lines.append("对话记录")
        lines.append(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        lines.append("")
        
        for turn in self.history.l1_cache:
            role_name = self._get_role_name(turn.role)
            
            if include_timestamp:
                time_str = turn.timestamp.strftime('%H:%M:%S')
                lines.append(f"[{time_str}] {role_name}:")
            else:
                lines.append(f"{role_name}:")
            
            lines.append(f"  {turn.text}")
            lines.append("")
        
        # 添加统计信息
        stats = self.history.get_stats()
        lines.append("=" * 60)
        lines.append("统计信息")
        lines.append("=" * 60)
        lines.append(f"总对话轮数: {stats['total_turns']}")
        lines.append(f"总 Token 数: {stats['total_tokens']}")
        lines.append(f"L1 缓存: {stats['l1_size']} 轮")
        lines.append(f"L2 缓存: {stats['l2_size']} 轮")
        
        return "\n".join(lines)
    
    def export_to_markdown(self) -> str:
        """
        导出为 Markdown 格式
        
        Returns:
            Markdown 字符串
        """
        lines = []
        lines.append("# 对话记录")
        lines.append("")
        lines.append(f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        for turn in self.history.l1_cache:
            role_name = self._get_role_name(turn.role)
            time_str = turn.timestamp.strftime('%H:%M:%S')
            
            lines.append(f"### {role_name} `{time_str}`")
            lines.append("")
            lines.append(turn.text)
            lines.append("")
        
        # 添加统计信息
        stats = self.history.get_stats()
        lines.append("---")
        lines.append("")
        lines.append("## 统计信息")
        lines.append("")
        lines.append(f"- **总对话轮数**: {stats['total_turns']}")
        lines.append(f"- **总 Token 数**: {stats['total_tokens']}")
        lines.append(f"- **L1 缓存**: {stats['l1_size']} 轮 ({stats['l1_tokens']} tokens)")
        lines.append(f"- **L2 缓存**: {stats['l2_size']} 轮 ({stats['l2_tokens']} tokens)")
        
        return "\n".join(lines)
    
    def export_to_html(self) -> str:
        """
        导出为 HTML 格式
        
        Returns:
            HTML 字符串
        """
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html lang='zh-CN'>")
        html.append("<head>")
        html.append("  <meta charset='UTF-8'>")
        html.append("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html.append("  <title>对话记录</title>")
        html.append("  <style>")
        html.append("    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }")
        html.append("    .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }")
        html.append("    .conversation { background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }")
        html.append("    .teacher { border-left: 4px solid #3498db; }")
        html.append("    .student { border-left: 4px solid #9b59b6; }")
        html.append("    .system { border-left: 4px solid #95a5a6; }")
        html.append("    .role { font-weight: bold; color: #2c3e50; margin-bottom: 5px; }")
        html.append("    .time { color: #7f8c8d; font-size: 0.9em; }")
        html.append("    .text { color: #34495e; line-height: 1.6; }")
        html.append("    .stats { background: white; padding: 20px; border-radius: 8px; margin-top: 20px; }")
        html.append("    .stats h2 { color: #2c3e50; margin-top: 0; }")
        html.append("    .stat-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #ecf0f1; }")
        html.append("  </style>")
        html.append("</head>")
        html.append("<body>")
        
        # 头部
        html.append("  <div class='header'>")
        html.append("    <h1>对话记录</h1>")
        html.append(f"    <p>导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        html.append("  </div>")
        
        # 对话内容
        for turn in self.history.l1_cache:
            role_name = self._get_role_name(turn.role)
            role_class = turn.role.value
            time_str = turn.timestamp.strftime('%H:%M:%S')
            
            html.append(f"  <div class='conversation {role_class}'>")
            html.append(f"    <div class='role'>{role_name} <span class='time'>{time_str}</span></div>")
            html.append(f"    <div class='text'>{turn.text}</div>")
            html.append("  </div>")
        
        # 统计信息
        stats = self.history.get_stats()
        html.append("  <div class='stats'>")
        html.append("    <h2>统计信息</h2>")
        html.append(f"    <div class='stat-item'><span>总对话轮数</span><span>{stats['total_turns']}</span></div>")
        html.append(f"    <div class='stat-item'><span>总 Token 数</span><span>{stats['total_tokens']}</span></div>")
        html.append(f"    <div class='stat-item'><span>L1 缓存</span><span>{stats['l1_size']} 轮 ({stats['l1_tokens']} tokens)</span></div>")
        html.append(f"    <div class='stat-item'><span>L2 缓存</span><span>{stats['l2_size']} 轮 ({stats['l2_tokens']} tokens)</span></div>")
        html.append("  </div>")
        
        html.append("</body>")
        html.append("</html>")
        
        return "\n".join(html)
    
    def _get_role_name(self, role: Role) -> str:
        """获取角色名称"""
        role_names = {
            Role.TEACHER: "教师",
            Role.STUDENT: "学生",
            Role.UNKNOWN: "未知"
        }
        return role_names.get(role, "未知")
    
    def search_conversations(self, keyword: str, case_sensitive: bool = False) -> List[ConversationTurn]:
        """
        搜索对话
        
        Args:
            keyword: 搜索关键词
            case_sensitive: 是否区分大小写
            
        Returns:
            匹配的对话列表
        """
        results = []
        
        for turn in self.history.l1_cache:
            text = turn.text if case_sensitive else turn.text.lower()
            search_key = keyword if case_sensitive else keyword.lower()
            
            if search_key in text:
                results.append(turn)
        
        return results

