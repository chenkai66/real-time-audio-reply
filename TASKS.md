# 实时语音识别与智能回复系统 - 任务规划

## 项目概述

构建一个高实时性的语音识别与智能回复系统，用于腾讯会议、飞书会议等在线授课场景。系统能够：
- 实时监听并识别语音对话
- 智能区分教师与学生角色
- 自动检测学生提问并生成回复
- 实现高效的上下文压缩策略
- 提供美观简约的前端界面

---

## 核心技术架构

### 1. 音频采集层
- **系统音频捕获**：使用 BlackHole/Loopback 虚拟音频设备捕获系统音频
- **麦克风输入**：同时支持麦克风输入作为备选方案
- **音频格式**：PCM 16kHz 16bit 单声道
- **缓冲策略**：200ms 音频块（3200 字节）实时传输

### 2. 语音识别层（ASR）
- **服务提供商**：阿里云 DashScope
- **模型选择**：paraformer-realtime-v2（高准确率）或 fun-asr-realtime（低延迟）
- **连接方式**：WebSocket 持久连接
- **VAD 模式**：自动语音活动检测，智能断句
- **实时性要求**：端到端延迟 < 500ms

### 3. 角色识别与对话管理层
- **角色识别策略**：
  - 首次对话：通过大模型分析语音内容特征判断角色（教师/学生）
  - 后续对话：基于声纹特征 + 内容语义双重判断
  - 角色缓存：维护角色-声纹映射表
  
- **对话状态机**：
  ```
  [初始化] → [教师发言] → [等待学生提问] → [学生提问] → [生成回复] → [等待学生提问]
  ```

### 4. 上下文压缩层（核心优化）
- **实时压缩策略**：
  - **滑动窗口**：保留最近 5 轮完整对话（约 2000 tokens）
  - **关键信息提取**：后台异步提取关键实体、主题、问题
  - **分层存储**：
    - L1：最近 2 轮对话（完整保留）
    - L2：3-5 轮对话（摘要保留）
    - L3：历史对话（仅保留关键问题索引）
  
- **压缩触发条件**：
  - 累计 tokens > 3000 时触发
  - 每 3 轮对话后台异步压缩
  - 使用 qwen-turbo 进行摘要生成

- **压缩算法**：
  ```
  原始对话 → 提取关键实体 → 生成摘要 → 保留问答对 → 丢弃冗余信息
  ```

### 5. 大模型回复层
- **模型选择**：qwen-plus（平衡性能与成本）
- **Prompt 工程**：
  - 系统角色：授课助手
  - 上下文注入：压缩后的历史对话
  - 约束条件：简洁、准确、教学场景适配
  
- **回复策略**：
  - 仅响应学生提问
  - 过滤无效问题（如"嗯"、"好的"）
  - 支持多轮追问

### 6. 前端展示层
- **技术栈**：React + TypeScript + Tailwind CSS
- **设计风格**：
  - 深色主题为主，护眼且专业
  - 使用 JetBrains Mono / Fira Code 等编程字体
  - 渐变色点缀（蓝紫色系）
  - 流畅的动画过渡（Framer Motion）
  
- **核心组件**：
  - 实时语音波形可视化
  - 对话历史滚动列表（角色标识）
  - 系统状态指示器（监听中/识别中/回复中）
  - 压缩进度提示

---

## 详细任务分解

### Phase 1：环境配置与基础架构（2-3 天）

#### Task 1.1：项目初始化
- [ ] 创建项目目录结构
  ```
  /
  ├── backend/              # Python 后端
  │   ├── core/            # 核心业务逻辑
  │   ├── services/        # 外部服务封装
  │   ├── utils/           # 工具函数
  │   └── main.py          # 入口文件
  ├── frontend/            # React 前端
  │   ├── src/
  │   │   ├── components/  # UI 组件
  │   │   ├── hooks/       # 自定义 Hooks
  │   │   ├── services/    # API 服务
  │   │   └── App.tsx      # 主应用
  │   └── package.json
  ├── config/              # 配置文件
  ├── tests/               # 测试文件
  ├── README.md
  └── TASKS.md
  ```

