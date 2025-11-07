'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { chatAPI } from '@/lib/api-client';
import type { ChatMessageResponse, RelevantContext } from '@/lib/api-client';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  relevantContext?: RelevantContext[];
  timestamp: Date;
}

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Index resume when component mounts
    indexResumeData();

    // Add initial greeting
    setMessages([
      {
        role: 'assistant',
        content: "Hi! I'm your AI resume optimization assistant. I can help you improve your resume, answer questions about STAR framework, suggest better phrasing, and more. What would you like to know?",
        timestamp: new Date(),
      },
    ]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const indexResumeData = async () => {
    setIsIndexing(true);
    try {
      const parsedResumeStr = sessionStorage.getItem('parsed_resume');
      if (!parsedResumeStr) {
        console.warn('No resume data to index');
        return;
      }

      const parsedResume = JSON.parse(parsedResumeStr);
      await chatAPI.indexResume({ resume_data: parsedResume });
      console.log('Resume indexed successfully for RAG');
    } catch (err: any) {
      console.error('Failed to index resume:', err);
      // Don't show error to user, just log it
    } finally {
      setIsIndexing(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isSending) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsSending(true);
    setError(null);

    try {
      // Get resume version ID (can be empty for now)
      const resumeVersionId = sessionStorage.getItem('resume_version_id') || 'default';

      const response = await chatAPI.sendMessage({
        resume_version_id: resumeVersionId,
        message: inputMessage,
        chat_session_id: sessionId || undefined,
      });

      // Update session ID
      if (!sessionId) {
        setSessionId(response.session_id);
      }

      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.reply,
        relevantContext: response.relevant_context,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      console.error('Chat error:', err);

      // Add error message
      const errorMessage: Message = {
        role: 'assistant',
        content: "I'm sorry, I encountered an error. Please try again or rephrase your question.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const suggestedQuestions = [
    "How can I improve my bullet points using STAR framework?",
    "What keywords should I include from the job description?",
    "Can you suggest quantifiable metrics for my experience?",
    "How do I make my resume more ATS-friendly?",
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 p-8">
      <div className="max-w-6xl mx-auto h-[calc(100vh-4rem)] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 bg-white bg-opacity-20 text-white px-6 py-3 rounded-full hover:bg-opacity-30 transition-all backdrop-blur-sm font-medium"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span>Back</span>
          </button>
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white">AI Resume Assistant</h1>
            <p className="text-white text-opacity-90 mt-1">
              {isIndexing ? 'Indexing your resume...' : 'Powered by RAG + GPT-4'}
            </p>
          </div>
          <div className="w-32"></div>
        </div>

        {/* Chat Container */}
        <div className="flex-1 bg-white rounded-3xl shadow-2xl flex flex-col overflow-hidden">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message, idx) => (
              <MessageBubble key={idx} message={message} />
            ))}

            {isSending && (
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="flex-1 bg-gray-100 rounded-2xl p-4">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Questions (only show at start) */}
          {messages.length === 1 && (
            <div className="px-6 pb-4">
              <p className="text-sm text-gray-500 mb-2 font-medium">Suggested questions:</p>
              <div className="grid grid-cols-2 gap-2">
                {suggestedQuestions.map((question, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputMessage(question)}
                    className="text-left text-sm bg-indigo-50 hover:bg-indigo-100 text-indigo-700 px-4 py-2 rounded-lg transition"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="px-6 pb-2">
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm">
                {error}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="border-t border-gray-200 p-6">
            <div className="flex gap-3">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about resume optimization..."
                className="flex-1 border-2 border-gray-300 rounded-2xl px-4 py-3 focus:border-indigo-500 focus:outline-none resize-none"
                rows={2}
                disabled={isSending || isIndexing}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isSending || isIndexing}
                className={`px-6 py-3 rounded-2xl font-bold transition-all flex items-center gap-2 ${
                  !inputMessage.trim() || isSending || isIndexing
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:shadow-lg hover:scale-105'
                }`}
              >
                {isSending ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Sending...
                  </>
                ) : (
                  <>
                    Send
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  </>
                )}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">Press Enter to send, Shift+Enter for new line</p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Message Bubble Component
interface MessageBubbleProps {
  message: Message;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div
        className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser
            ? 'bg-gradient-to-br from-green-400 to-blue-500'
            : 'bg-gradient-to-br from-indigo-500 to-purple-600'
        }`}
      >
        {isUser ? (
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        ) : (
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-[80%] ${isUser ? 'items-end' : ''}`}>
        <div
          className={`rounded-2xl p-4 ${
            isUser
              ? 'bg-gradient-to-br from-green-500 to-blue-600 text-white'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Relevant Context (only for assistant messages with context) */}
        {!isUser && message.relevantContext && message.relevantContext.length > 0 && (
          <div className="mt-2 ml-4">
            <p className="text-xs text-gray-500 font-medium mb-2">📚 Referenced from your resume:</p>
            <div className="space-y-2">
              {message.relevantContext.map((context, idx) => (
                <div key={idx} className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-blue-900">{context.company}</span>
                    <span className="text-gray-400">•</span>
                    <span className="text-blue-700">{context.title}</span>
                    <span className="ml-auto text-xs bg-blue-200 text-blue-800 px-2 py-0.5 rounded-full">
                      {(context.relevance_score * 100).toFixed(0)}% match
                    </span>
                  </div>
                  <p className="text-gray-700 text-xs">{context.bullet_point}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <p className="text-xs text-gray-400 mt-1 ml-4">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
}
