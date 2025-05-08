import { useState, useEffect, useRef } from 'react';
import ChatInput from './ChatInput';
import { websocketService, AgentResponse } from '../services/websocketService';
import { ChatMessage as IChatMessage, useChatHistory } from '../contexts/ChatHistoryContext';
import { fileService } from '../services/fileService';
import { useSettings } from '../contexts/SettingsContext';
import ChatMessage from './ChatMessage';
import { DotsSpinner } from './DotsSpinner/DotsSpinner';

// Interface matching the one added in ChatInput
interface AttachedFile {
  id: string;
  name: string;
}

const formatExecutionTime = (seconds: string): string => {
  const minutes = Math.floor(parseInt(seconds) / 60);
  const remainingSeconds = Math.floor(parseInt(seconds) % 60);
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
};

const ChatArea = () => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [requestId, setRequestId] = useState<string>('');
  const { messages, addMessage } = useChatHistory();
  const { settings } = useSettings();
  const [uploadedFiles, setUploadedFiles] = useState<Record<string, { name: string; type: string; size: number }>>({});

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleFileUpload = async (file: File): Promise<AttachedFile> => {
    setIsUploading(true);
    try {
      const fileId = await fileService.uploadFile(file);
      // Store file metadata
      setUploadedFiles(prev => ({
        ...prev,
        [fileId]: {
          name: file.name,
          type: file.type,
          size: file.size
        }
      }));
      // Return object with id and name
      return { id: fileId, name: file.name };
    } catch (error) {
      throw error;
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = (content: string, files?: string[]) => {
    // Add user message
    const newUserMessage: IChatMessage = {
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
      }),
      agents_trace: [],
      files: files?.map(fileId => ({
        id: fileId,
        session_id: sessionId || '',
        request_id: requestId || '',
        original_name: uploadedFiles[fileId]?.name || fileId,
        mimetype: uploadedFiles[fileId]?.type || '',
        internal_id: fileId,
        internal_name: fileId,
        from_agent: false
      }))
    };

    const messageToSend = {
      message: content,
      llm_name: settings.model?.name,
      ...(files && { files: files }),
    };

    addMessage(newUserMessage);
    setIsWaitingForResponse(true);
    websocketService.sendMessage(messageToSend);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const handleWebSocketMessage = (response: AgentResponse) => {

      if (response.type === 'agent_response') {
        setIsWaitingForResponse(false);
        setSessionId(response.response.session_id);
        setRequestId(response.response.request_id);
        const newMessage: IChatMessage = {
          id: response.response.request_id || Date.now().toString(),
          content: response.response.response.response,
          isUser: false,
          timestamp: new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
          }),
          executionTime: response.response.execution_time.toString(),
          sessionId: response.response.session_id,
          requestId: response.response.request_id,
          isError: !response.response.response.is_success,
          agents_trace: response.response.response.agents_trace,
          files: response.response.files
        };
        addMessage(newMessage)
      }
    };

    websocketService.addMessageHandler(handleWebSocketMessage);

    return () => {
      websocketService.removeMessageHandler(handleWebSocketMessage);
    };
  }, [messages.length, addMessage]);

  return (
    <div className="flex flex-col h-full relative">
      {/* Chat messages area */}
      <div className={`flex-1 overflow-y-auto p-4 space-y-2 ${messages.length === 0 ? 'flex items-center justify-center' : ''}`} style={{ 
        height: 'calc(100vh - 30vh)', // 100vh - input area height
        overflowY: 'auto'
      }}>
        {messages.length !== 0 && (
          messages.map(message => (
            <ChatMessage 
              key={message.id} 
              id={message.id}
              content={message.content} 
              isUser={message.isUser} 
              timestamp={message.timestamp}
              sessionId={message.sessionId}
              requestId={message.requestId}
              executionTime={message.executionTime ? formatExecutionTime(message.executionTime) : undefined}
              isError={message.isError}
              agents_trace={message.agents_trace}
              files={message.files}
            />
          ))
        )}
        {isWaitingForResponse && (
          <div className="flex justify-start py-4">
            <DotsSpinner />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      {/* Chat input area */}
      <div className={`flex-none ${messages.length === 0 ? 'w-full absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2' : ''}`}>
        {messages.length === 0 && (
          <div className="text-center text-gray-500 text-2xl">
            What can I do for you today?
          </div>
        )}
        <ChatInput 
          onSendMessage={handleSendMessage} 
          isUploading={isUploading}
          onFileUpload={handleFileUpload}
        />
      </div>
    </div>
  );
};

export default ChatArea;