- [ ] 配置依赖管理
  - 后端：`requirements.txt`（dashscope, pyaudio, websockets, fastapi, uvicorn）
  - 前端：`package.json`（react, typescript, tailwind, framer-motion, recharts）

- [ ] 环境变量验证
  - 验证 DASHSCOPE_API_KEY（需更新有效 Key）
  - 验证 OPENAI_API_KEY 和 OPENAI_BASE_URL
  - 验证阿里云 OSS 配置

#### Task 1.2：音频采集模块
- [ ] 安装虚拟音频设备（BlackHole for macOS）
- [ ] 实现系统音频捕获类 `SystemAudioCapture`
  - 支持设备枚举
  - 支持音频格式转换（PCM 16kHz）
  - 实现音频流缓冲队列
  
- [ ] 实现麦克风捕获类 `MicrophoneCapture`（备用方案）
- [ ] 音频预处理：降噪、音量归一化

#### Task 1.3：WebSocket 通信框架
- [ ] 后端 WebSocket 服务器（FastAPI）
  - 路由：`/ws/audio`（音频上传）
  - 路由：`/ws/transcript`（实时转写推送）
  
- [ ] 前端 WebSocket 客户端
  - 自动重连机制
  - 心跳保活
  - 消息队列管理

---

### Phase 2：语音识别与角色判断（3-4 天）

#### Task 2.1：阿里云 ASR 集成
- [ ] 封装 DashScope ASR 服务类 `RealtimeASR`
  - WebSocket 连接管理
  - VAD 模式配置
  - 实时转写回调处理
  - 错误重试机制
  
- [ ] 实现语音结束检测
  - 监听 `speech_stopped` 事件
  - 获取 `is_final=True` 的完整文本
  
- [ ] 性能优化
  - 音频块大小调优（测试 100ms/200ms/300ms）
  - 并发连接池管理

#### Task 2.2：角色识别模块
- [ ] 实现 `RoleIdentifier` 类
  - **首次识别**：
    ```python
    def identify_initial_role(text: str) -> str:
        # 使用 qwen-turbo 分析语音内容
        # Prompt: "判断以下内容是教师发言还是学生提问：{text}"
        # 返回：teacher / student
    ```
  
  - **声纹特征提取**（简化版）：
    - 提取音频 MFCC 特征
    - 计算特征向量相似度
    - 维护角色-特征映射表
  
  - **混合判断策略**：
    ```python
    if 声纹相似度 > 0.8:
        return 缓存角色
    else:
        return 大模型判断(text)
    ```

- [ ] 实现对话状态管理 `ConversationState`
  - 状态：INIT / TEACHER_SPEAKING / WAITING_QUESTION / STUDENT_ASKING / GENERATING_REPLY
  - 状态转换逻辑
  - 角色历史记录

#### Task 2.3：提问检测与过滤
- [ ] 实现问题检测器 `QuestionDetector`
  - 规则匹配：包含"吗"、"呢"、"如何"、"为什么"等
  - 大模型判断：是否为有效提问
  - 过滤无效输入：语气词、确认词
  
- [ ] 提问优先级队列
  - 支持多个学生同时提问
  - 按时间顺序排队处理

---

### Phase 3：上下文压缩与管理（2-3 天）

#### Task 3.1：对话历史管理
- [ ] 实现 `ConversationHistory` 类
  ```python
  class ConversationHistory:
      def __init__(self):
          self.l1_cache = []  # 最近 2 轮完整对话
          self.l2_cache = []  # 3-5 轮摘要
          self.l3_index = []  # 历史问题索引
          self.total_tokens = 0
      
      def add_turn(self, role, text):
          # 添加对话轮次
          # 自动触发压缩检查
      
      def get_context(self) -> str:
          # 返回用于大模型的上下文
  ```

