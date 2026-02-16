import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Mic, Wifi, WifiOff } from 'lucide-react';
import { AudioVisualizer } from './components/AudioVisualizer';
import { ConversationPanel, Message } from './components/ConversationPanel';
import { ControlPanel } from './components/ControlPanel';
import { StatsDisplay } from './components/StatsDisplay';
import { StatusIndicator, Status } from './components/StatusIndicator';
import { useWebSocket } from './hooks/useWebSocket';
import { apiService } from './services/api';

function App() {
  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState<Status>('idle');
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [stats, setStats] = useState({
    total_turns: 0,
    total_tokens: 0,
    l1_size: 0,
    l2_size: 0,
    l1_tokens: 0,
    l2_tokens: 0,
  });

  const { isConnected, messages: wsMessages, sendTranscript } = useWebSocket();

  // 处理 WebSocket 消息
  useEffect(() => {
    if (wsMessages.length === 0) return;

    const lastMessage = wsMessages[wsMessages.length - 1];

    switch (lastMessage.type) {
      case 'connected':
        setStatusMessage('已连接到服务器');
        break;

      case 'status':
        if (lastMessage.status === 'processing') {
          setStatus('processing');
          setStatusMessage('正在识别角色...');
        } else if (lastMessage.status === 'generating') {
          setStatus('generating');
          setStatusMessage('正在生成回复...');
        }
        break;

      case 'role_identified':
        const newMessage: Message = {
          id: Date.now().toString(),
          role: lastMessage.role,
          text: lastMessage.text,
          timestamp: lastMessage.timestamp,
        };
        setMessages(prev => [...prev, newMessage]);
        setStatus(isListening ? 'listening' : 'idle');
        break;

      case 'reply':
        const replyMessage: Message = {
          id: Date.now().toString(),
          role: 'system',
          text: lastMessage.text,
          timestamp: lastMessage.timestamp,
        };
        setMessages(prev => [...prev, replyMessage]);
        setStatus(isListening ? 'listening' : 'idle');
        setStatusMessage('回复已生成');
        break;

      case 'stats':
        setStats(lastMessage.data);
        break;

      case 'error':
        setStatus('error');
        setStatusMessage(lastMessage.message);
        setTimeout(() => {
          setStatus(isListening ? 'listening' : 'idle');
        }, 3000);
        break;
    }
  }, [wsMessages, isListening]);

  // 定期更新统计信息
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const data = await apiService.getStats();
        setStats(data.conversation);
      } catch (error) {
        console.error('获取统计信息失败:', error);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleToggleListening = () => {
    setIsListening(!isListening);
    setStatus(!isListening ? 'listening' : 'idle');
    setStatusMessage(!isListening ? '正在监听...' : '');
  };

  const handleClear = async () => {
    try {
      await apiService.clearConversation();
      setMessages([]);
      setStats({
        total_turns: 0,
        total_tokens: 0,
        l1_size: 0,
        l2_size: 0,
        l1_tokens: 0,
        l2_tokens: 0,
      });
      setStatusMessage('历史已清空');
    } catch (error) {
      console.error('清空失败:', error);
      setStatus('error');
      setStatusMessage('清空失败');
    }
  };

  // 模拟测试功能
  const handleTest = () => {
    const testMessages = [
      { role: 'teacher' as const, text: '今天我们学习 Python 的基础语法' },
      { role: 'student' as const, text: '老师，什么是变量？' },
      { role: 'system' as const, text: '变量是用来存储数据的容器。在 Python 中，你可以使用等号来给变量赋值。' },
    ];

    testMessages.forEach((msg, index) => {
      setTimeout(() => {
        sendTranscript(msg.text, true);
      }, index * 2000);
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent-500/10 rounded-full blur-3xl" />
      </div>

      {/* 主内容 */}
      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* 头部 */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
                <Mic className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold gradient-text">
                  实时语音识别与智能回复系统
                </h1>
                <p className="text-gray-400 text-sm mt-1">
                  AI 驱动的在线授课助手
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {isConnected ? (
                <>
                  <Wifi className="w-5 h-5 text-green-400" />
                  <span className="text-sm text-green-400">已连接</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-5 h-5 text-red-400" />
                  <span className="text-sm text-red-400">未连接</span>
                </>
              )}
            </div>
          </div>
        </motion.header>

        {/* 状态指示器 */}
        <StatusIndicator status={status} message={statusMessage} />

        {/* 主要内容区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          {/* 左侧 - 音频可视化和对话 */}
          <div className="lg:col-span-2 space-y-6">
            <AudioVisualizer isActive={isListening} />
            <ConversationPanel messages={messages} />
          </div>

          {/* 右侧 - 控制和统计 */}
          <div className="space-y-6">
            <ControlPanel
              isListening={isListening}
              onToggleListening={handleToggleListening}
              onClear={handleClear}
            />
            <StatsDisplay stats={stats} />

            {/* 测试按钮 */}
            {process.env.NODE_ENV === 'development' && (
              <button
                onClick={handleTest}
                className="w-full btn-secondary text-sm"
              >
                🧪 测试模式
              </button>
            )}
          </div>
        </div>

        {/* 页脚 */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-12 text-center text-gray-500 text-sm"
        >
          <p>© 2026 实时语音识别系统 · 基于阿里云 DashScope 和通义千问</p>
        </motion.footer>
      </div>
    </div>
  );
}

export default App;

