# API 快速参考

> 所有 API 端点速查表

## 基础信息

- **Base URL**: `http://localhost:8000`
- **文档**: `http://localhost:8000/docs`
- **健康检查**: `GET /api/health`

---

## 📊 对话管理

| 功能 | 方法 | 端点 | 参数 |
|------|------|------|------|
| 获取历史 | GET | `/api/conversation/history` | - |
| 导出JSON | GET | `/api/export/json` | - |
| 导出TXT | GET | `/api/export/txt` | - |
| 导出Markdown | GET | `/api/export/markdown` | - |
| 导出HTML | GET | `/api/export/html` | - |
| 搜索对话 | GET | `/api/search` | `keyword`, `case_sensitive` |

**示例**：
```bash
curl http://localhost:8000/api/export/html > conversation.html
curl "http://localhost:8000/api/search?keyword=Python"
```

---

## 📈 智能分析

| 功能 | 方法 | 端点 | 参数 |
|------|------|------|------|
| 参与度分析 | GET | `/api/analysis/participation` | - |
| 提问分析 | GET | `/api/analysis/questions` | - |
| 关键词分析 | GET | `/api/analysis/keywords` | `top_n` |
| 互动质量 | GET | `/api/analysis/quality` | - |
| 生成报告 | GET | `/api/analysis/report` | - |

**示例**：
```bash
curl http://localhost:8000/api/analysis/participation
curl "http://localhost:8000/api/analysis/keywords?top_n=10"
curl http://localhost:8000/api/analysis/report
```

---

## ⚙️ 个性化设置

### 基础设置

| 功能 | 方法 | 端点 | 参数 |
|------|------|------|------|
| 获取所有设置 | GET | `/api/settings` | - |
| 获取指定设置 | GET | `/api/settings/{key}` | - |
| 更新设置 | POST | `/api/settings/{key}` | `value` |
| 重置设置 | POST | `/api/settings/reset` | - |

**示例**：
```bash
curl http://localhost:8000/api/settings
curl -X POST http://localhost:8000/api/settings/teacher_name \
  -H "Content-Type: application/json" \
  -d '{"value": "张老师"}'
```

### 快捷回复

| 功能 | 方法 | 端点 | 参数 |
|------|------|------|------|
| 获取列表 | GET | `/api/quick-replies` | - |
| 添加回复 | POST | `/api/quick-replies` | `text` |
| 删除回复 | DELETE | `/api/quick-replies` | `text` |

**示例**：
```bash
curl http://localhost:8000/api/quick-replies
curl -X POST "http://localhost:8000/api/quick-replies?text=很好的问题"
curl -X DELETE "http://localhost:8000/api/quick-replies?text=很好的问题"
```

### 学生管理

| 功能 | 方法 | 端点 | 参数 |
|------|------|------|------|
| 获取列表 | GET | `/api/students` | - |
| 添加学生 | POST | `/api/students` | `name`, `info` |
| 删除学生 | DELETE | `/api/students/{name}` | - |

**示例**：
```bash
curl http://localhost:8000/api/students
curl -X POST "http://localhost:8000/api/students?name=张三" \
  -d '{"grade": "高一"}'
curl -X DELETE http://localhost:8000/api/students/张三
```

### Prompt 管理

| 功能 | 方法 | 端点 | 参数 |
|------|------|------|------|
| 获取当前 | GET | `/api/prompt/current` | - |
| 自定义 | POST | `/api/prompt/custom` | `style`, `prompt` |

**示例**：
```bash
curl http://localhost:8000/api/prompt/current
curl -X POST "http://localhost:8000/api/prompt/custom" \
  -d '{"style": "custom", "prompt": "你是一位耐心的老师..."}'
```

---

## 📚 课堂会话

| 功能 | 方法 | 端点 | 参数 |
|------|------|------|------|
| 开始会话 | POST | `/api/session/start` | `topic` |
| 结束会话 | POST | `/api/session/end` | - |
| 当前会话 | GET | `/api/session/current` | - |
| 指定会话 | GET | `/api/session/{session_id}` | - |
| 最近会话 | GET | `/api/sessions/recent` | `days` |
| 所有会话 | GET | `/api/sessions/all` | - |
| 会话统计 | GET | `/api/sessions/statistics` | `days` |
| 会话对比 | GET | `/api/sessions/compare` | `session_id1`, `session_id2` |
| 添加备注 | POST | `/api/session/{session_id}/note` | `note` |

