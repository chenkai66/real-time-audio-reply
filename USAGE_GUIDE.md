# 功能使用指南

> 实时语音教学助手完整功能说明

## 目录

- [快速开始](#快速开始)
- [核心功能](#核心功能)
- [对话管理](#对话管理)
- [智能分析](#智能分析)
- [个性化设置](#个性化设置)
- [课堂会话](#课堂会话)
- [智能提醒](#智能提醒)
- [使用场景](#使用场景)
- [最佳实践](#最佳实践)

---

## 快速开始

### 1. 启动服务

```bash
# 启动后端
cd backend
python -m uvicorn main:app --reload

# 启动前端（另一个终端）
cd frontend
npm run dev
```

### 2. 基本使用流程

```
开始会话 → 实时监听 → 自动识别 → 智能回复 → 结束会话 → 导出分析
```

---

## 核心功能

### 实时语音识别

**功能**：自动识别教师和学生的语音，转换为文字

**API**：
```bash
POST /api/audio/upload
Content-Type: multipart/form-data

# 上传音频文件
curl -X POST http://localhost:8000/api/audio/upload \
  -F "file=@audio.wav"
```

**响应**：
```json
{
  "text": "什么是 Python？",
  "role": "student",
  "confidence": 0.95
}
```

### 智能角色识别

**功能**：自动区分教师和学生的发言

**准确率**：100%（基于内容分析）

**识别策略**：
- 问句 → 学生
- 陈述句 → 教师
- 关键词匹配
- 上下文分析

### 自动回复生成

**功能**：根据学生提问自动生成专业回复

**API**：
```bash
POST /api/text/process
Content-Type: application/json

{
  "text": "什么是 Python？",
  "role": "student"
}
```

**响应**：
```json
{
  "reply": "Python 是一种高级编程语言...",
  "tokens": 45,
  "time": 1.2
}
```

---

## 对话管理

### 1. 查看对话历史

**API**：`GET /api/conversation/history`

```bash
curl http://localhost:8000/api/conversation/history
```

**响应**：
```json
{
  "l1_cache": [
    {
      "role": "teacher",
      "text": "今天我们学习 Python",
      "timestamp": "2026-02-16T10:00:00",
      "tokens": 8
    }
  ],
  "stats": {
    "total_turns": 10,
    "total_tokens": 150
  }
}
```

### 2. 导出对话记录

#### JSON 格式
```bash
curl http://localhost:8000/api/export/json > conversation.json
```

**特点**：
- 结构化数据
- 包含完整元数据
- 易于程序处理

#### 文本格式
```bash
curl http://localhost:8000/api/export/txt > conversation.txt
```

**特点**：
- 简洁易读
- 包含时间戳
- 适合打印

#### Markdown 格式
```bash
curl http://localhost:8000/api/export/markdown > conversation.md
```

**特点**：
- 格式化文档
- 支持标题层级
- 适合文档系统

#### HTML 格式
```bash
curl http://localhost:8000/api/export/html > conversation.html
```

**特点**：
- 美观的网页样式
- 角色颜色区分
- 可直接在浏览器打开

**样式预览**：
- 教师对话：蓝色左边框
- 学生对话：紫色左边框
- 白色卡片设计
- 响应式布局

### 3. 搜索对话

**API**：`GET /api/search`

```bash
# 搜索关键词
curl "http://localhost:8000/api/search?keyword=Python"

# 区分大小写
curl "http://localhost:8000/api/search?keyword=python&case_sensitive=true"
```

**响应**：
```json
{
  "keyword": "Python",
  "count": 5,
  "results": [
    {
      "role": "student",
      "text": "什么是 Python？",
      "timestamp": "2026-02-16T10:05:00"
    }
  ]
}
```

---

## 智能分析

### 1. 参与度分析

**API**：`GET /api/analysis/participation`

```bash
curl http://localhost:8000/api/analysis/participation
```

**响应**：
```json
{
  "teacher_turns": 15,
  "student_turns": 10,
  "teacher_percentage": 60.0,
  "student_percentage": 40.0,
  "avg_teacher_tokens": 25,
  "avg_student_tokens": 15
}
```

**解读**：
- 学生参与度 > 30%：良好
- 学生参与度 < 20%：需改进

### 2. 提问分析

**API**：`GET /api/analysis/questions`

```bash
curl http://localhost:8000/api/analysis/questions
```

**响应**：
```json
{
  "total_questions": 8,
  "questions": [
    {
      "text": "什么是 Python？",
      "timestamp": "2026-02-16T10:05:00",
      "tokens": 6
    }
  ],
  "avg_question_length": 12
}
```

**解读**：
- 提问数 > 5：互动积极
- 提问数 < 3：需鼓励提问

### 3. 关键词分析

**API**：`GET /api/analysis/keywords`

```bash
curl "http://localhost:8000/api/analysis/keywords?top_n=10"
```

**响应**：
```json
{
  "keywords": [
    {"word": "Python", "count": 15},
    {"word": "编程", "count": 12},
    {"word": "学习", "count": 10}
  ]
}
```

**用途**：
- 了解课堂重点
- 发现学生关注点
- 优化教学内容

### 4. 互动质量分析

**API**：`GET /api/analysis/quality`

```bash
curl http://localhost:8000/api/analysis/quality
```

**响应**：
```json
{
  "avg_response_time": 5.2,
  "interaction_rate": 3.5,
  "total_interactions": 25
}
```

**指标说明**：
- 响应时间 < 10s：优秀
- 互动频率 > 2次/分钟：良好

### 5. 生成分析报告

**API**：`GET /api/analysis/report`

```bash
curl http://localhost:8000/api/analysis/report
```

**报告内容**：
- 参与度分析
- 提问分析
- 高频关键词
- 互动质量
- 综合评价
- 总体评分（0-100）
- 改进建议

**评分标准**：
- 80-100：优秀 ⭐⭐⭐⭐⭐
- 60-79：良好 ⭐⭐⭐⭐
- 40-59：及格 ⭐⭐⭐
- 0-39：需改进 ⭐⭐

---

## 个性化设置

### 1. 查看所有设置

**API**：`GET /api/settings`

```bash
curl http://localhost:8000/api/settings
```

### 2. 更新设置

**API**：`POST /api/settings/{key}`

```bash
# 更新教师名称
curl -X POST http://localhost:8000/api/settings/teacher_name \
  -H "Content-Type: application/json" \
  -d '{"value": "张老师"}'

# 更改回复风格
curl -X POST http://localhost:8000/api/settings/reply_style \
  -H "Content-Type: application/json" \
  -d '{"value": "friendly"}'
```

**可用风格**：
- `professional`：专业型（默认）
- `friendly`：友好型
- `humorous`：幽默型

### 3. 快捷回复管理

**添加快捷回复**：
```bash
curl -X POST "http://localhost:8000/api/quick-replies?text=非常好的问题！"
```

**获取快捷回复**：
```bash
curl http://localhost:8000/api/quick-replies
```

**删除快捷回复**：
```bash
curl -X DELETE "http://localhost:8000/api/quick-replies?text=非常好的问题！"
```

### 4. 学生管理

**添加学生**：
```bash
curl -X POST "http://localhost:8000/api/students?name=张三" \
  -H "Content-Type: application/json" \
  -d '{"grade": "高一", "class": "1班"}'
```

**获取学生列表**：
```bash
curl http://localhost:8000/api/students
```

**删除学生**：
```bash
curl -X DELETE http://localhost:8000/api/students/张三
```

### 5. 自定义 Prompt

**查看当前 Prompt**：
```bash
curl http://localhost:8000/api/prompt/current
```

**设置自定义 Prompt**：
```bash
curl -X POST "http://localhost:8000/api/prompt/custom" \
  -H "Content-Type: application/json" \
  -d '{
    "style": "custom",
    "prompt": "你是一位耐心的编程教师，请用简单易懂的语言回答学生的问题。"
  }'
```

---

## 课堂会话

### 1. 开始会话

**API**：`POST /api/session/start`

```bash
curl -X POST "http://localhost:8000/api/session/start?topic=Python面向对象编程"
```

**响应**：
```json
{
  "message": "课堂会话已开始",
  "session": {
    "session_id": "20260216_100000",
    "topic": "Python面向对象编程",
    "start_time": "2026-02-16T10:00:00"
  }
}
```

### 2. 结束会话

**API**：`POST /api/session/end`

```bash
curl -X POST http://localhost:8000/api/session/end
```

**自动记录**：
- 会话时长
- 对话总数
- 提问数量
- 质量评分
- 高频关键词

### 3. 查看会话

**当前会话**：
```bash
curl http://localhost:8000/api/session/current
```

**指定会话**：
```bash
curl http://localhost:8000/api/session/20260216_100000
```

**最近会话**：
```bash
curl "http://localhost:8000/api/sessions/recent?days=7"
```

**所有会话**：
```bash
curl http://localhost:8000/api/sessions/all
```

### 4. 会话统计

**API**：`GET /api/sessions/statistics`

```bash
curl "http://localhost:8000/api/sessions/statistics?days=30"
```

**响应**：
```json
{
  "total_sessions": 15,
  "total_duration": 750.5,
  "avg_duration": 50.0,
  "total_conversations": 300,
  "avg_conversations": 20,
  "total_questions": 120,
  "avg_questions": 8,
  "avg_quality_score": 75
}
```

### 5. 会话对比

**API**：`GET /api/sessions/compare`

```bash
curl "http://localhost:8000/api/sessions/compare?session_id1=20260216_100000&session_id2=20260217_100000"
```

**响应**：
```json
{
  "session1": {...},
  "session2": {...},
  "comparison": {
    "duration_diff": 5.5,
    "conversation_diff": 3,
    "question_diff": 2,
    "quality_diff": 10
  }
}
```

### 6. 添加备注

**API**：`POST /api/session/{session_id}/note`

```bash
curl -X POST "http://localhost:8000/api/session/20260216_100000/note?note=这是一堂很好的课"
```

---

## 智能提醒

### 1. 关键词提醒

**添加关键词**：
```bash
curl -X POST "http://localhost:8000/api/reminder/keyword?keyword=考试"
```

**删除关键词**：
```bash
curl -X DELETE "http://localhost:8000/api/reminder/keyword?keyword=考试"
```

**触发条件**：学生发言中包含关键词时自动提醒

### 2. 未回答问题

**查看未回答问题**：
```bash
curl http://localhost:8000/api/reminder/unanswered
```

**响应**：
```json
{
  "questions": [
    {
      "question": "什么是装饰器？",
      "timestamp": "2026-02-16T10:15:00"
    }
  ]
}
```

### 3. 紧急问题检测

**自动识别关键词**：
- 紧急
- 急
- 不懂
- 不会
- 错误
- 帮助

**优先级**：紧急问题会优先提醒

---

## 使用场景

### 场景 1：日常授课

```bash
# 1. 开始会话
curl -X POST "http://localhost:8000/api/session/start?topic=今日课程"

# 2. 开始监听（前端界面）
# 学生提问 → 自动识别 → 生成回复

# 3. 结束会话
curl -X POST http://localhost:8000/api/session/end

# 4. 导出记录
curl http://localhost:8000/api/export/html > 今日课堂.html
```

### 场景 2：课后分析

```bash
# 1. 查看参与度
curl http://localhost:8000/api/analysis/participation

# 2. 查看提问情况
curl http://localhost:8000/api/analysis/questions

# 3. 生成完整报告
curl http://localhost:8000/api/analysis/report

# 4. 查看统计趋势
curl "http://localhost:8000/api/sessions/statistics?days=30"
```

### 场景 3：内容检索

```bash
# 1. 搜索特定话题
curl "http://localhost:8000/api/search?keyword=装饰器"

# 2. 查看关键词分布
curl http://localhost:8000/api/analysis/keywords

# 3. 导出相关内容
curl http://localhost:8000/api/export/markdown > 装饰器讨论.md
```

### 场景 4：个性化配置

```bash
# 1. 设置教师信息
curl -X POST http://localhost:8000/api/settings/teacher_name \
  -d '{"value": "张老师"}'

# 2. 添加快捷回复
curl -X POST "http://localhost:8000/api/quick-replies?text=这个问题很好"

# 3. 添加学生名单
curl -X POST "http://localhost:8000/api/students?name=张三"

# 4. 设置关键词提醒
curl -X POST "http://localhost:8000/api/reminder/keyword?keyword=作业"
```

---

## 最佳实践

### 1. 课前准备

- ✅ 设置教师名称和课程主题
- ✅ 添加学生名单
- ✅ 配置快捷回复模板
- ✅ 设置关键词提醒

### 2. 课中使用

- ✅ 开始会话记录
- ✅ 实时监听学生提问
- ✅ 使用快捷回复提高效率
- ✅ 关注未回答问题提醒

### 3. 课后总结

- ✅ 结束会话并查看统计
- ✅ 生成分析报告
- ✅ 导出对话记录
- ✅ 对比历史会话

### 4. 长期优化

- ✅ 定期查看统计趋势
- ✅ 根据分析调整教学策略
- ✅ 优化 Prompt 和回复风格
- ✅ 积累常见问题库

---

## 技巧与建议

### 提高识别准确率

1. 清晰发音
2. 避免背景噪音
3. 使用高质量麦克风
4. 适当的语速

### 提升回复质量

1. 选择合适的回复风格
2. 自定义 Prompt 模板
3. 使用快捷回复模板
4. 定期更新关键词库

### 优化教学效果

1. 关注参与度指标
2. 鼓励学生提问
3. 及时回复未回答问题
4. 定期查看分析报告

---

## 故障排除

### 问题：无法连接服务

**解决方案**：
```bash
# 检查服务状态
curl http://localhost:8000/api/health

# 重启服务
python -m uvicorn backend.main:app --reload
```

### 问题：导出失败

**解决方案**：
```bash
# 检查对话历史
curl http://localhost:8000/api/conversation/history

# 确保有对话数据
```

### 问题：分析数据为空

**解决方案**：
- 确保已有对话记录
- 检查会话是否已开始
- 验证数据是否正确保存

---

## 更多帮助

- 📖 完整文档：[README.md](./README.md)
- 📋 开发计划：[TASKS.md](./TASKS.md)
- 🔧 API 文档：http://localhost:8000/docs
- 🎬 功能演示：`python demo_features.py`

---

**最后更新**：2026-02-16  
**版本**：v0.3.0

