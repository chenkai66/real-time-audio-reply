/**
 * WebSocket 服务
 * 管理与后端的 WebSocket 连接
 */

export type MessageType = 
  | 'connected'
  | 'status'
  | 'role_identified'
  | 'reply'
  | 'stats'
  | 'error'
  | 'pong';

export interface WebSocketMessage {
  type: MessageType;
  [key: string]: any;
}

export type MessageHandler = (message: WebSocketMessage) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageHandlers: Set<MessageHandler> = new Set();
  private isManualClose = false;

  constructor(url: string) {
    this.url = url;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);
        this.isManualClose = false;

        this.ws.onopen = () => {
          console.log('WebSocket 连接成功');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.messageHandlers.forEach(handler => handler(message));
          } catch (error) {
            console.error('解析消息失败:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket 错误:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket 连接关闭');
          if (!this.isManualClose) {
            this.attemptReconnect();
          }
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect().catch(console.error);
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('达到最大重连次数');
    }
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket 未连接');
    }
  }

  onMessage(handler: MessageHandler) {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  disconnect() {
    this.isManualClose = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  // 发送心跳
  sendPing() {
    this.send({ type: 'ping' });
  }

  // 发送转写文本
  sendTranscript(text: string, isFinal: boolean = false) {
    this.send({
      type: 'transcript',
      text,
      is_final: isFinal
    });
  }
}

// 创建全局实例
const wsUrl = `ws://${window.location.hostname}:8000/ws/audio`;
export const websocketService = new WebSocketService(wsUrl);