**示例**：
```bash
# 开始会话
curl -X POST "http://localhost:8000/api/session/start?topic=Python基础"

# 结束会话
curl -X POST http://localhost:8000/api/session/end

# 查看统计
curl "http://localhost:8000/api/sessions/statistics?days=30"

# 对比会话
curl "http://localhost:8000/api/sessions/compare?session_id1=xxx&session_id2=yyy"
```

---

## 🔔 智能提醒

| 功能 | 方法 | 端点 | 参数 |
|------|------|------|------|
| 添加关键词 | POST | `/api/reminder/keyword` | `keyword` |
| 删除关键词 | DELETE | `/api/reminder/keyword` | `keyword` |
| 未回答问题 | GET | `/api/reminder/unanswered` | - |

**示例**：
```bash
curl -X POST "http://localhost:8000/api/reminder/keyword?keyword=考试"
curl -X DELETE "http://localhost:8000/api/reminder/keyword?keyword=考试"
curl http://localhost:8000/api/reminder/unanswered
```

---

## 🎤 核心功能

| 功能 | 方法 | 端点 | 参数 |
|------|------|------|------|
| 上传音频 | POST | `/api/audio/upload` | `file` |
| 处理文本 | POST | `/api/text/process` | `text`, `role` |
| 性能指标 | GET | `/api/metrics` | - |

**示例**：
```bash
curl -X POST http://localhost:8000/api/audio/upload \
  -F "file=@audio.wav"

curl -X POST http://localhost:8000/api/text/process \
  -H "Content-Type: application/json" \
  -d '{"text": "什么是Python？", "role": "student"}'
```

---

## 📋 常用组合

### 完整课堂流程

```bash
# 1. 开始会话
curl -X POST "http://localhost:8000/api/session/start?topic=今日课程"

# 2. 课中监听（前端界面操作）

# 3. 结束会话
curl -X POST http://localhost:8000/api/session/end

# 4. 导出记录
curl http://localhost:8000/api/export/html > 今日课堂.html

# 5. 查看分析
curl http://localhost:8000/api/analysis/report
```

### 快速配置

```bash
# 设置教师信息
curl -X POST http://localhost:8000/api/settings/teacher_name \
  -d '{"value": "张老师"}'

# 设置回复风格
curl -X POST http://localhost:8000/api/settings/reply_style \
  -d '{"value": "friendly"}'

# 添加快捷回复
curl -X POST "http://localhost:8000/api/quick-replies?text=很好的问题"

# 添加关键词提醒
curl -X POST "http://localhost:8000/api/reminder/keyword?keyword=作业"
```

### 数据分析

```bash
# 参与度
curl http://localhost:8000/api/analysis/participation

# 提问情况
curl http://localhost:8000/api/analysis/questions

# 关键词
curl "http://localhost:8000/api/analysis/keywords?top_n=10"

# 完整报告
curl http://localhost:8000/api/analysis/report
```

---

## 🔧 响应格式

### 成功响应
```json
{
  "message": "操作成功",
  "data": {...}
}
```

### 错误响应
```json
{
  "detail": "错误信息"
}
```

---

## 💡 提示

### 回复风格
- `professional` - 专业型（默认）
- `friendly` - 友好型
- `humorous` - 幽默型

### 导出格式
- `json` - 结构化数据
- `txt` - 纯文本
- `markdown` - Markdown 文档
- `html` - 网页格式

### 时间参数
- `days=7` - 最近7天
- `days=30` - 最近30天

---

## 📞 获取帮助

- 📖 详细文档：[USAGE_GUIDE.md](./USAGE_GUIDE.md)
- 🔧 API 文档：http://localhost:8000/docs
- 🎬 功能演示：`python demo_features.py`

---

**版本**：v0.3.0  
**更新**：2026-02-16

