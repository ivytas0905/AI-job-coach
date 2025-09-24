'use client';
import { UserButton } from "@clerk/nextjs";

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Job Coach AI</h1>
            </div>
            <div className="flex items-center space-x-4">
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </div>
      </nav>

      {/* 主要内容 */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome to Job Coach AI!
          </h2>
          <p className="text-gray-600">
            Your personal career coach is ready to help optimize your job search journey!
          </p>
        </div>

        {/* Core Feature - Daily Schedule Generator */}
        <div className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-xl p-8 text-white mb-8">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center mb-4">
                <div className="bg-white/20 p-3 rounded-full mr-4">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-2">🚀 Daily Job Search Schedule</h2>
                  <p className="text-white/90 text-lg">
                    Get your personalized daily action plan - our signature feature that sets you apart from other job seekers
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap gap-3 mb-6">
                <div className="bg-white/10 px-3 py-1 rounded-full text-sm">✅ Personalized Tasks</div>
                <div className="bg-white/10 px-3 py-1 rounded-full text-sm">⏰ Time-blocked Schedule</div>
                <div className="bg-white/10 px-3 py-1 rounded-full text-sm">🎯 Goal-oriented</div>
                <div className="bg-white/10 px-3 py-1 rounded-full text-sm">📊 Progress Tracking</div>
              </div>
            </div>
            <div className="ml-6">
              <button 
                onClick={() => window.location.href = '/daily-schedule'}
                className="bg-white text-purple-600 font-bold py-4 px-8 rounded-xl hover:bg-gray-100 transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                Generate Today&apos;s Schedule
              </button>
            </div>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* AI Chat Card */}
          <div className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center mb-4">
              <div className="bg-blue-500 p-3 rounded-full">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="ml-3 text-lg font-semibold text-gray-900">AI Career Guidance</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Chat one-on-one with your AI coach for personalized job search advice and career planning guidance
            </p>
            <button 
              onClick={() => window.location.href = '/chat'}
              className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 transition-colors"
            >
              Start Chatting
            </button>
          </div>

          {/* Resume Optimization Card */}
          <div className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center mb-4">
              <div className="bg-green-500 p-3 rounded-full">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="ml-3 text-lg font-semibold text-gray-900">Resume Optimization</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Upload your resume and get AI-powered analysis with targeted optimization suggestions
            </p>
            <button 
              onClick={() => window.location.href = '/resume'}
              className="w-full bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition-colors"
            >
              Optimize Resume
            </button>
          </div>

          {/* Interview Preparation Card */}
          <div className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center mb-4">
              <div className="bg-purple-500 p-3 rounded-full">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="ml-3 text-lg font-semibold text-gray-900">Interview Practice</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Simulate real interview scenarios to improve your performance and answering techniques
            </p>
            <button 
              onClick={() => window.location.href = '/interview'}
              className="w-full bg-purple-500 text-white py-2 px-4 rounded-md hover:bg-purple-600 transition-colors"
            >
              Start Practice
            </button>
          </div>
        </div>

        {/* Quick Action Section */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
          <h3 className="text-xl font-bold mb-2">Need More Support?</h3>
          <p className="mb-4 opacity-90">
            Chat with your AI coach for additional guidance and motivation
          </p>
          <button 
            onClick={() => window.location.href = '/chat'}
            className="bg-white text-blue-600 font-semibold py-2 px-6 rounded-md hover:bg-gray-100 transition-colors"
          >
            Chat with AI Coach
          </button>
        </div>
      </main>
    </div>
  );
}