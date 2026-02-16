/**
 * API 服务
 * 处理 REST API 请求
 */

const API_BASE_URL = 'http://localhost:8000';

export interface ConversationStats {
  total_turns: number;
  total_tokens: number;
  l1_size: number;
  l2_size: number;
  l3_size: number;
  l1_tokens: number;
  l2_tokens: number;
}

export interface SystemStats {
  conversation: ConversationStats;
  connections: number;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API 请求失败: ${response.statusText}`);
    }

    return response.json();
  }

  async getStats(): Promise<SystemStats> {
    return this.request<SystemStats>('/api/stats');
  }

  async clearConversation(): Promise<{ message: string }> {
    return this.request('/api/conversation/clear', {
      method: 'POST',
    });
  }

  async getConversationHistory(): Promise<any> {
    return this.request('/api/conversation/history');
  }

  async testGenerate(question: string, context?: string): Promise<{ reply: string }> {
    return this.request('/api/test/generate', {
      method: 'POST',
      body: JSON.stringify({ question, context }),
    });
  }

  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request('/health');
  }
}

export const apiService = new ApiService();

