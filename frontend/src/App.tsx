import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Mic, Wifi, WifiOff } from 'lucide-react';
import { AudioVisualizer } from './components/AudioVisualizer';
import { ConversationPanel, Message } from './components/ConversationPanel';
import { ControlPanel } from './components/ControlPanel';
import { StatsDisplay } from './components/StatsDisplay';
import { StatusIndicator, Status } from './components/StatusIndicator';
import { apiService } from './services/api';
import { audioCaptureService, AudioSource } from './services/audioCapture';
import { wsService } from './services/websocket';

function App() {
  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState<Status>('idle');
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [audioSource, setAudioSource] = useState<AudioSource>('microphone');
  const [stats, setStats] = useState({
    total_turns: 0,
    total_tokens: 0,
    l1_size: 0,
    l2_size: 0,
    l1_tokens: 0,
    l2_tokens: 0,
  });

  // 初始化 WebSocket 连接
  useEffect(() => {
    const initWebSocket = async () => {
      try {
        await wsService.connect();
        setIsConnected(true);
        setStatusMessage('已连接到服务器');

        // 注册消息处理器
        wsService.on('transcript', (message) => {
          const newMessage: Message = {
            id: Date.now().toString(),
            role: message.role || 'student',
            text: message.text || '',
            timestamp: message.timestamp || new Date().toISOString(),
          };
          setMessages(prev => [...prev, newMessage]);
          setStatus(isListening ? 'listening' : 'idle');
        });

        wsService.on('transcript_partial', (message) => {
          // 中间识别结果，显示在状态栏
          setStatusMessage(`识别中: ${message.text}`);
        });

        wsService.on('reply', (message) => {
          const replyMessage: Message = {
            id: Date.now().toString(),
            role: 'system',
            text: message.text || '',
            timestamp: message.timestamp || new Date().toISOString(),
          };
          setMessages(prev => [...prev, replyMessage]);
          setStatus(isListening ? 'listening' : 'idle');
          setStatusMessage('回复已生成');
        });

        wsService.on('status', (message) => {
          if (message.status === 'processing') {
            setStatus('processing');
            setStatusMessage('正在识别角色...');
          } else if (message.status === 'generating') {
            setStatus('generating');
            setStatusMessage('正在生成回复...');
          }
        });

        wsService.on('error', (message) => {
          setStatus('error');
          setStatusMessage(message.message || '发生错误');
          setTimeout(() => {
            setStatus(isListening ? 'listening' : 'idle');
          }, 3000);
        });

      } catch (error) {
        console.error('WebSocket 连接失败:', error);
        setIsConnected(false);
        setStatusMessage('连接失败');
      }
    };

    initWebSocket();

    return () => {
      wsService.disconnect();
    };
  }, []);

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

  // 处理开始/停止监听
  const handleToggleListening = async () => {
    if (!isListening) {
      // 开始监听
      try {
        // 检查浏览器支持
        if (!audioCaptureService.constructor.isSupported()) {
          setStatus('error');
          setStatusMessage('浏览器不支持音频采集');
          return;
        }

        // 检查 WebSocket 连接
        if (!wsService.isConnected()) {
          setStatusMessage('正在连接服务器...');
          await wsService.connect();
        }

        setStatus('listening');
        setStatusMessage('正在启动音频采集...');

        // 通知后端开始监听
        wsService.send({ type: 'start_listening' });

        // 开始音频采集
        await audioCaptureService.startCapture(audioSource, (audioData) => {
          // 发送音频数据到后端
          wsService.sendAudio(audioData);
        });

        setIsListening(true);
        setStatusMessage('正在监听...');
        console.log('✅ 开始监听');
      } catch (error) {
        console.error('启动监听失败:', error);
        setStatus('error');
        setStatusMessage(error instanceof Error ? error.message : '启动失败');
        setTimeout(() => setStatus('idle'), 3000);
      }
    } else {
      // 停止监听
      
      // 通知后端停止监听
      wsService.send({ type: 'stop_listening' });
      
      // 停止音频采集
      audioCaptureService.stopCapture();
      
      setIsListening(false);
      setStatus('idle');
      setStatusMessage('');
      console.log('✅ 停止监听');
    }
  };

  // 清空对话
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

  // 切换音频源
  const handleAudioSourceChange = (source: AudioSource) => {
    if (isListening) {
      setStatusMessage('请先停止监听');
      return;
    }
    setAudioSource(source);
    setStatusMessage(`已切换到: ${source === 'microphone' ? '麦克风' : source === 'system' ? '系统音频' : '麦克风+系统音频'}`);
  };

  // 测试功能
  const handleTest = () => {
    const testMessages = [
      { role: 'teacher' as const, text: '今天我们学习 Python 的基础语法' },
      { role: 'student' as const, text: '老师，什么是变量？' },
      { role: 'system' as const, text: '变量是用来存储数据的容器。在 Python 中，你可以使用等号来给变量赋值。' },
    ];

    testMessages.forEach((msg, index) => {
      setTimeout(() => {
        wsService.sendText(msg.text, msg.role);
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

            {/* 音频源选择 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card p-4"
            >
              <h3 className="text-sm font-semibold text-gray-300 mb-3">音频源</h3>
              <div className="space-y-2">
                <button
                  onClick={() => handleAudioSourceChange('microphone')}
                  disabled={isListening}
                  className={`w-full px-3 py-2 rounded-lg text-sm transition-colors ${
                    audioSource === 'microphone'
                      ? 'bg-primary-500 text-white'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  } ${isListening ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  🎤 麦克风
                </button>
                <button
                  onClick={() => handleAudioSourceChange('system')}
                  disabled={isListening}
                  className={`w-full px-3 py-2 rounded-lg text-sm transition-colors ${
                    audioSource === 'system'
                      ? 'bg-primary-500 text-white'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  } ${isListening ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  🔊 系统音频
                </button>
                <button
                  onClick={() => handleAudioSourceChange('both')}
                  disabled={isListening}
                  className={`w-full px-3 py-2 rounded-lg text-sm transition-colors ${
                    audioSource === 'both'
                      ? 'bg-primary-500 text-white'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  } ${isListening ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  🎧 麦克风 + 系统音频
                </button>
              </div>
            </motion.div>

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

