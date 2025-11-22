'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { resumeOptimizationAPI } from '@/lib/api-client';
import type { OptimizationSuggestion } from '@/lib/api-client';

interface ParsedResume {
  personal_info?: {
    name?: string;
    email?: string;
    phone?: string;
    linkedin?: string;
    github?: string;
  };
  experience?: Array<{
    company?: string;
    title?: string;
    location?: string;
    start_date?: string;
    end_date?: string;
    description?: string;
  }>;
  education?: Array<{
    school?: string;
    degree?: string;
    start_date?: string;
    end_date?: string;
    description?: string;
  }>;
  skills?: Array<{
    name?: string;
    category?: string;
  }>;
}

interface ConversationMessage {
  role: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

interface Hint {
  type: string;
  message: string;
  follow_up_question?: string | null;
  placeholder?: string | null;
}

interface BulletOptimization {
  original: string;
  suggested: string;
  reasons: string[];
  keywordsAdded: string[];
  scoreImprovement: number;
  hints?: Hint[];
  status: 'pending' | 'accepted' | 'rejected' | 'discussing';
  conversation: ConversationMessage[];
  isRefining?: boolean;
  company?: string;
  title?: string;
}

export default function OptimizePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [resume, setResume] = useState<ParsedResume | null>(null);
  const [optimizations, setOptimizations] = useState<Map<string, BulletOptimization>>(new Map());
  const [error, setError] = useState<string | null>(null);
  const [activeDiscussionKey, setActiveDiscussionKey] = useState<string | null>(null);
  const [discussionMessage, setDiscussionMessage] = useState('');
  const [jobTitle, setJobTitle] = useState('');

  useEffect(() => {
    loadResumeAndOptimizations();
  }, []);

  const loadResumeAndOptimizations = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Get data from session storage
      const parsedResumeStr = sessionStorage.getItem('parsed_resume');
      const targetKeywordsStr = sessionStorage.getItem('target_keywords');
      const jdJobTitle = sessionStorage.getItem('job_title');

      if (!parsedResumeStr) {
        throw new Error('No resume data found. Please upload your resume first.');
      }

      if (!targetKeywordsStr) {
        throw new Error('No job description keywords found. Please analyze a JD first.');
      }

      const parsedResume = JSON.parse(parsedResumeStr);
      const targetKeywords = JSON.parse(targetKeywordsStr);

      console.log('📋 Parsed Resume:', parsedResume);
      console.log('🎯 Target Keywords:', targetKeywords);

      setResume(parsedResume);
      setJobTitle(jdJobTitle || 'Target Position');

      // Get optimization suggestions
      const result = await resumeOptimizationAPI.optimizeResume({
        resume_data: parsedResume,
        target_keywords: targetKeywords,
        job_title: jdJobTitle || 'Target Position',
      });

      console.log('✨ Optimization Result:', result);
      console.log('📊 Optimizations count:', result.optimizations.length);

      // Map optimizations by section and bullet
      const optMap = new Map<string, BulletOptimization>();
      result.optimizations.forEach((opt, idx) => {
        const key = `${opt.section}-${opt.subsection}-${opt.original_text}`;

        console.log(`🔑 Optimization ${idx} key:`, key);
        console.log(`   Original (first 50 chars):`, opt.original_text.substring(0, 50) + '...');

        // Extract company and title from subsection
        const [company, title] = opt.subsection.split(' - ');

        optMap.set(key, {
          original: opt.original_text,
          suggested: opt.optimized_text,
          reasons: opt.improvements,
          keywordsAdded: opt.keywords_added || [],
          scoreImprovement: opt.score_improvement,
          hints: opt.hints || [],
          status: 'pending',
          conversation: [],
          company: company,
          title: title
        });
      });

      console.log('🗺️ Total optimization keys stored:', optMap.size);
      console.log('🔑 All keys:', Array.from(optMap.keys()));

