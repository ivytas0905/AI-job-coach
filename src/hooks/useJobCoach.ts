// src/hooks/useJobCoach.ts
import { useState, useRef, useEffect } from 'react';
import { Message } from '@/src/types';

export function useJobCoach() {
  const [messages, setMessages] = useState<Message[]>([
    { 
      id: '1', 
      role: 'ai', 
      content: 'Hello! I am your AI Job Coach.\n\nI can help you polish your resume, conduct mock interviews, or practice algorithm problems. Are you ready to start?', 
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Artifact state (Right panel)
  const [activeArtifact, setActiveArtifact] = useState<{title: string, content: string, lang: string} | null>(null);
  const [isArtifactOpen, setIsArtifactOpen] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text
    };
    
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Simulate Network Delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      let aiResponse: Message;
      const lowerText = text.toLowerCase();

      // Logic simulation
      if (lowerText.includes('resume')) {
        const resumeTemplate = `# Resume (Optimized)\n\n## Profile\nSoftware Engineer...`;
        aiResponse = {
          id: (Date.now() + 1).toString(),
          role: 'ai',
          content: 'Sure, let\'s optimize your resume. See the template on the right.',
          hasCode: true,
          codeContent: resumeTemplate,
          fileName: 'Resume_Optimized.md',
          language: 'markdown'
        };
        setActiveArtifact({ title: 'Resume_Optimized.md', content: resumeTemplate, lang: 'markdown' });
        setIsArtifactOpen(true);
      } else if (lowerText.includes('leetcode')) {
        const code = `function twoSum(nums, target) { ... }`;
        aiResponse = {
          id: (Date.now() + 1).toString(),
          role: 'ai',
          content: 'Here is a LeetCode problem solution.',
          hasCode: true,
          codeContent: code,
          fileName: 'Solution.ts',
          language: 'typescript'
        };
        setActiveArtifact({ title: 'Solution.ts', content: code, lang: 'typescript' });
        setIsArtifactOpen(true);
      } else {
        aiResponse = {
          id: (Date.now() + 1).toString(),
          role: 'ai',
          content: `Received: "${text}". How else can I help?`
        };
      }

      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    messages,
    input,
    setInput,
    isLoading,
    messagesEndRef,
    sendMessage,
    activeArtifact,
    isArtifactOpen,
    setIsArtifactOpen,
    setActiveArtifact
  };
}