'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { jdAnalysisAPI } from '@/lib/api-client';
import type { EnhancedJobDescription } from '@/types/resume';

export default function JDInputPage() {
  const router = useRouter();
  const [jdText, setJdText] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [company, setCompany] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzedJD, setAnalyzedJD] = useState<EnhancedJobDescription | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!jdText || jdText.trim().length < 50) {
      setError('Job description must be at least 50 characters');
      return;
    }

    if (!jobTitle || jobTitle.trim().length < 2) {
      setError('Please enter a job title');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      // Use new enhanced API client
      const result = await jdAnalysisAPI.analyze({
        jd_text: jdText,
        job_title: jobTitle,
        company: company || undefined,
      });

      setAnalyzedJD(result);

      // Store JD data in session storage for next step
      sessionStorage.setItem('jd_id', result.jd_id);
      sessionStorage.setItem('target_keywords', JSON.stringify(
        result.top_keywords.map(k => k.keyword)
      ));
      sessionStorage.setItem('job_title', jobTitle);

    } catch (err: any) {
      setError(err.message || 'Failed to analyze job description');
      console.error('JD Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleContinue = () => {
    // Navigate to tailor page
    router.push('/dashboard/resume/optimize');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 p-8">
      <div className="max-w-6xl mx-auto">
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
          <h1 className="text-4xl font-bold text-white">Analyze Job Description</h1>
          <div className="w-32"></div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="bg-white rounded-3xl p-8 shadow-2xl">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Paste Job Description</h2>

            {/* Job Title Input */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g., Senior Backend Engineer"
                className="w-full p-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none"
              />
            </div>

            {/* Company Input (Optional) */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company (Optional)
              </label>
              <input
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="e.g., Acme Corp"
                className="w-full p-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none"
              />
            </div>

            {/* JD Text Area */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Description <span className="text-red-500">*</span>
              </label>
              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste the full job description here...

Example:
We are seeking a talented Senior Backend Engineer...

Requirements:
- 5+ years of experience in backend development
- Strong proficiency in Python and Go
- Experience with microservices architecture
..."
                className="w-full h-64 p-4 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none resize-none"
              />
            </div>

            <div className="text-sm text-gray-500">
              Characters: {jdText.length} {jdText.length < 50 && '(minimum 50 required)'}
            </div>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {error}
              </div>
            )}

            <button
              onClick={handleAnalyze}
              disabled={jdText.length < 50 || !jobTitle || isAnalyzing}
              className={`w-full mt-6 py-4 rounded-full font-bold text-lg transition-all ${
                jdText.length < 50 || !jobTitle || isAnalyzing
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:shadow-lg hover:scale-105'
              }`}
            >
              {isAnalyzing ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing with GPT-4...
                </span>
              ) : (
                '🔍 Analyze Job Description'
              )}
            </button>
          </div>

          {/* Analysis Results */}
          <div className="bg-white rounded-3xl p-8 shadow-2xl overflow-y-auto max-h-[800px]">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Analysis Results</h2>

            {!analyzedJD ? (
              <div className="text-center text-gray-400 py-20">
                <svg className="w-24 h-24 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <p className="text-lg">Paste a job description to see analysis here</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Analysis Metadata */}
                {analyzedJD.analysis_metadata && (
                  <div className="flex items-center gap-2 text-sm">
                    {analyzedJD.cached && (
                      <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full font-medium">
                        ⚡ Cached Result
                      </span>
                    )}
                    <span className="text-gray-500">
                      Analyzed: {new Date(analyzedJD.analysis_metadata.analyzed_at).toLocaleString()}
                    </span>
                  </div>
                )}

                {/* JD Sections */}
                {analyzedJD.sections && (
                  <div className="border-b pb-6">
                    <h3 className="text-xl font-bold text-indigo-600 mb-4">📋 Job Description Sections</h3>

                    {/* Summary */}
                    {analyzedJD.sections.summary && (
                      <div className="mb-4">
                        <h4 className="font-semibold text-gray-700 mb-2">Summary</h4>
                        <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">{analyzedJD.sections.summary}</p>
                      </div>
                    )}

                    {/* Description */}
                    {analyzedJD.sections.description && (
                      <div className="mb-4">
                        <h4 className="font-semibold text-gray-700 mb-2">Description</h4>
                        <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">{analyzedJD.sections.description}</p>
                      </div>
                    )}

                    {/* Responsibilities */}
                    {analyzedJD.sections.responsibilities && analyzedJD.sections.responsibilities.length > 0 && (
                      <div className="mb-4">
                        <h4 className="font-semibold text-gray-700 mb-2">Responsibilities</h4>
                        <ul className="list-disc list-inside space-y-1 bg-blue-50 p-3 rounded-lg">
                          {analyzedJD.sections.responsibilities.map((resp, idx) => (
                            <li key={idx} className="text-sm text-gray-700">{resp}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Minimum Qualifications */}
                    {analyzedJD.sections.minimum_qualifications && analyzedJD.sections.minimum_qualifications.length > 0 && (
                      <div className="mb-4">
                        <h4 className="font-semibold text-red-700 mb-2">Minimum Qualifications <span className="text-red-600">*</span></h4>
                        <ul className="list-disc list-inside space-y-1 bg-red-50 p-3 rounded-lg border-2 border-red-200">
                          {analyzedJD.sections.minimum_qualifications.map((qual, idx) => (
                            <li key={idx} className="text-sm text-gray-700">{qual}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Preferred Qualifications */}
                    {analyzedJD.sections.preferred_qualifications && analyzedJD.sections.preferred_qualifications.length > 0 && (
                      <div className="mb-4">
                        <h4 className="font-semibold text-green-700 mb-2">Preferred Qualifications</h4>
                        <ul className="list-disc list-inside space-y-1 bg-green-50 p-3 rounded-lg">
                          {analyzedJD.sections.preferred_qualifications.map((qual, idx) => (
                            <li key={idx} className="text-sm text-gray-700">{qual}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Benefits */}
                    {analyzedJD.sections.benefits && analyzedJD.sections.benefits.length > 0 && (
                      <div className="mb-4">
                        <h4 className="font-semibold text-purple-700 mb-2">Benefits & Perks</h4>
                        <ul className="list-disc list-inside space-y-1 bg-purple-50 p-3 rounded-lg">
                          {analyzedJD.sections.benefits.map((benefit, idx) => (
                            <li key={idx} className="text-sm text-gray-700">{benefit}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* TOP 20 Keywords */}
                {analyzedJD.top_keywords && analyzedJD.top_keywords.length > 0 && (
                  <div className="border-b pb-6">
                    <h3 className="text-xl font-bold text-indigo-600 mb-4">🎯 TOP 20 Keywords</h3>
                    <div className="space-y-3">
                      {analyzedJD.top_keywords.map((kw, idx) => {
                        const typeColors = {
                          'technical_skill': 'bg-purple-100 text-purple-800',
                          'soft_skill': 'bg-green-100 text-green-800',
                          'tool': 'bg-blue-100 text-blue-800',
                          'certification': 'bg-yellow-100 text-yellow-800',
                          'domain_knowledge': 'bg-pink-100 text-pink-800'
                        };
                        return (
                          <div key={idx} className="flex items-center gap-3">
                            <span className="text-gray-500 text-sm font-mono w-6">{idx + 1}</span>
                            <div className="flex-1">
                              <div className="flex items-center justify-between mb-1">
                                <div className="flex items-center gap-2">
                                  <span className="font-semibold">{kw.keyword}</span>
                                  <span className={`px-2 py-0.5 rounded text-xs ${typeColors[kw.type]}`}>
                                    {kw.type.replace('_', ' ')}
                                  </span>
                                </div>
                                <span className="text-sm text-gray-500 font-medium">
                                  {(kw.weight * 100).toFixed(0)}%
                                </span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full transition-all"
                                  style={{ width: `${kw.weight * 100}%` }}
                                ></div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Required Skills */}
                {analyzedJD.required_skills && analyzedJD.required_skills.length > 0 && (
                  <div className="border-b pb-6">
                    <h3 className="text-xl font-bold text-indigo-600 mb-4">
                      Required Skills <span className="text-red-600">*</span>
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {analyzedJD.required_skills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium border-2 border-red-200"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Preferred Skills */}
                {analyzedJD.preferred_skills && analyzedJD.preferred_skills.length > 0 && (
                  <div className="border-b pb-6">
                    <h3 className="text-xl font-bold text-indigo-600 mb-4">Preferred Skills</h3>
                    <div className="flex flex-wrap gap-2">
                      {analyzedJD.preferred_skills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Job Requirements */}
                {analyzedJD.job_requirements && (
                  <div className="border-b pb-6">
                    <h3 className="text-xl font-bold text-indigo-600 mb-4">Job Requirements</h3>
                    <div className="space-y-3">
                      {analyzedJD.job_requirements.experience_years !== null && (
                        <div>
                          <p className="text-gray-500 text-sm font-medium">Experience</p>
                          <p className="font-semibold">{analyzedJD.job_requirements.experience_years}+ years</p>
                        </div>
                      )}
                      {analyzedJD.job_requirements.education && analyzedJD.job_requirements.education.length > 0 && (
                        <div>
                          <p className="text-gray-500 text-sm font-medium">Education</p>
                          <ul className="list-disc list-inside space-y-1">
                            {analyzedJD.job_requirements.education.map((edu, idx) => (
                              <li key={idx} className="text-sm">{edu}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {analyzedJD.job_requirements.responsibilities && analyzedJD.job_requirements.responsibilities.length > 0 && (
                        <div>
                          <p className="text-gray-500 text-sm font-medium">Key Responsibilities</p>
                          <ul className="list-disc list-inside space-y-1">
                            {analyzedJD.job_requirements.responsibilities.slice(0, 5).map((resp, idx) => (
                              <li key={idx} className="text-sm">{resp}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Continue Button */}
                <button
                  onClick={handleContinue}
                  className="w-full bg-gradient-to-r from-green-500 to-teal-600 text-white py-4 rounded-full font-bold text-lg hover:shadow-lg hover:scale-105 transition-all"
                >
                  Continue to Optimization →
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