- [ ] Token 计数器
  - 使用 tiktoken 库精确计算
  - 实时监控 token 使用量

#### Task 3.2：实时压缩引擎
- [ ] 实现 `ContextCompressor` 类
  - **异步压缩任务**：
    ```python
    async def compress_background():
        while True:
            if should_compress():
                summary = await generate_summary(l1_cache[-3:])
                move_to_l2(summary)
            await asyncio.sleep(5)
    ```
  
  - **摘要生成 Prompt**：
    ```
    将以下对话压缩为关键信息摘要，保留：
    1. 主要讨论主题
    2. 学生提出的问题
    3. 重要的知识点
    
    对话内容：{conversation}
    ```
  
  - **关键实体提取**：
    - 使用 NER 提取人名、地名、专业术语
    - 构建知识图谱索引

- [ ] 压缩策略配置
  - 可调参数：窗口大小、压缩阈值、保留轮数
  - A/B 测试不同策略效果

#### Task 3.3：智能检索增强
- [ ] 实现向量数据库（可选）
  - 使用 FAISS 或 Chroma
  - 存储历史问答对的 embedding
  - 相似问题检索（避免重复回答）

---

### Phase 4：大模型回复生成（2 天）

#### Task 4.1：回复生成服务
- [ ] 实现 `ReplyGenerator` 类
  ```python
  class ReplyGenerator:
      def __init__(self):
          self.model = "qwen-plus"
          self.system_prompt = """
          你是一位授课助手，负责回答学生在课堂上的提问。
          要求：
          1. 回答简洁明了，控制在 100 字以内
          2. 使用通俗易懂的语言
          3. 如果问题不清楚，礼貌地要求学生补充
          4. 结合上下文给出针对性回答
          """
      
      async def generate(self, question: str, context: str) -> str:
          # 调用大模型 API
          # 返回回复文本
  ```

- [ ] Prompt 优化
  - 添加课程主题上下文
  - 添加教师风格配置（严谨/轻松/幽默）
  - 支持自定义 Prompt 模板

#### Task 4.2：回复质量控制
- [ ] 实现回复过滤器
  - 长度检查（避免过长回复）
  - 敏感词过滤
  - 相关性检查（是否偏离主题）
  
- [ ] 回复缓存机制
  - 相似问题直接返回缓存答案
  - 减少 API 调用成本

---

### Phase 5：前端界面开发（3-4 天）

#### Task 5.1：项目搭建
- [ ] 初始化 React + TypeScript 项目
  ```bash
  npm create vite@latest frontend -- --template react-ts
  cd frontend
  npm install tailwindcss framer-motion recharts lucide-react
  ```

- [ ] 配置 Tailwind CSS
  - 自定义主题色（深蓝/紫色渐变）
  - 配置字体（JetBrains Mono）
  - 配置动画预设

#### Task 5.2：核心组件开发
- [ ] `AudioVisualizer` 组件
  - 实时音频波形显示
  - 使用 Canvas API 绘制
  - 音量指示器
  
- [ ] `ConversationPanel` 组件
  - 对话气泡（教师/学生/系统）
  - 角色头像与标识
  - 自动滚动到最新消息
  - 时间戳显示
  
- [ ] `StatusIndicator` 组件
  - 系统状态：空闲/监听中/识别中/生成中
  - 使用动画效果（脉冲/旋转）
  - 显示当前说话人
  
- [ ] `ControlPanel` 组件
  - 开始/停止监听按钮
  - 音频设备选择
  - 设置面板（压缩策略、模型选择）
  
- [ ] `CompressionMonitor` 组件（可选）
  - Token 使用量实时显示
  - 压缩进度条
  - 历史对话轮数统计

#### Task 5.3：UI/UX 优化
- [ ] 设计系统
  - 定义颜色变量（CSS Variables）
  - 统一间距、圆角、阴影
  - 响应式布局（支持不同屏幕尺寸）
  
