"use client"

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ResumePreview } from '../../components/ResumePreview';

export default function ResumePreviewPage() {
  const params = useParams();
  const router = useRouter();
  const template = params.template as string;
  
  const [resumeData, setResumeData] = useState<any>(null);
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);

  useEffect(() => {
    // 从 localStorage 获取简历数据
    const savedData = localStorage.getItem('resumeData');
    if (savedData) {
      setResumeData(JSON.parse(savedData));
    }
  }, []);

  

const handleDownload = async (format: 'pdf' | 'word') => {
  try {
    const response = await fetch(`http://localhost:8000/api/resume/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resumeData, template, format }),
      cache: 'no-store', // 防缓存干扰
    });

    if (!response.ok) {
      const errText = await response.text().catch(() => '');
      console.error('Generate failed:', response.status, response.statusText, errText);
      throw new Error(errText || `Generate failed: ${response.status} ${response.statusText}`);
    }

    // 默认文件名（兜底，避免空）
    let filename = `resume.${format === 'pdf' ? 'pdf' : 'docx'}`;

    // 优先从 Content-Disposition 取文件名
    const cd = response.headers.get('Content-Disposition');
    if (cd) {
      // 先尝试 filename*=UTF-8''xxx（更可靠，兼容中文）
      const mUtf8 = /filename\*=(?:UTF-8'')?([^;]+)/i.exec(cd);
      const mBasic = /filename="([^"]+)"/i.exec(cd);
      if (mUtf8) {
        try { filename = decodeURIComponent(mUtf8[1]); } catch { /* ignore */ }
      } else if (mBasic) {
        filename = mBasic[1];
      }
    } else {
      // 兜底再看 Content-Type
      const type = response.headers.get('Content-Type') || '';
      if (type.includes('pdf')) filename = 'resume.pdf';
      else if (type.includes('word')) filename = 'resume.docx';
    }

    // 下载文件
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename; //  这里用解析后的文件名
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);

    console.log(` Resume downloaded: ${filename}`);
  } catch (error) {
    console.error('Download failed:', error);
    alert('Failed to download resume. Please try again.');
  } finally {
    setShowDownloadMenu(false);
  }
};


  if (!resumeData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your resume...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-4">  {/* 改：max-w-4xl → max-w-5xl */}
        
        {/* 顶部标题 */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6 text-center">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🎉 YAY! You have your new resume
          </h1>
          <p className="text-gray-600">
            Review your resume and download it in your preferred format
          </p>
        </div>
  
        {/* 主内容区 - 简历预览和下载按钮 */}
        <div className="grid grid-cols-1 gap-6">
          
          {/* 简历预览区域 - 占满整个宽度 */}
          <div className="bg-gray-100 rounded-lg p-8 flex items-center justify-center min-h-[800px]">
            {/* 简历预览卡片 - 放大尺寸 */}
            <div className="bg-white rounded-lg shadow-2xl w-full max-w-3xl transform scale-110">
              <ResumePreview data={resumeData} template={template} />
            </div>
          </div>
  
          {/* 下载按钮区域 */}
          <div className="flex justify-center">
            <div className="relative">
              <button
                onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 text-lg font-semibold shadow-lg"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download
              </button>
  
              {/* 下载菜单 */}
              {showDownloadMenu && (
                <div className="absolute left-1/2 transform -translate-x-1/2 mt-2 w-56 bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-10">
                  <button
                    onClick={() => handleDownload('pdf')}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors flex items-center gap-3"
                  >
                    <svg className="w-6 h-6 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                    </svg>
                    <div>
                      <div className="font-semibold">Download as PDF</div>
                      <div className="text-xs text-gray-500">Best for sharing</div>
                    </div>
                  </button>
                  <button
                    onClick={() => handleDownload('word')}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors flex items-center gap-3"
                  >
                    <svg className="w-6 h-6 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                    </svg>
                    <div>
                      <div className="font-semibold">Download as Word</div>
                      <div className="text-xs text-gray-500">Easy to edit</div>
                    </div>
                  </button>
                </div>
              )}
            </div>
          </div>
  
          {/* 底部按钮 */}
          <div className="flex justify-center mt-4 mb-8">
            <button
              onClick={() => router.push(`/dashboard/resume/build/form/${template}`)}
              className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-gray-700"
            >
              ← Back to Edit
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}