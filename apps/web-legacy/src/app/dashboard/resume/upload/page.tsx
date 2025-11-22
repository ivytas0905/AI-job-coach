'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

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
  raw_text?: string;
}

export default function UploadResumePage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [parsedData, setParsedData] = useState<ParsedResume | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [isSavingMaster, setIsSavingMaster] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (selectedFile: File) => {
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];

    if (!validTypes.includes(selectedFile.type)) {
      setError('Please upload a PDF or DOCX file');
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setFile(selectedFile);
    setError(null);
    setParsedData(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/v1/parse/resume', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to parse resume');
      }

      const data: ParsedResume = await response.json();
      console.log('Parsed resume data:', data);
      setParsedData(data);

      // Save parsed resume to session storage for optimization workflow
      sessionStorage.setItem('parsed_resume', JSON.stringify(data));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while parsing your resume');
      console.error('Upload error:', err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSaveAsMaster = async () => {
    if (!parsedData) return;

    setIsSavingMaster(true);
    setError(null);

    try {
      // Convert parsed resume to Master Resume format
      const masterResume = {
        personal_info: parsedData.personal_info,
        experiences: parsedData.experience?.map(exp => ({
          company: exp.company,
          title: exp.title,
          location: exp.location,
          start_date: exp.start_date,
          end_date: exp.end_date,
          description: exp.description,
          bullets: exp.description
            ? exp.description
                .split(/[.!]\s+/)
                .filter(text => text.trim().length > 10)
                .map(text => ({
                  text: text.trim().endsWith('.') ? text.trim() : text.trim() + '.',
                  keywords: [],
                  skills_used: []
                }))
            : [],
          skills_used: [],
          industry: ''
        })) || [],
        education: parsedData.education?.map(edu => ({
          school: edu.school,
          degree: edu.degree,
          start_date: edu.start_date,
          end_date: edu.end_date,
          description: edu.description
        })) || [],
        skills: parsedData.skills?.map(skill => ({
          name: skill.name,
          category: skill.category || 'general'
        })) || []
      };

      const response = await fetch('http://localhost:8000/api/v1/master/resume', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(masterResume),
      });

      if (!response.ok) {
        throw new Error('Failed to save Master Resume');
      }

      const data = await response.json();

      if (data.success && data.master_resume.id) {
        sessionStorage.setItem('master_resume_id', data.master_resume.id);
        alert('✅ Master Resume saved successfully! You can now proceed to analyze a Job Description.');
        router.push('/dashboard/resume/jd-input');
      } else {
        throw new Error(data.error || 'Failed to save Master Resume');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while saving Master Resume');
      console.error('Save Master error:', err);
    } finally {
      setIsSavingMaster(false);
    }
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
          <h1 className="text-4xl font-bold text-white">Upload & Parse Resume</h1>
          <div className="w-32"></div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="bg-white rounded-3xl p-8 shadow-2xl">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Upload Your Resume</h2>

            {/* Drag & Drop Zone */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`border-3 border-dashed rounded-2xl p-12 text-center transition-all ${
                dragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 bg-gray-50'
              }`}
            >
              <div className="mb-4">
                <svg
                  className="w-16 h-16 mx-auto text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>

              <p className="text-lg font-medium text-gray-700 mb-2">
                {file ? file.name : 'Drag and drop your resume here'}
              </p>
              <p className="text-sm text-gray-500 mb-4">
                or click to browse
              </p>

              <input
                type="file"
                id="fileInput"
                className="hidden"
                accept=".pdf,.docx,.doc"
                onChange={handleFileChange}
              />

              <label
                htmlFor="fileInput"
                className="inline-block bg-indigo-500 text-white px-6 py-3 rounded-full cursor-pointer hover:bg-indigo-600 transition-colors"
              >
                Choose File
              </label>

              <p className="text-xs text-gray-400 mt-4">
                Supported formats: PDF, DOCX (Max 10MB)
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {error}
              </div>
            )}

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={!file || isUploading}
              className={`w-full mt-6 py-4 rounded-full font-bold text-lg transition-all ${
                !file || isUploading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:shadow-lg hover:scale-105'
              }`}
            >
              {isUploading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Parsing Resume...
                </span>
              ) : (
                'Parse Resume'
              )}
            </button>
          </div>

          {/* Results Section */}
          <div className="bg-white rounded-3xl p-8 shadow-2xl overflow-y-auto max-h-[800px]">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Parsed Results</h2>

            {!parsedData ? (
              <div className="text-center text-gray-400 py-20">
                <svg className="w-24 h-24 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-lg">Upload a resume to see parsed data here</p>
              </div>
            ) : parsedData && (parsedData.personal_info || parsedData.experience?.length > 0 || parsedData.education?.length > 0 || parsedData.skills?.length > 0) ? (
              <div className="space-y-6">
                {/* Personal Info */}
                {parsedData.personal_info && (
                  <div className="border-b pb-6">
                    <h3 className="text-xl font-bold text-indigo-600 mb-4">Personal Information</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      {parsedData.personal_info.name && (
                        <div>
                          <p className="text-gray-500">Name</p>
                          <p className="font-medium">{parsedData.personal_info.name}</p>
                        </div>
                      )}
                      {parsedData.personal_info.email && (
                        <div>
                          <p className="text-gray-500">Email</p>
                          <p className="font-medium">{parsedData.personal_info.email}</p>
                        </div>
                      )}
                      {parsedData.personal_info.phone && (
                        <div>
                          <p className="text-gray-500">Phone</p>
                          <p className="font-medium">{parsedData.personal_info.phone}</p>
                        </div>
                      )}
                      {parsedData.personal_info.linkedin && (
                        <div>
                          <p className="text-gray-500">LinkedIn</p>
                          <p className="font-medium text-blue-600 truncate">{parsedData.personal_info.linkedin}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Experience */}
                {parsedData.experience && parsedData.experience.length > 0 && (
                  <div className="border-b pb-6">
                    <h3 className="text-xl font-bold text-indigo-600 mb-4">Experience</h3>
                    {parsedData.experience.map((exp, idx) => (
                      <div key={idx} className="mb-4 last:mb-0">
                        <p className="font-bold text-gray-800">{exp.title}</p>
                        <p className="text-sm text-gray-600">{exp.company} {exp.location && `• ${exp.location}`}</p>
                        <p className="text-xs text-gray-500">{exp.start_date} - {exp.end_date}</p>
                        {exp.description && (
                          <ul className="mt-2 space-y-1">
                            {exp.description.split('\n').map((bullet, bIdx) => (
                              <li key={bIdx} className="text-sm text-gray-700 flex items-start gap-2">
                                <span className="text-indigo-500 mt-1">•</span>
                                <span>{bullet}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Education */}
                {parsedData.education && parsedData.education.length > 0 && (
                  <div className="border-b pb-6">
                    <h3 className="text-xl font-bold text-indigo-600 mb-4">Education</h3>
                    {parsedData.education.map((edu, idx) => (
                      <div key={idx} className="mb-4 last:mb-0">
                        <p className="font-bold text-gray-800">{edu.school}</p>
                        <p className="text-sm text-gray-600">{edu.degree}</p>
                        <p className="text-xs text-gray-500">{edu.start_date} - {edu.end_date}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Skills */}
                {parsedData.skills && parsedData.skills.length > 0 && (
                  <div className="border-b pb-6">
                    <h3 className="text-xl font-bold text-indigo-600 mb-4">Skills</h3>
                    <div className="space-y-3">
                      {(() => {
                        // Group skills by category
                        const groupedSkills: Record<string, string[]> = {};
                        parsedData.skills.forEach(skill => {
                          const category = skill.category || 'Other';
                          if (!groupedSkills[category]) {
                            groupedSkills[category] = [];
                          }
                          groupedSkills[category].push(skill.name);
                        });

                        // Render each category
                        return Object.entries(groupedSkills).map(([category, skills]) => (
                          <div key={category}>
                            <p className="text-sm font-semibold text-gray-700 mb-2">{category}:</p>
                            <div className="flex flex-wrap gap-2 ml-4">
                              {skills.map((skillName, idx) => (
                                <span
                                  key={idx}
                                  className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm font-medium"
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

                {/* Save as Master Resume Button */}
                <button
                  onClick={handleSaveAsMaster}
                  disabled={isSavingMaster}
                  className={`w-full py-4 rounded-full font-bold text-lg transition-all shadow-lg ${
                    isSavingMaster
                      ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                      : 'bg-gradient-to-r from-emerald-500 via-green-500 to-teal-500 text-white hover:from-emerald-600 hover:via-green-600 hover:to-teal-600 hover:shadow-xl hover:scale-105'
                  }`}
                >
                  {isSavingMaster ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin h-6 w-6 mr-3" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span className="text-white">Saving Master Resume...</span>
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                      </svg>
                      <span>Save as Master Resume</span>
                    </span>
                  )}
                </button>
              </div>
            ) : (
              <div className="text-center text-gray-400 py-20">
                <p className="text-lg">Resume parsed but no data extracted. Please try a different file.</p>
                <p className="text-sm mt-2">Make sure your resume contains clear sections for experience, education, and skills.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