- [ ] 动画效果
  - 消息进入动画（淡入 + 上滑）
  - 状态切换过渡
  - 加载骨架屏
  
- [ ] 交互细节
  - 悬停效果
  - 点击反馈
  - 错误提示（Toast）

---

### Phase 6：系统集成与测试（2-3 天）

#### Task 6.1：端到端集成
- [ ] 后端服务启动脚本
  ```python
  # main.py
  if __name__ == "__main__":
      # 启动 FastAPI 服务器
      # 初始化 ASR 连接
      # 启动后台压缩任务
      uvicorn.run(app, host="0.0.0.0", port=8000)
  ```

- [ ] 前后端联调
  - WebSocket 消息格式统一
  - 错误处理与重连
  - 性能监控埋点

#### Task 6.2：会议软件适配
- [ ] 腾讯会议音频捕获
  - 配置 BlackHole 为输出设备
  - 测试音频质量
  
- [ ] 飞书会议音频捕获
  - 同上配置
  - 测试多人对话场景
  
- [ ] 音频路由配置指南
  - 编写详细的设置文档
  - 提供截图说明

#### Task 6.3：测试与优化
- [ ] 功能测试
  - 单人对话测试
  - 多人对话测试
  - 长时间运行稳定性测试
  
- [ ] 性能测试
  - 端到端延迟测量（目标 < 1s）
  - 内存占用监控
  - CPU 使用率优化
  
- [ ] 压缩策略验证
  - 对比不同压缩策略的效果
  - 测试 token 节省率
  - 验证回复质量是否下降

---

### Phase 7：部署与文档（1-2 天）

#### Task 7.1：部署准备
- [ ] Docker 容器化（可选）
  - 编写 Dockerfile
  - Docker Compose 配置
  
- [ ] 环境变量管理
  - 创建 `.env.example`
  - 敏感信息加密存储

#### Task 7.2：文档编写
- [ ] README.md
  - 项目简介
  - 快速开始指南
  - 系统要求
  - 常见问题
  
- [ ] 用户手册
  - 安装步骤
  - 配置说明
  - 使用教程
  - 故障排查

---

## 技术难点与解决方案

### 难点 1：系统音频捕获
**问题**：macOS 默认不支持捕获系统音频  
**解决方案**：
- 安装 BlackHole 虚拟音频设备
- 使用"音频 MIDI 设置"创建多输出设备
- 配置会议软件输出到虚拟设备

### 难点 2：实时性保证
**问题**：语音识别 + 大模型推理延迟累加  
**解决方案**：
- 使用 WebSocket 减少连接开销
- ASR 采用流式识别（边说边转写）
- 大模型使用流式输出（SSE）
- 后台异步压缩，不阻塞主流程

### 难点 3：角色区分准确性
**问题**：纯语音内容难以区分说话人  
**解决方案**：
- 首次对话通过内容语义判断（教师通常先讲解，学生后提问）
- 提取简单声纹特征（音高、语速）辅助判断
- 允许用户手动标注纠正
- 积累数据后训练轻量级分类器

### 难点 4：上下文压缩质量
**问题**：压缩可能丢失关键信息  
**解决方案**：
- 分层存储策略，最近对话完整保留
- 使用大模型生成高质量摘要
- 保留所有学生问题（即使压缩）
- 提供"查看完整历史"功能

### 难点 5：多人对话场景
**问题**：多个学生同时提问  
**解决方案**：
- 实现提问队列，按时间顺序处理
- 显示"排队中"提示
- 支持教师手动选择优先回答的问题

---

## 性能指标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| 端到端延迟 | < 1.5s | 从学生说完到显示回复 |
| ASR 准确率 | > 95% | 人工标注对比 |
| 角色识别准确率 | > 90% | 统计错误率 |
| Token 压缩率 | > 60% | 压缩前后 token 对比 |
| 系统稳定性 | 连续运行 2 小时无崩溃 | 压力测试 |
| 内存占用 | < 500MB | 监控工具 |

---

