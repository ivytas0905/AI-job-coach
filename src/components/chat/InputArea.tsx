// src/components/chat/InputArea.tsx
import React from 'react';
import { Paperclip, Image as ImageIcon, Mic, Send } from 'lucide-react';

interface InputAreaProps {
  input: string;
  setInput: (val: string) => void;
  onSend: (e: React.FormEvent) => void;
  isLoading: boolean;
  isArtifactOpen: boolean;
}

export default function InputArea({ input, setInput, onSend, isLoading, isArtifactOpen }: InputAreaProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend(e);
    }
  };

  return (
    <div className="p-4 bg-white md:px-8 pb-6">
      <div className={isArtifactOpen ? '' : 'max-w-3xl mx-auto'}>
        <div className="bg-gray-50 border border-gray-200 rounded-2xl p-3 shadow-sm focus-within:ring-2 focus-within:ring-indigo-100 focus-within:border-indigo-400 transition-all">
          {/* Text Input */}
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message Job Coach..."
            className="w-full bg-transparent border-none focus:ring-0 resize-none text-gray-800 placeholder-gray-400 min-h-[60px] leading-relaxed px-1"
            style={{ minHeight: '60px' }}
            aria-label="Message input"
          />
          
          {/* Action Buttons */}
          <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-100">
            <div className="flex items-center gap-1">
              <button className="flex items-center gap-2 px-3 py-1.5 text-gray-500 bg-transparent hover:bg-gray-200 rounded-lg transition-colors text-sm font-medium">
                <Paperclip size={18} /> <span className="hidden sm:inline">Upload</span>
              </button>
              <button className="flex items-center gap-2 px-3 py-1.5 text-gray-500 bg-transparent hover:bg-gray-200 rounded-lg transition-colors text-sm font-medium">
                <ImageIcon size={18} /> <span className="hidden sm:inline">Image</span>
              </button>
            </div>
            
            <div className="flex items-center gap-2">
              <button className="flex items-center justify-center w-9 h-9 text-gray-500 bg-transparent hover:bg-gray-200 rounded-full transition-colors">
                <Mic size={20} />
              </button>
              <button
                onClick={onSend}
                disabled={!input.trim() || isLoading}
                className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium transition-all shadow-sm ${
                  input.trim() ? 'bg-indigo-600 text-white hover:bg-indigo-700' : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                }`}
              >
                <span>Send</span> <Send size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="text-center text-xs text-gray-400 mt-3">AI can make mistakes. Please verify important information.</div>
    </div>
  );
}