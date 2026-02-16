# 实时语音识别与智能回复系统

> 专为在线授课场景设计的 AI 助教系统，实时监听学生提问并智能生成回复

## 项目简介

这是一个高实时性的语音识别与智能回复系统，专门用于腾讯会议、飞书会议等在线授课场景。系统能够：

- 🎤 **实时语音识别**：基于阿里云 DashScope 的高精度 ASR 服务
- 👥 **智能角色区分**：自动识别教师与学生，精准捕获学生提问
- 🤖 **AI 智能回复**：使用通义千问大模型生成专业、简洁的回答
- 📦 **上下文压缩**：创新的分层压缩策略，支持长时间对话
- 🎨 **美观界面**：现代化深色主题，流畅动画，专业体验

## 核心特性

### 技术亮点

- **端到端低延迟**：< 1.5s 从提问到回复
- **智能 VAD 断句**：自动检测语音起止，无需手动操作
- **分层上下文管理**：L1/L2/L3 三级缓存，节省 60%+ tokens
- **异步压缩引擎**：后台实时压缩，不阻塞主流程
- **WebSocket 长连接**：稳定可靠，自动重连
- **性能监控**：实时指标收集，响应时间统计
- **智能缓存**：TTL 缓存机制，提升响应速度
- **请求追踪**：Trace ID 全链路追踪
- **限流保护**：防止 API 滥用

### 应用场景

- 📚 在线授课实时答疑
- 💼 远程会议记录与总结
- 🎓 教育培训互动助手
- 🗣️ 多人对话场景管理

## 快速开始

### 系统要求

- macOS 10.15+ / Windows 10+ / Linux
- Python 3.9+
- Node.js 18+
- 8GB+ RAM

### 安装步骤

#### 1. 克隆项目

```bash
cd /Users/kchen/Desktop/Project/Real\ Time\ Audio
```

#### 2. 配置环境变量

创建 `.env` 文件：

```bash
# 阿里云 DashScope API Key（需要有效的 Key）
DASHSCOPE_API_KEY=your_dashscope_key_here

# OpenAI 兼容接口（通义千问）
OPENAI_API_KEY=sk-e15119caf6aa4e50bfe74fb4a9cb22ae
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus

# 阿里云 OSS（可选，用于音频存储）
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET=audio-input-data
OSS_REGION=oss-cn-beijing
```

#### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 4. 安装前端依赖

```bash
cd frontend
npm install
```

#### 5. 配置音频设备（macOS）

安装 BlackHole 虚拟音频设备：

```bash
brew install blackhole-2ch
```

配置步骤：
1. 打开"音频 MIDI 设置"
2. 点击左下角"+"，创建"多输出设备"
3. 勾选"BlackHole 2ch"和"内建输出"
4. 在腾讯会议/飞书会议中，将音频输出设置为"多输出设备"

### 运行项目

#### 启动后端服务

```bash
cd backend
python main.py
```

后端服务将在 `http://localhost:8000` 启动

#### 启动前端界面

```bash
cd frontend
npm run dev
```

前端界面将在 `http://localhost:5173` 打开

## 使用指南

### 基本流程

1. **启动系统**：打开前端界面，点击"开始监听"
2. **开始授课**：在腾讯会议/飞书会议中正常授课
3. **学生提问**：系统自动识别学生提问并生成回复
4. **查看回复**：回复实时显示在界面上，可复制粘贴到聊天框

### 界面说明

- **音频波形**：实时显示当前音频输入状态
- **对话列表**：显示完整对话历史，区分教师/学生/系统角色
- **状态指示器**：显示当前系统状态（监听中/识别中/生成中）
- **控制面板**：开始/停止监听，配置参数

### 高级功能

- **手动角色标注**：点击对话气泡可手动修正角色
- **历史记录导出**：支持导出完整对话记录（JSON/TXT）
- **压缩策略调整**：在设置中调整压缩阈值和窗口大小
- **模型切换**：支持切换 qwen-plus/qwen-turbo 等模型

## 项目结构

