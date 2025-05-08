import type { FC, ReactNode } from 'react';
import { createContext, useContext, useState, useCallback } from 'react';
import { AgentPlan } from '../services/websocketService';

export interface ChatMessage {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: string;
  executionTime?: string;
  sessionId?: string;
  requestId?: string;
  isError?: boolean;
  agents_trace: any[];
  agentsPlan?: AgentPlan[];
  files?: Array<{
    id: string;
    session_id: string;
    request_id: string;
    original_name: string;
    mimetype: string;
    internal_id: string;
    internal_name: string;
    from_agent: boolean;
  }>;
}

interface ChatHistoryContextType {
  messages: ChatMessage[];
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
}

const ChatHistoryContext = createContext<ChatHistoryContextType | undefined>(undefined);

export const ChatHistoryProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages(prevMessages => [...prevMessages, message]);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    localStorage.removeItem('chatHistory');
  }, []);

  return (
    <ChatHistoryContext.Provider value={{ messages, addMessage, clearMessages }}>
      {children}
    </ChatHistoryContext.Provider>
  );
};

export const useChatHistory = () => {
  const context = useContext(ChatHistoryContext);
  if (context === undefined) {
    throw new Error('useChatHistory must be used within a ChatHistoryProvider');
  }
  return context;
}; 