// src/types/index.ts

export type Role = 'user' | 'ai';

export interface Message {
  id: string;
  role: Role;
  content: string;
  hasCode?: boolean;
  codeContent?: string;
  fileName?: string;
  language?: string;
}

export interface HistoryItem {
  id: number;
  title: string;
  date: string;
}

export interface SuggestionCard {
  icon: React.ReactNode;
  title: string;
  desc: string;
  prompt: string;
}