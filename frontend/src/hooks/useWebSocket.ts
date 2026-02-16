import { useState, useEffect } from 'react';
import { websocketService, WebSocketMessage } from '../services/websocket';

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const connect = async () => {
      try {
        await websocketService.connect();
        setIsConnected(true);
        setError(null);
      } catch (err) {
        setError('连接失败');
        setIsConnected(false);
      }
    };

    connect();

    const unsubscribe = websocketService.onMessage((message) => {
      setMessages(prev => [...prev, message]);
      
      if (message.type === 'error') {
        setError(message.message);
      }
    });

    // 心跳
    const pingInterval = setInterval(() => {
      if (websocketService.isConnected()) {
        websocketService.sendPing();
      }
    }, 30000);

    return () => {
      unsubscribe();
      clearInterval(pingInterval);
      websocketService.disconnect();
    };
  }, []);

  const sendTranscript = (text: string, isFinal: boolean = false) => {
    websocketService.sendTranscript(text, isFinal);
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return {
    isConnected,
    messages,
    error,
    sendTranscript,
    clearMessages,
  };
};

