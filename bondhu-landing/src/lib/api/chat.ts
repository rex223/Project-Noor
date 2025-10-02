/**
 * Chat API Client for Bondhu AI
 * Handles communication with the FastAPI backend for chat functionality
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  id?: string;
}

export interface ChatRequest {
  user_id: string;
  message: string;
}

export interface ChatResponse {
  response: string;
  has_personality_context: boolean;
  timestamp: string;
  message_id?: string;
}

export interface ChatHistoryItem {
  id: string;
  message: string;
  response: string;
  has_personality_context: boolean;
  created_at: string;
}

export interface ChatHistoryResponse {
  messages: ChatHistoryItem[];
  total: number;
  user_id: string;
}

/**
 * Chat API service
 */
export const chatApi = {
  /**
   * Send a chat message and get AI response
   */
  sendMessage: async (userId: string, message: string): Promise<ChatResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          message: message,
        } as ChatRequest),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: ChatResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Chat API Error:', error);
      throw error;
    }
  },

  /**
   * Get chat history for a user
   */
  getChatHistory: async (
    userId: string,
    limit: number = 20,
    offset: number = 0
  ): Promise<ChatHistoryResponse> => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/chat/history/${userId}?limit=${limit}&offset=${offset}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch chat history: ${response.statusText}`);
      }

      const data: ChatHistoryResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Chat History API Error:', error);
      throw error;
    }
  },

  /**
   * Clear all chat history for a user
   */
  clearChatHistory: async (userId: string): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/history/${userId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to clear chat history: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Clear Chat History API Error:', error);
      throw error;
    }
  },

  /**
   * Search chat history for a user
   */
  searchChatHistory: async (
    userId: string,
    query: string,
    limit: number = 20
  ): Promise<ChatHistoryResponse> => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/chat/search/${userId}?q=${encodeURIComponent(query)}&limit=${limit}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to search chat history: ${response.statusText}`);
      }

      const data: ChatHistoryResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Search Chat History API Error:', error);
      throw error;
    }
  },

  /**
   * Check chat service health
   */
  healthCheck: async (): Promise<{ status: string; service: string; model: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Chat service unhealthy');
      }

      return await response.json();
    } catch (error) {
      console.error('Chat Health Check Error:', error);
      throw error;
    }
  },

  /**
   * Convert ChatHistoryItem to ChatMessage format
   */
  convertHistoryToMessages: (history: ChatHistoryItem[]): ChatMessage[] => {
    const messages: ChatMessage[] = [];

    history.forEach((item) => {
      // User message
      messages.push({
        role: 'user',
        content: item.message,
        timestamp: new Date(item.created_at),
        id: `${item.id}-user`,
      });

      // Assistant response
      messages.push({
        role: 'assistant',
        content: item.response,
        timestamp: new Date(item.created_at),
        id: `${item.id}-assistant`,
      });
    });

    return messages;
  },
};

/**
 * Error types for better error handling
 */
export class ChatAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'ChatAPIError';
  }
}
