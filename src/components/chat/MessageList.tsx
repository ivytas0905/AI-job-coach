// src/components/chat/MessageList.tsx
import React from 'react';
import { User, Sparkles, FileText, Code2, Clock, MessageSquare } from 'lucide-react';
import { Message, SuggestionCard, HistoryItem } from '../../types';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  onArtifactOpen: (data: {title: string, content: string, lang: string}) => void;
  onCardClick: (prompt: string) => void;
  cards: SuggestionCard[];
  recentHistory: HistoryItem[];
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
}

export default function MessageList({ 
  messages, isLoading, onArtifactOpen, onCardClick, cards, recentHistory, messagesEndRef 
}: MessageListProps) {
  
  return (
    <div className="flex-1 overflow-y-auto py-4">
      {/* Welcome screen - centered layout when only one message exists */}
      {messages.length === 1 ? (
        <div className="min-h-full flex items-center justify-center px-4 md:px-8">
          {/* Fixed max-width container */}
          <div className="w-full max-w-3xl">
            {/* Avatar + message with left offset for avatar */}
            <div className="flex gap-4 items-start -ml-12">
              {/* Avatar */}
              <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-indigo-600 text-white">
                <Sparkles size={16} />
              </div>
              
              {/* Content container */}
              <div className="flex-1 space-y-6">
                {/* Welcome message bubble */}
                <div className="px-4 py-3 rounded-2xl text-[15px] leading-relaxed shadow-sm bg-white border border-gray-100 text-gray-800">
                  <div className="whitespace-pre-wrap">{messages[0].content}</div>
                </div>

                {/* Cards & History - Show only when there is 1 message (Welcome msg) */}
                {!isLoading && (
                  <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {/* Suggestion cards grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                      {cards.map((card, index) => (
                        <button 
                          key={index} 
                          onClick={() => onCardClick(card.prompt)} 
                          className="flex flex-col items-start p-5 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 hover:border-indigo-300 hover:shadow-lg hover:-translate-y-1 transition-all text-left group h-full"
                        >
                          <div className="p-3 bg-gray-100 rounded-xl group-hover:bg-white group-hover:shadow-sm transition-all mb-4">
                            {card.icon}
                          </div>
                          <h3 className="font-semibold text-gray-800 mb-2">{card.title}</h3>
                          <p className="text-sm text-gray-500 leading-relaxed">{card.desc}</p>
                        </button>
                      ))}
                    </div>

                    {/* Recent conversation history */}
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-sm font-medium text-gray-500 px-1">
                        <Clock size={16} /><span>Recent</span>
                      </div>
                      <div className="space-y-2">
                        {recentHistory.slice(0, 3).map((item) => (
                          <button 
                            key={item.id} 
                            className="w-full text-left flex items-center justify-between px-4 py-3 hover:bg-gray-50 rounded-lg transition-colors group"
                          >
                            <div className="flex items-center gap-3">
                              <MessageSquare size={18} className="text-gray-400 group-hover:text-indigo-600 transition-colors" />
                              <span className="text-gray-700 text-sm font-medium group-hover:text-gray-900">{item.title}</span>
                            </div>
                            <span className="text-xs text-gray-400">{item.date}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : (
        // Normal conversation mode - messages list
        <div className="px-4 md:px-8 space-y-6">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              {/* Message avatar */}
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${msg.role === 'ai' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-600'}`}>
                {msg.role === 'ai' ? <Sparkles size={16} /> : <User size={16} />}
              </div>

              {/* Message content */}
              <div className={`flex flex-col max-w-[85%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`px-4 py-3 rounded-2xl text-[15px] leading-relaxed shadow-sm ${
                  msg.role === 'user' ? 'bg-gray-100 text-gray-800 rounded-tr-sm' : 'bg-white border border-gray-100 text-gray-800 pl-4 pt-3'
                }`}>
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                  
                  {/* Code artifact button if message has code */}
                  {msg.hasCode && (
                    <button 
                      onClick={() => onArtifactOpen({ title: msg.fileName!, content: msg.codeContent!, lang: msg.language! })}
                      className="mt-3 flex items-center space-x-3 bg-white border border-gray-200 rounded-xl p-3 hover:border-indigo-300 hover:shadow-md transition-all group text-left w-full"
                    >
                      <div className="bg-indigo-50 text-indigo-600 p-2.5 rounded-lg group-hover:bg-indigo-100 transition-colors">
                        {msg.fileName?.endsWith('.md') ? <FileText size={20} /> : <Code2 size={20} />}
                      </div>
                      <div>
                        <div className="font-semibold text-gray-800 text-sm group-hover:text-indigo-600 transition-colors">{msg.fileName}</div>
                        <div className="text-xs text-gray-400 mt-0.5">Click to view & edit</div>
                      </div>
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Loading indicator */}
      {isLoading && (
        <div className="flex gap-4 px-4 md:px-8">
           <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center text-white animate-pulse">
             <Sparkles size={16} />
           </div>
           <div className="text-gray-400 text-sm py-2 pl-1">Coach is thinking...</div>
        </div>
      )}
      
      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
}