## 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| API Key 失效 | 系统无法工作 | 实现多 Key 轮询，添加余额监控 |
| 网络不稳定 | 识别中断 | WebSocket 自动重连，本地缓存音频 |
| 大模型回复质量差 | 用户体验下降 | 添加回复评分机制，收集反馈优化 Prompt |
| 音频设备配置复杂 | 用户上手困难 | 提供详细图文教程，开发自动配置脚本 |
| 长时间运行内存泄漏 | 系统崩溃 | 定期清理缓存，设置内存上限 |

---

## 迭代计划

### v1.0（MVP）- 2 周
- ✅ 基础语音识别
- ✅ 简单角色判断（基于内容）
- ✅ 大模型回复
- ✅ 基础前端界面

### v1.1 - 1 周
- ✅ 上下文压缩
- ✅ 声纹辅助判断
- ✅ UI 优化

### v1.2 - 1 周
- ✅ 多人对话支持
- ✅ 历史记录导出
- ✅ 性能优化

### v2.0（未来）
- 🔮 语音合成（TTS）自动播报回复
- 🔮 知识库集成（RAG）
- 🔮 多语言支持
- 🔮 移动端适配

---

## 开发规范

### 代码风格
- Python：遵循 PEP 8，使用 Black 格式化
- TypeScript：使用 ESLint + Prettier
- 命名：驼峰命名（前端）、下划线命名（后端）

### Git 工作流
- 分支策略：`main`（生产）、`dev`（开发）、`feature/*`（功能）
- Commit 规范：`feat/fix/docs/style/refactor/test/chore: 描述`
- 代码审查：所有 PR 需至少一人审查

### 测试要求
- 单元测试覆盖率 > 70%
- 关键模块（ASR、压缩）需集成测试
- 上线前进行完整的端到端测试

---

## 资源清单

### API 服务
- ✅ 阿里云 DashScope（需更新有效 API Key）
- ✅ 通义千问大模型（qwen-plus/qwen-turbo）
- ✅ 阿里云 OSS（bucket: audio-input-data，区域：北京）

### 开发工具
- Python 3.9+
- Node.js 18+
- VS Code / PyCharm
- Postman（API 测试）

### 第三方库
- 后端：dashscope, pyaudio, fastapi, uvicorn, websockets, tiktoken
- 前端：react, typescript, tailwindcss, framer-motion, recharts, lucide-react

---

## 总结

本项目是一个复杂的实时系统，核心挑战在于：
1. **低延迟**：需要优化每个环节的处理速度
2. **高准确性**：ASR 和角色识别需要达到实用水平
3. **智能压缩**：在保证回复质量的前提下控制 token 消耗
4. **用户体验**：界面美观、操作简单、反馈及时

建议按照 Phase 1 → Phase 7 的顺序逐步实现，每个 Phase 完成后进行测试验证，确保质量后再进入下一阶段。

预计总开发时间：**3-4 周**（单人全职开发）

---

## Phase 8: 优化与增强功能（进行中）

### Task 8.1: 性能优化
- [ ] 添加请求缓存机制
- [ ] 优化 Token 计数性能
- [ ] 添加连接池管理
- [ ] 实现请求限流

### Task 8.2: 错误处理增强
- [ ] 统一错误处理中间件
- [ ] 详细的错误日志
- [ ] 错误重试机制
- [ ] 优雅降级策略

### Task 8.3: 监控与日志
- [ ] 结构化日志系统
- [ ] 性能监控指标
- [ ] 请求追踪（Trace ID）
- [ ] 健康检查增强

### Task 8.4: 配置优化
- [ ] 支持多环境配置
- [ ] 配置热更新
- [ ] 敏感信息加密
- [ ] 配置验证

### Task 8.5: 测试增强
- [ ] 添加性能测试
- [ ] 添加压力测试
- [ ] 模拟真实场景测试
- [ ] 测试覆盖率提升到 80%+

---

**最后更新**：2026-02-16  
**文档版本**：v1.1

