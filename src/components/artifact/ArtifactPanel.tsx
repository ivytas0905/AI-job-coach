// src/components/artifact/ArtifactPanel.tsx
import React, { useState } from 'react';
import { Terminal, Copy, Check, X } from 'lucide-react';

interface ArtifactPanelProps {
  title: string;
  content: string;
  lang: string;
  onClose: () => void;
}

export default function ArtifactPanel({ title, content, lang, onClose }: ArtifactPanelProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-1/2 h-full bg-[#1e1e1e] flex flex-col border-l border-gray-200 shadow-2xl animate-in slide-in-from-right-10 duration-300 z-30 flex-shrink-0">
      <div className="flex items-center justify-between px-4 py-3 bg-[#252526] border-b border-[#333]">
        <div className="flex items-center space-x-2 text-gray-300">
          <Terminal size={16} className="text-blue-400" />
          <span className="text-sm font-medium font-mono">{title}</span>
        </div>
        <div className="flex items-center space-x-2">
          <button onClick={handleCopy} className="p-1.5 text-gray-400 hover:text-white hover:bg-white/10 rounded transition-colors">
            {copied ? <Check size={16} className="text-green-400" /> : <Copy size={16} />}
          </button>
           <button onClick={onClose} className="p-1.5 text-gray-400 hover:text-white hover:bg-white/10 rounded transition-colors">
            <X size={16} />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-0 relative font-mono text-sm">
        <div className="absolute left-0 top-4 bottom-0 w-10 text-right pr-3 text-gray-600 select-none">
          {content.split('\n').map((_, i) => <div key={i} className="leading-6">{i + 1}</div>)}
        </div>
        <pre className="p-4 pl-12 text-gray-300 leading-6 tab-4 outline-none">
          <code>{content}</code>
        </pre>
      </div>

      <div className="px-4 py-2 bg-[#007acc] text-white text-xs flex items-center justify-between">
        <span>{lang.toUpperCase()}</span>
        <span>UTF-8</span>
      </div>
    </div>
  );
}