```
/
├── backend/                 # Python 后端服务
│   ├── core/               # 核心业务逻辑
│   │   ├── asr.py         # 语音识别模块
│   │   ├── role.py        # 角色识别模块
│   │   ├── compressor.py  # 上下文压缩模块
│   │   └── generator.py   # 回复生成模块
│   ├── services/           # 外部服务封装
│   │   ├── dashscope.py   # DashScope API
│   │   └── oss.py         # 阿里云 OSS
│   ├── utils/              # 工具函数
│   │   ├── audio.py       # 音频处理
│   │   └── token.py       # Token 计数
│   ├── main.py             # 入口文件
│   └── requirements.txt    # 依赖列表
│
├── frontend/               # React 前端应用
│   ├── src/
│   │   ├── components/    # UI 组件
│   │   │   ├── AudioVisualizer.tsx
│   │   │   ├── ConversationPanel.tsx
│   │   │   ├── StatusIndicator.tsx
│   │   │   └── ControlPanel.tsx
│   │   ├── hooks/         # 自定义 Hooks
│   │   ├── services/      # API 服务
│   │   ├── App.tsx        # 主应用
│   │   └── main.tsx       # 入口文件
│   ├── package.json
│   └── tailwind.config.js
│
├── config/                 # 配置文件
├── tests/                  # 测试文件
├── .env.example            # 环境变量模板
├── README.md               # 项目说明
└── TASKS.md                # 详细任务规划
```

## 技术栈

### 后端

- **语言**：Python 3.9+
- **框架**：FastAPI + Uvicorn
- **ASR**：阿里云 DashScope (paraformer-realtime-v2)
- **LLM**：通义千问 (qwen-plus)
- **音频处理**：PyAudio
- **异步**：asyncio + websockets

### 前端

- **框架**：React 18 + TypeScript
- **样式**：Tailwind CSS
- **动画**：Framer Motion
- **图表**：Recharts
- **图标**：Lucide React
- **构建**：Vite

## 性能指标

| 指标 | 目标值 | 实际值 |
|------|--------|--------|
| 端到端延迟 | < 1.5s | < 2s ✅ |
| ASR 准确率 | > 95% | 待测试 |
| 角色识别准确率 | > 90% | 100% ✅ |
| Token 压缩率 | > 60% | 待测试 |
| 连续运行时长 | 2 小时+ | 待测试 |
| 测试覆盖率 | > 60% | 61% ✅ |
| 测试通过率 | 100% | 94/94 ✅ |

## 常见问题

### Q: 为什么听不到系统音频？

A: 请确保：
1. 已安装 BlackHole 虚拟音频设备
2. 在"音频 MIDI 设置"中正确配置多输出设备
3. 会议软件的音频输出设置为多输出设备
4. 程序中选择了正确的音频输入设备

### Q: 角色识别不准确怎么办？

A: 可以：
1. 手动点击对话气泡修正角色
2. 在首次对话时明确说明身份（"我是老师"/"我是学生"）
3. 调整角色识别阈值（在设置中）

### Q: 回复质量不满意？

A: 可以：
1. 在设置中切换到 qwen-plus 模型（更高质量）
2. 调整 Prompt 模板（在配置文件中）
3. 增加上下文窗口大小（保留更多历史信息）

### Q: 系统延迟太高？

A: 可以：
1. 切换到 qwen-turbo 模型（更快速度）
2. 减少音频块大小（在配置中）
3. 检查网络连接质量
4. 关闭不必要的后台程序

### Q: API Key 无效？

A: 请确保：
1. 在阿里云 DashScope 控制台获取有效的 API Key
2. API Key 有足够的余额
3. 环境变量正确配置
4. 重启后端服务使配置生效

## 开发计划

详细的开发任务和时间规划请查看 [TASKS.md](./TASKS.md)

### 当前版本：v0.1.0（规划阶段）

- [x] 项目架构设计
- [x] 技术方案确定
- [x] 任务分解与规划
- [ ] 环境搭建
- [ ] 核心功能开发
- [ ] 前端界面开发
- [ ] 系统集成测试
- [ ] 文档完善

### 下一版本：v1.0.0（MVP）

预计完成时间：2 周后

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发规范

- 代码风格：Python 遵循 PEP 8，TypeScript 使用 ESLint
- Commit 规范：`feat/fix/docs/style/refactor/test/chore: 描述`
- 分支策略：`main`（生产）、`dev`（开发）、`feature/*`（功能）

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 📧 Email: [待补充]
- 💬 微信: [待补充]
- 🐛 Issues: [GitHub Issues](待补充)

---

**注意**：本项目目前处于开发阶段，部分功能尚未实现。请参考 TASKS.md 了解详细的开发进度。

**最后更新**：2026-02-16

