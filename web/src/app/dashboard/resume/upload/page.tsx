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
      setParsedData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while parsing your resume');
      console.error('Upload error:', err);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => router.back()}
            className="bg-white bg-opacity-20 text-white px-6 py-3 rounded-full hover:bg-opacity-30 transition-all backdrop-blur-sm"
          >
            ← Back
          </button>
          <h1 className="text-4xl font-bold text-white">Upload & Parse Resume</h1>
          <div className="w-24"></div>
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
            ) : (
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
                        {exp.description && <p className="text-sm text-gray-700 mt-2">{exp.description}</p>}
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
                  <div>
                    <h3 className="text-xl font-bold text-indigo-600 mb-4">Skills</h3>
                    <div className="flex flex-wrap gap-2">
                      {parsedData.skills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm font-medium"
                        >
                          {skill.name}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