      setOptimizations(optMap);

    } catch (err: any) {
      setError(err.message || 'Failed to load resume optimization');
      console.error('Load error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getBulletOptimization = (section: string, subsection: string, bullet: string): BulletOptimization | undefined => {
    const key = `${section}-${subsection}-${bullet}`;
    return optimizations.get(key);
  };

  const updateBulletStatus = (section: string, subsection: string, bullet: string, status: 'accepted' | 'rejected') => {
    const key = `${section}-${subsection}-${bullet}`;
    const opt = optimizations.get(key);
    if (opt) {
      setOptimizations(new Map(optimizations.set(key, { ...opt, status })));
    }
  };

  const startDiscussion = (section: string, subsection: string, bullet: string) => {
    const key = `${section}-${subsection}-${bullet}`;
    setActiveDiscussionKey(key);
    const opt = optimizations.get(key);
    if (opt) {
      setOptimizations(new Map(optimizations.set(key, { ...opt, status: 'discussing' })));
    }
  };

  const submitDiscussion = async (section: string, subsection: string, bullet: string) => {
    const key = `${section}-${subsection}-${bullet}`;
    const opt = optimizations.get(key);

    if (!opt || !discussionMessage.trim()) return;

    try {
      // Add user message to conversation
      const userMessage: ConversationMessage = {
        role: 'user',
        text: discussionMessage,
        timestamp: new Date()
      };

      // Update status to show refining
      setOptimizations(new Map(optimizations.set(key, {
        ...opt,
        conversation: [...opt.conversation, userMessage],
        isRefining: true,
        status: 'discussing'
      })));

      setDiscussionMessage('');

      // Get target keywords from session storage
      const targetKeywordsStr = sessionStorage.getItem('target_keywords');
      const targetKeywords = targetKeywordsStr ? JSON.parse(targetKeywordsStr) : [];

      // Call API to refine optimization
      const result = await resumeOptimizationAPI.refineOptimization({
        original_bullet: opt.original,
        current_suggestion: opt.suggested,
        user_feedback: discussionMessage,
        target_keywords: targetKeywords,
        company: opt.company,
        title: opt.title,
        job_title: jobTitle
      });

      // Add AI response to conversation
      const aiMessage: ConversationMessage = {
        role: 'ai',
        text: result.ai_explanation,
        timestamp: new Date()
      };

      // Update optimization with refined suggestion
      setOptimizations(new Map(optimizations.set(key, {
        ...opt,
        suggested: result.refined_text,
        reasons: [...opt.reasons, ...result.improvements],
        keywordsAdded: [...new Set([...opt.keywordsAdded, ...result.keywords_added])],
        conversation: [...opt.conversation, userMessage, aiMessage],
        isRefining: false,
        status: 'pending'
      })));

      setActiveDiscussionKey(null);

    } catch (err: any) {
      console.error('Discussion error:', err);
      alert('Failed to refine optimization: ' + (err.message || 'Unknown error'));

      // Reset refining status
      const currentOpt = optimizations.get(key);
      if (currentOpt) {
        setOptimizations(new Map(optimizations.set(key, {
          ...currentOpt,
          isRefining: false,
          status: 'pending'
        })));
      }
    }
  };

  const handleFinalize = () => {
    // Build finalized resume with accepted changes
    const finalizedResume = { ...resume };

    // Apply accepted optimizations
    optimizations.forEach((opt, key) => {
      if (opt.status === 'accepted') {
        // Update the resume data with accepted suggestions
        // This will be implemented in the next step
      }
    });

    // Save and navigate to next step
    sessionStorage.setItem('finalized_resume', JSON.stringify(finalizedResume));
    alert('Resume optimized successfully! Ready for tailoring.');
    router.push('/dashboard/resume/tailor');
  };

  const getAcceptedCount = () => {
    return Array.from(optimizations.values()).filter(opt => opt.status === 'accepted').length;
  };

  const getTotalImprovement = () => {
    return Array.from(optimizations.values())
      .filter(opt => opt.status === 'accepted')
      .reduce((sum, opt) => sum + opt.scoreImprovement, 0);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-500 to-pink-600 p-8 flex items-center justify-center">
        <div className="text-white text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-xl font-bold">Analyzing your resume...</p>
          <p className="text-sm mt-2">AI is generating optimization suggestions</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-500 to-pink-600 p-8 flex items-center justify-center">
        <div className="bg-white rounded-3xl p-8 max-w-md">
          <p className="text-red-600 font-bold text-xl mb-4">Error</p>
          <p className="text-gray-700 mb-6">{error}</p>
          <button
            onClick={() => router.back()}
            className="w-full bg-purple-500 text-white py-3 rounded-full font-bold hover:bg-purple-600"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-500 to-pink-600 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 bg-white bg-opacity-20 text-white px-6 py-3 rounded-full hover:bg-opacity-30 transition-all backdrop-blur-sm font-medium"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span>Back</span>
          </button>
          <h1 className="text-4xl font-bold text-white">Resume Optimization</h1>
          <div className="w-32"></div>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-2xl p-6 shadow-xl">
            <p className="text-gray-500 text-sm mb-2">Total Suggestions</p>
            <p className="text-4xl font-bold text-purple-600">{optimizations.size}</p>
          </div>
          <div className="bg-white rounded-2xl p-6 shadow-xl">
            <p className="text-gray-500 text-sm mb-2">Changes Accepted</p>
            <p className="text-4xl font-bold text-green-600">{getAcceptedCount()}</p>
          </div>
          <div className="bg-white rounded-2xl p-6 shadow-xl">
            <p className="text-gray-500 text-sm mb-2">Score Improvement</p>
            <p className="text-4xl font-bold text-blue-600">+{getTotalImprovement().toFixed(0)}</p>
          </div>
        </div>

        {/* Finalize Button */}
        <div className="mb-8">
          <button
            onClick={handleFinalize}
            disabled={getAcceptedCount() === 0}
            className={`w-full py-4 rounded-2xl font-bold text-lg transition-all shadow-xl ${
              getAcceptedCount() === 0
                ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                : 'bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500 text-white hover:from-green-600 hover:via-emerald-600 hover:to-teal-600 hover:shadow-2xl'
            }`}
          >
            {getAcceptedCount() === 0
              ? 'Accept changes to finalize'
              : `✓ Finalize Resume with ${getAcceptedCount()} ${getAcceptedCount() === 1 ? 'Change' : 'Changes'}`
            }
          </button>
        </div>

        {/* Resume Display with Inline Optimizations */}
        <div className="bg-white rounded-3xl p-8 shadow-2xl">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">{resume?.personal_info?.name || 'Your Resume'}</h2>
          <p className="text-lg text-purple-600 font-medium mb-8">Optimizing for: {jobTitle}</p>

          {/* Personal Info */}
          {resume?.personal_info && (
            <div className="mb-8 pb-8 border-b-2 border-gray-200">
              <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                {resume.personal_info.email && (
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    {resume.personal_info.email}
                  </span>
                )}
                {resume.personal_info.phone && (
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                    {resume.personal_info.phone}
                  </span>
                )}
                {resume.personal_info.linkedin && (
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                    </svg>
                    {resume.personal_info.linkedin}
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Experience Section */}
          {resume?.experience && resume.experience.length > 0 && (
            <div className="mb-8">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">EXPERIENCE</h3>
              {resume.experience.map((exp, expIdx) => {
                const subsection = `${exp.company} - ${exp.title}`;
                const bullets = exp.description ? exp.description.split('\n').filter(b => b.trim()) : [];

                console.log(`📌 Experience ${expIdx}:`, {
                  company: exp.company,
                  title: exp.title,
                  subsection,
                  bulletsCount: bullets.length,
                  bullets: bullets
                });

                return (
                  <div key={expIdx} className="mb-8 last:mb-0">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="text-xl font-bold text-gray-800">{exp.title}</h4>
                        <p className="text-lg text-gray-600">{exp.company}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500">{exp.location}</p>
                        <p className="text-sm text-gray-500">{exp.start_date} - {exp.end_date}</p>
                      </div>
                    </div>

                    {/* Bullet Points with Optimizations */}
                    <div className="mt-4 space-y-4">
                      {bullets.map((bullet, bulletIdx) => {
                        const opt = getBulletOptimization('experience', subsection, bullet);

                        console.log(`🔍 Checking bullet ${bulletIdx}:`, {
                          bullet: bullet.substring(0, 50) + '...',
                          key: `experience-${subsection}-${bullet}`,
                          hasOptimization: !!opt
                        });

                        return (
                          <div key={bulletIdx}>
                            {/* Original Bullet */}
                            <div className="flex items-start gap-3">
                              <span className="text-purple-500 mt-1">•</span>
                              <div className="flex-1">
                                <p className={`text-gray-700 ${opt ? 'line-through opacity-60' : ''}`}>
                                  {bullet}
                                </p>

                                {/* Optimization Suggestion */}
                                {opt && (
                                  <div className={`mt-3 p-4 rounded-xl border-2 ${
                                    opt.status === 'accepted' ? 'bg-green-50 border-green-500' :
                                    opt.status === 'rejected' ? 'bg-red-50 border-red-300' :
                                    opt.status === 'discussing' ? 'bg-blue-50 border-blue-500' :
                                    'bg-yellow-50 border-yellow-500'
                                  }`}>
                                    {/* Suggested Text */}
                                    <div className="mb-3">
                                      <p className="text-xs font-bold text-gray-500 mb-1">SUGGESTED:</p>
                                      <p className="text-gray-800 font-medium">{opt.suggested}</p>
                                    </div>

                                    {/* Improvements */}
                                    <div className="mb-3">
                                      <p className="text-xs font-bold text-gray-500 mb-2">IMPROVEMENTS:</p>
                                      <ul className="space-y-1">
                                        {opt.reasons.map((reason, idx) => (
                                          <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                                            <span className="text-green-500 mt-0.5">✓</span>
                                            <span>{reason}</span>
                                          </li>
                                        ))}
                                      </ul>
                                    </div>

                                    {/* Keywords Added */}
                                    {opt.keywordsAdded && opt.keywordsAdded.length > 0 && (
                                      <div className="mb-3">
                                        <p className="text-xs font-bold text-gray-500 mb-2">KEYWORDS ADDED:</p>
                                        <div className="flex flex-wrap gap-2">
                                          {opt.keywordsAdded.map((kw, idx) => (
                                            <span key={idx} className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs font-medium">
                                              {kw}
                                            </span>
                                          ))}
                                        </div>
                                      </div>
                                    )}

                                    {/* Hints for Further Improvement */}
                                    {opt.hints && opt.hints.length > 0 && (
                                      <div className="mb-3 bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border border-blue-200">
                                        <p className="text-xs font-bold text-blue-800 mb-3 flex items-center gap-2">
                                          <span className="text-base">💡</span>
                                          WAYS TO IMPROVE FURTHER:
                                        </p>
                                        <div className="space-y-2">
                                          {opt.hints.map((hint, idx) => (
                                            <div key={idx} className="bg-white p-3 rounded-lg border border-blue-100">
                                              <p className="text-sm text-gray-800 font-medium mb-1">
                                                {hint.message}
                                              </p>
                                              {hint.follow_up_question && (
                                                <p className="text-xs text-blue-600 italic mt-1">
                                                  {hint.follow_up_question}
                                                </p>
                                              )}
                                              {hint.placeholder && (
                                                <p className="text-xs text-gray-500 mt-1">
                                                  Suggestion: <span className="font-mono bg-gray-100 px-1 py-0.5 rounded">{hint.placeholder}</span>
                                                </p>
                                              )}
                                            </div>
                                          ))}
                                        </div>
                                      </div>
                                    )}

                                    {/* Score Improvement */}
                                    <div className="mb-4">
                                      <span className="inline-block bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold">
                                        +{opt.scoreImprovement} points
                                      </span>
                                    </div>

                                    {/* Conversation History */}
                                    {opt.conversation && opt.conversation.length > 0 && (
                                      <div className="mb-3 space-y-2">
                                        <p className="text-xs font-bold text-gray-500 mb-2">CONVERSATION:</p>
                                        {opt.conversation.map((msg, idx) => (
                                          <div
                                            key={idx}
                                            className={`p-3 rounded-lg ${
                                              msg.role === 'user'
                                                ? 'bg-blue-50 border border-blue-200 ml-4'
                                                : 'bg-green-50 border border-green-200 mr-4'
                                            }`}
                                          >
                                            <p className="text-xs font-bold text-gray-600 mb-1">
                                              {msg.role === 'user' ? '👤 You:' : '🤖 AI:'}
                                            </p>
                                            <p className="text-sm text-gray-700">{msg.text}</p>
                                          </div>
                                        ))}
                                      </div>
                                    )}

                                    {/* Discussion Area */}
                                    {opt.status === 'discussing' && activeDiscussionKey === `experience-${subsection}-${bullet}` && (
                                      <div className="mb-3">
                                        {opt.isRefining ? (
                                          <div className="p-4 bg-blue-50 rounded-lg text-center">
                                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
                                            <p className="text-sm text-blue-700 font-medium">AI is refining the suggestion...</p>
                                          </div>
                                        ) : (
                                          <>
                                            <textarea
                                              value={discussionMessage}
                                              onChange={(e) => setDiscussionMessage(e.target.value)}
                                              placeholder="Ask AI to refine this suggestion... (e.g., 'Make it more technical', 'Add more metrics', 'Focus on leadership')"
                                              className="w-full p-3 border border-gray-300 rounded-lg text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                              rows={3}
                                            />
                                            <div className="flex gap-2 mt-2">
                                              <button
                                                onClick={() => submitDiscussion('experience', subsection, bullet)}
                                                disabled={!discussionMessage.trim()}
                                                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                                                  discussionMessage.trim()
                                                    ? 'bg-blue-500 text-white hover:bg-blue-600'
                                                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                }`}
                                              >
                                                💬 Send to AI
                                              </button>
                                              <button
                                                onClick={() => setActiveDiscussionKey(null)}
                                                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-400"
                                              >
                                                Cancel
                                              </button>
                                            </div>
                                          </>
                                        )}
                                      </div>
                                    )}

                                    {/* Action Buttons */}
                                    <div className="flex gap-2">
                                      <button
                                        onClick={() => updateBulletStatus('experience', subsection, bullet, 'accepted')}
                                        className={`flex-1 py-2 rounded-lg font-medium text-sm transition ${
                                          opt.status === 'accepted'
                                            ? 'bg-green-500 text-white'
                                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                                        }`}
                                      >
                                        ✓ Accept
                                      </button>
                                      <button
                                        onClick={() => updateBulletStatus('experience', subsection, bullet, 'rejected')}
                                        className={`flex-1 py-2 rounded-lg font-medium text-sm transition ${
                                          opt.status === 'rejected'
                                            ? 'bg-red-500 text-white'
                                            : 'bg-red-100 text-red-700 hover:bg-red-200'
                                        }`}
                                      >
                                        ✗ Reject
                                      </button>
                                      <button
                                        onClick={() => startDiscussion('experience', subsection, bullet)}
                                        className="flex-1 py-2 rounded-lg font-medium text-sm bg-blue-100 text-blue-700 hover:bg-blue-200 transition"
                                      >
                                        💬 Discuss
                                      </button>
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Education Section */}
          {resume?.education && resume.education.length > 0 && (
            <div className="mb-8">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">EDUCATION</h3>
              {resume.education.map((edu, idx) => (
                <div key={idx} className="mb-4 last:mb-0">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="text-xl font-bold text-gray-800">{edu.school}</h4>
                      <p className="text-lg text-gray-600">{edu.degree}</p>
                    </div>
                    <p className="text-sm text-gray-500">{edu.start_date} - {edu.end_date}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Skills Section */}
          {resume?.skills && resume.skills.length > 0 && (
            <div>
              <h3 className="text-2xl font-bold text-gray-800 mb-6">SKILLS</h3>
              <div className="space-y-4">
                {(() => {
                  const groupedSkills: Record<string, string[]> = {};
                  resume.skills.forEach(skill => {
                    const category = skill.category || 'Other';
                    if (!groupedSkills[category]) {
                      groupedSkills[category] = [];
                    }
                    groupedSkills[category].push(skill.name || '');
                  });

                  return Object.entries(groupedSkills).map(([category, skills]) => (
                    <div key={category}>
                      <p className="font-bold text-gray-700 mb-2">{category}:</p>
                      <div className="flex flex-wrap gap-2 ml-4">
                        {skills.map((skillName, idx) => (
                          <span
                            key={idx}
                            className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium"
                          >
                            {skillName}
                          </span>
                        ))}
                      </div>
                    </div>
                  ));
                })()}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
