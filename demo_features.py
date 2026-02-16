"""
功能演示脚本
展示所有新增功能的使用方法
"""
import asyncio
import httpx
from datetime import datetime


BASE_URL = "http://localhost:8000"


async def demo_settings():
    """演示个性化设置功能"""
    print("\n" + "="*60)
    print("【1. 个性化设置功能演示】")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        # 获取所有设置
        print("\n1.1 获取当前设置")
        response = await client.get(f"{BASE_URL}/api/settings")
        print(f"状态码: {response.status_code}")
        settings = response.json()
        print(f"教师名称: {settings.get('teacher_name')}")
        print(f"回复风格: {settings.get('reply_style')}")
        print(f"语言: {settings.get('language')}")
        
        # 更新设置
        print("\n1.2 更新教师名称")
        response = await client.post(
            f"{BASE_URL}/api/settings/teacher_name",
            json={"value": "张老师"}
        )
        print(f"响应: {response.json()}")
        
        # 更新回复风格
        print("\n1.3 更改回复风格为友好型")
        response = await client.post(
            f"{BASE_URL}/api/settings/reply_style",
            json={"value": "friendly"}
        )
        print(f"响应: {response.json()}")


async def demo_quick_replies():
    """演示快捷回复功能"""
    print("\n" + "="*60)
    print("【2. 快捷回复功能演示】")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        # 添加快捷回复
        print("\n2.1 添加快捷回复")
        replies = [
            "非常好的问题！",
            "让我们一起来探讨这个问题",
            "这个知识点很重要，请大家记笔记"
        ]
        
        for reply in replies:
            response = await client.post(
                f"{BASE_URL}/api/quick-replies",
                params={"text": reply}
            )
            print(f"添加: {reply}")
        
        # 获取所有快捷回复
        print("\n2.2 获取所有快捷回复")
        response = await client.get(f"{BASE_URL}/api/quick-replies")
        all_replies = response.json()["replies"]
        for i, reply in enumerate(all_replies, 1):
            print(f"{i}. {reply}")


async def demo_students():
    """演示学生管理功能"""
    print("\n" + "="*60)
    print("【3. 学生管理功能演示】")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        # 添加学生
        print("\n3.1 添加学生")
        students = [
            {"name": "张三", "info": {"grade": "高一", "class": "1班"}},
            {"name": "李四", "info": {"grade": "高一", "class": "2班"}},
            {"name": "王五", "info": {"grade": "高二", "class": "1班"}}
        ]
        
        for student in students:
            response = await client.post(
                f"{BASE_URL}/api/students",
                params={"name": student["name"]},
                json=student.get("info")
            )
            print(f"添加学生: {student['name']} - {student['info']}")
        
        # 获取学生列表
        print("\n3.2 获取学生列表")
        response = await client.get(f"{BASE_URL}/api/students")
        student_list = response.json()["students"]
        for student in student_list:
            print(f"- {student['name']}: {student['info']}")


async def demo_session_management():
    """演示课堂会话管理"""
    print("\n" + "="*60)
    print("【4. 课堂会话管理演示】")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        # 开始会话
        print("\n4.1 开始新的课堂会话")
        response = await client.post(
            f"{BASE_URL}/api/session/start",
            params={"topic": "Python 面向对象编程"}
        )
        session = response.json()["session"]
        print(f"会话ID: {session['session_id']}")
        print(f"主题: {session['topic']}")
        print(f"开始时间: {session['start_time']}")
        
        # 模拟一些对话
        print("\n4.2 模拟课堂对话...")
        await asyncio.sleep(1)
        
        # 获取当前会话
        print("\n4.3 获取当前会话信息")
        response = await client.get(f"{BASE_URL}/api/session/current")
        current = response.json()["session"]
        if current:
            print(f"当前会话: {current['topic']}")
            print(f"持续时间: {current['duration_minutes']} 分钟")


async def demo_export():
    """演示导出功能"""
    print("\n" + "="*60)
    print("【5. 对话导出功能演示】")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        # 导出为不同格式
        formats = ["json", "txt", "markdown", "html"]
        
        for fmt in formats:
            print(f"\n5.{formats.index(fmt)+1} 导出为 {fmt.upper()} 格式")
            response = await client.get(f"{BASE_URL}/api/export/{fmt}")
            
            if response.status_code == 200:
                filename = f"demo_export.{fmt}"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"✓ 已导出到: {filename}")
            else:
                print(f"✗ 导出失败: {response.status_code}")


