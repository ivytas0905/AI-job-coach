'use client';

import React, { useState } from 'react';
import { Sparkles, PanelLeft, PanelLeftClose, FileText, MessageSquare, Cpu } from 'lucide-react';

// Import hooks and data using relative paths (to avoid path alias issues)
import { useJobCoach } from '../hooks/useJobCoach';
import { mockHistory } from '../data/mock';
import { SuggestionCard } from '../types';

// Import separated components using relative paths
import Sidebar from '../components/layout/Sidebar';
// Note: If you renamed this file to CodePanel.tsx, please update the import below accordingly
import ArtifactPanel from '../components/artifact/ArtifactPanel';
import MessageList from '../components/chat/MessageList';
import InputArea from '../components/chat/InputArea';

export default function JobCoachPage() {
  // 1. Use the custom hook for logic
  const { 
    messages, input, setInput, isLoading, messagesEndRef, sendMessage, 
    activeArtifact, isArtifactOpen, setIsArtifactOpen, setActiveArtifact 
  } = useJobCoach();

  // 2. State for Sidebar visibility
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // 3. Suggestion Cards Data
  const suggestionCards: SuggestionCard[] = [
    { icon: <FileText size={20} className="text-purple-600" />, title: "Resume Polish", desc: "Upload resume for expert review", prompt: "Help me optimize this resume..." },
    { icon: <MessageSquare size={20} className="text-blue-600" />, title: "Mock Interview", desc: "Practice with a realistic interview", prompt: "I am applying for a Senior Frontend Engineer role..." },
    { icon: <Cpu size={20} className="text-green-600" />, title: "LeetCode Practice", desc: "Daily algo challenge & hints", prompt: "Give me a medium difficulty LeetCode algorithm..." }
  ];

  return (
    <div className="flex h-screen w-full bg-white text-gray-900 font-sans overflow-hidden">
      
      {/* --- Left Sidebar --- */}
      <Sidebar 
        isOpen={isSidebarOpen} 
        history={mockHistory} 
        onNewChat={() => window.location.reload()} 
      />

      {/* --- Main Chat Area --- */}
      <div 
        // Feature: Click outside to close the sidebar
        // When the user clicks anywhere in the main area, if the sidebar is open, close it.
        onClick={() => {
          if (isSidebarOpen) setIsSidebarOpen(false);
        }}
        className={`flex flex-col h-full transition-all duration-300 ease-in-out flex-1 min-w-0 ${isArtifactOpen ? 'border-r border-gray-200' : ''}`}
      >
        
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 bg-white/80 backdrop-blur-md sticky top-0 z-10 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <button 
              // Feature: Toggle sidebar
              // IMPORTANT: stopPropagation is needed to prevent the click from bubbling up 
              // to the parent div's onClick, which would immediately close the sidebar again.
              onClick={(e) => {
                e.stopPropagation(); 
                setIsSidebarOpen(!isSidebarOpen);
              }} 
              className="p-2 text-gray-500 hover:bg-gray-100 rounded-md transition-colors"
              title={isSidebarOpen ? "Close sidebar" : "Open sidebar"}
            >
              {isSidebarOpen ? <PanelLeftClose size={20} /> : <PanelLeft size={20} />}
            </button>
            
            <div className="flex items-center space-x-2 text-indigo-600">
              <Sparkles size={20} />
              <h1 className="text-lg font-semibold tracking-tight text-gray-800">Job Coach AI</h1>
            </div>
          </div>
          <div className="px-2 py-1 bg-indigo-50 text-indigo-600 text-xs font-medium rounded-full border border-indigo-100">Pro</div>
        </header>

        {/* Message List Component */}
        <MessageList 
          messages={messages} 
          isLoading={isLoading} 
          onArtifactOpen={(data) => { setActiveArtifact(data); setIsArtifactOpen(true); }}
          onCardClick={sendMessage}
          cards={suggestionCards}
          recentHistory={mockHistory}
          messagesEndRef={messagesEndRef}
        />

        {/* Input Area Component */}
        <InputArea 
          input={input} 
          setInput={setInput} 
          onSend={(e) => { e.preventDefault(); sendMessage(input); }} 
          isLoading={isLoading} 
          isArtifactOpen={isArtifactOpen}
        />
      </div>

      {/* --- Right Artifact Panel --- */}
      {isArtifactOpen && activeArtifact && (
        <ArtifactPanel 
          {...activeArtifact} 
          onClose={() => setIsArtifactOpen(false)} 
        />
      )}
    </div>
  );
}