// src/components/layout/Sidebar.tsx
import React from 'react';
import { Plus, MessageSquare, Settings } from 'lucide-react';
import { HistoryItem } from '../../types';

interface SidebarProps {
  isOpen: boolean;
  history: HistoryItem[];
  onNewChat: () => void;
}

export default function Sidebar({ isOpen, history, onNewChat }: SidebarProps) {
  return (
    <div 
      onClick={(e) => e.stopPropagation()}
      className={`${
        isOpen ? 'w-[260px] border-r' : 'w-0 border-none'
      } bg-[#171717] transition-all duration-300 ease-in-out border-gray-800 relative z-20 flex-shrink-0 overflow-hidden h-full`}
    >
      <div className="w-[260px] h-full flex flex-col">
        {/* New Chat */}
        <div className="p-3 mb-2">
          <button 
            onClick={onNewChat}
            className="w-full flex items-center gap-3 px-3 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg text-white transition-colors border border-gray-700 shadow-sm"
          >
            <Plus size={18} />
            <span className="text-sm font-medium">New Chat</span>
          </button>
        </div>

        {/* History */}
        <div className="flex-1 overflow-y-auto px-3 py-2 scrollbar-thin scrollbar-thumb-thumb-gray-700">
          <div className="text-xs font-semibold text-gray-500 mb-3 px-2">Recent</div>
          <div className="space-y-1">
            {history.map((item) => (
              <button 
                key={item.id}
                className="w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-800 transition-colors group"
              >
                <MessageSquare size={16} className="text-gray-500 group-hover:text-gray-300 flex-shrink-0" />
                <div className="flex-1 overflow-hidden">
                  <div className="truncate text-sm text-gray-300 group-hover:text-white">{item.title}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Profile */}
        <div className="p-3 border-t border-gray-800 bg-[#171717]">
          <button className="w-full flex items-center gap-3 px-2 py-2 hover:bg-gray-800 rounded-lg transition-colors">
            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">JC</div>
            <div className="flex-1 text-left overflow-hidden">
              <div className="text-sm font-medium text-white truncate">Job Seeker</div>
              <div className="text-xs text-gray-500 truncate">Free Plan</div>
            </div>
            <Settings size={16} className="text-gray-500 flex-shrink-0" />
          </button>
        </div>
      </div>
    </div>
  );
}