async def demo_analysis():
    """演示分析功能"""
    print("\n" + "="*60)
    print("【6. 智能分析功能演示】")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        # 参与度分析
        print("\n6.1 参与度分析")
        response = await client.get(f"{BASE_URL}/api/analysis/participation")
        if response.status_code == 200:
            data = response.json()
            print(f"教师发言: {data.get('teacher_turns', 0)} 次")
            print(f"学生发言: {data.get('student_turns', 0)} 次")
            print(f"学生参与度: {data.get('student_percentage', 0):.1f}%")
        
        # 提问分析
        print("\n6.2 提问分析")
        response = await client.get(f"{BASE_URL}/api/analysis/questions")
        if response.status_code == 200:
            data = response.json()
            print(f"学生提问总数: {data.get('total_questions', 0)} 个")
        
        # 关键词分析
        print("\n6.3 高频关键词分析")
        response = await client.get(f"{BASE_URL}/api/analysis/keywords?top_n=5")
        if response.status_code == 200:
            data = response.json()
            keywords = data.get('keywords', [])
            for kw in keywords:
                print(f"- {kw['word']}: {kw['count']} 次")
        
        # 生成报告
        print("\n6.4 生成课堂分析报告")
        response = await client.get(f"{BASE_URL}/api/analysis/report")
        if response.status_code == 200:
            data = response.json()
            report = data.get('report', '')
            print(report[:500] + "..." if len(report) > 500 else report)


async def demo_search():
    """演示搜索功能"""
    print("\n" + "="*60)
    print("【7. 对话搜索功能演示】")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        # 搜索关键词
        print("\n7.1 搜索包含 'Python' 的对话")
        response = await client.get(
            f"{BASE_URL}/api/search",
            params={"keyword": "Python", "case_sensitive": False}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"找到 {data['count']} 条匹配结果")
            for result in data['results'][:3]:  # 只显示前3条
                print(f"- [{result['role']}] {result['text'][:50]}...")


async def demo_reminder():
    """演示智能提醒功能"""
    print("\n" + "="*60)
    print("【8. 智能提醒功能演示】")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        # 添加关键词提醒
        print("\n8.1 添加关键词提醒")
        keywords = ["考试", "作业", "重点"]
        
        for keyword in keywords:
            response = await client.post(
                f"{BASE_URL}/api/reminder/keyword",
                params={"keyword": keyword}
            )
            print(f"添加关键词: {keyword}")
        
        # 查看未回答问题
        print("\n8.2 查看未回答的问题")
        response = await client.get(f"{BASE_URL}/api/reminder/unanswered")
        if response.status_code == 200:
            data = response.json()
            questions = data.get('questions', [])
            if questions:
                for q in questions:
                    print(f"- {q['question']}")
            else:
                print("暂无未回答的问题")


async def demo_session_statistics():
    """演示会话统计功能"""
    print("\n" + "="*60)
    print("【9. 课堂统计功能演示】")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        # 获取统计数据
        print("\n9.1 获取最近30天的统计数据")
        response = await client.get(
            f"{BASE_URL}/api/sessions/statistics",
            params={"days": 30}
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"总课堂数: {stats.get('total_sessions', 0)}")
            print(f"总时长: {stats.get('total_duration', 0):.1f} 分钟")
            print(f"平均时长: {stats.get('avg_duration', 0):.1f} 分钟")
            print(f"总对话数: {stats.get('total_conversations', 0)}")
            print(f"平均质量评分: {stats.get('avg_quality_score', 0):.1f}/100")
        
        # 获取最近的会话
        print("\n9.2 获取最近7天的课堂会话")
        response = await client.get(
            f"{BASE_URL}/api/sessions/recent",
            params={"days": 7}
        )
        
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('sessions', [])
            print(f"找到 {len(sessions)} 个会话")
            for session in sessions[:3]:  # 只显示前3个
                print(f"- {session['topic']} ({session['start_time'][:10]})")


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("  实时语音教学助手 - 功能演示")
    print("="*60)
    print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("请确保后端服务已启动 (python -m uvicorn backend.main:app)")
    print("="*60)
    
    try:
        # 检查服务是否运行
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/health")
            if response.status_code != 200:
                print("\n❌ 后端服务未运行，请先启动服务")
                return
        
        print("\n✓ 后端服务运行正常\n")
        
        # 运行各个演示
        await demo_settings()
        await demo_quick_replies()
        await demo_students()
        await demo_session_management()
        await demo_export()
        await demo_analysis()
        await demo_search()
        await demo_reminder()
        await demo_session_statistics()
        
        print("\n" + "="*60)
        print("  演示完成！")
        print("="*60)
        print("\n所有功能都已成功演示 ✓")
        print("您可以通过 API 文档查看更多详情: http://localhost:8000/docs")
        
    except httpx.ConnectError:
        print("\n❌ 无法连接到后端服务")
        print("请先启动服务: python -m uvicorn backend.main:app")
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")


if __name__ == "__main__":
    asyncio.run(main())

