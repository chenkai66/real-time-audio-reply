/**
 * WebSocket 服务 - 增强版
 * 支持音频数据传输和实时通信
 */

export interface WebSocketMessage {
  type: 'audio' | 'transcript' | 'reply' | 'status' | 'error' | 'connected' | 'pong';
  data?: any;
  text?: string;
  role?: string;
  timestamp?: string;
  status?: string;
  message?: string;
}

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, (data: any) => void> = new Map();
  private isConnecting = false;

  /**
   * 连接到 WebSocket 服务器
   */
  connect(userId: string = 'default'): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        console.log('WebSocket 已连接');
        resolve();
        return;
      }

      if (this.isConnecting) {
        console.log('WebSocket 正在连接中...');
        return;
      }

      this.isConnecting = true;
      const url = `ws://localhost:8000/ws/${userId}`;
      
      try {
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
          console.log('✅ WebSocket 连接成功');
          this.reconnectAttempts = 0;
          this.isConnecting = false;
          this.startHeartbeat();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('解析消息失败:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket 错误:', error);
          this.isConnecting = false;
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket 连接关闭');
          this.isConnecting = false;
          this.stopHeartbeat();
          this.reconnect(userId);
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * 重新连接
   */
  private reconnect(userId: string): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ WebSocket 重连失败，已达到最大重试次数');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * this.reconnectAttempts;

    console.log(`⏳ ${delay}ms 后尝试重连... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      this.connect(userId).catch(error => {
        console.error('重连失败:', error);
      });
    }, delay);
  }

  /**
   * 启动心跳
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.send({ type: 'ping' });
    }, 30000); // 30秒心跳
  }

  /**
   * 停止心跳
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * 发送消息
   */
  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket 未连接，无法发送消息');
    }
  }

  /**
   * 发送音频数据
   */
  sendAudio(audioData: Int16Array): void {
    this.send({
      type: 'audio',
      data: Array.from(audioData), // 转换为普通数组以便 JSON 序列化
    });
  }

  /**
   * 发送文本（用于测试）
   */
  sendText(text: string, role: string = 'student'): void {
    this.send({
      type: 'transcript',
      text,
      role,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(message: WebSocketMessage): void {
    // 调用注册的处理器
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      handler(message);
    }

    // 默认处理
    switch (message.type) {
      case 'connected':
        console.log('✅ 服务器确认连接');
        break;

      case 'pong':
        // 心跳响应，不需要处理
        break;

      case 'transcript':
        console.log('📝 识别结果:', message.text);
        break;

      case 'reply':
        console.log('💬 AI 回复:', message.text);
        break;

      case 'status':
        console.log('📊 状态更新:', message.status);
        break;

      case 'error':
        console.error('❌ 错误:', message.message);
        break;

      default:
        console.log('收到消息:', message);
    }
  }

  /**
   * 注册消息处理器
   */
  on(type: string, handler: (data: any) => void): void {
    this.messageHandlers.set(type, handler);
  }

  /**
   * 移除消息处理器
   */
  off(type: string): void {
    this.messageHandlers.delete(type);
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.reconnectAttempts = this.maxReconnectAttempts; // 阻止自动重连
    console.log('✅ WebSocket 已断开');
  }

  /**
   * 获取连接状态
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * 获取连接状态描述
   */
  getStatus(): string {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'unknown';
    }
  }
}

// 导出单例
export const wsService = new WebSocketService();
