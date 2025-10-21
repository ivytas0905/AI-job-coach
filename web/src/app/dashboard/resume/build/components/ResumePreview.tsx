
import React from 'react';

// 定义接口
interface ContactInfo {
  fullName: string;
  title: string;
  location: string;
  phone: string;
  email: string;
}

interface Experience {
  position: string;
  company: string;
  startDate: string;
  endDate: string;
  location: string;
  description: string;
}

interface Education {
  degree: string;
  school: string;
  startDate: string;
  endDate: string;
  location: string;
}

interface ResumeData {
  contact: ContactInfo;
  experience: Experience[];
  education: Education[];
  skills: string[];
  summary: string;
}

interface ResumePreviewProps {
  data: ResumeData;
  template: string;
}

export function ResumePreview({ data, template }: ResumePreviewProps) {
  const renderTemplate = () => {
    switch (template) {
      case 'simple':
        return <SimpleTemplate data={data} />;
      case 'professional':
        return <ProfessionalTemplate data={data} />;
      case 'modern':
        return <ModernTemplate data={data} />;
      default:
        return <SimpleTemplate data={data} />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-xl overflow-hidden border border-gray-200">
      {/* 预览标签 */}
      <div className="bg-gray-100 px-4 py-2 border-b border-gray-200">
        <p className="text-xs text-gray-600 font-medium">Preview</p>
      </div>
      
      {/* 修复缩放 - 使用正确的容器 */}
      <div className="overflow-auto bg-gray-100 p-4" style={{ maxHeight: 'calc(100vh - 180px)' }}>
        <div 
          className="origin-top-left mx-auto"
          style={{ 
            transform: 'scale(0.6)',
            transformOrigin: 'top left',
          }}
        >
          {renderTemplate()}
        </div>
      </div>
    </div>
  );
}

// ============ Simple 模板 ============
function SimpleTemplate({ data }: { data: ResumeData }) {
  return (
    <div className="w-[595px] min-h-[842px] bg-white p-12 shadow-lg">
      {/* 头部信息 */}
      <div className="text-center mb-8 pb-6 border-b-2 border-gray-800">
        <h1 className="text-4xl font-bold mb-2 tracking-tight">
          {data.contact.fullName || 'Your Name'}
        </h1>
        <p className="text-base text-gray-700 mb-2">
          {data.contact.title || 'Your Job Title'}
        </p>
        <div className="text-sm text-gray-600 flex justify-center gap-3 flex-wrap">
          {data.contact.location && <span>{data.contact.location}</span>}
          {data.contact.phone && (
            <>
              {data.contact.location && <span>•</span>}
              <span>{data.contact.phone}</span>
            </>
          )}
          {data.contact.email && (
            <>
              {(data.contact.location || data.contact.phone) && <span>•</span>}
              <span>{data.contact.email}</span>
            </>
          )}
        </div>
      </div>

      {/* Summary */}
      {data.summary && (
        <div className="mb-6">
          <h2 className="text-xl font-bold mb-3 uppercase tracking-wide">Summary</h2>
          <p className="text-sm text-gray-700 leading-relaxed">{data.summary}</p>
        </div>
      )}

      {/* Experience */}
      {data.experience && data.experience.length > 0 && data.experience.some(exp => exp.position || exp.company) && (
        <div className="mb-6">
          <h2 className="text-xl font-bold mb-4 uppercase tracking-wide">Experience</h2>
          <div className="space-y-5">
            {data.experience.map((exp, i) => (
              <div key={i}>
                <div className="flex justify-between items-start mb-1">
                  <div>
                    <h3 className="font-bold text-base">{exp.position || 'Position'}</h3>
                    <p className="text-sm text-gray-700">{exp.company || 'Company'}</p>
                  </div>
                  <div className="text-sm text-gray-600 text-right">
                    {exp.startDate && exp.endDate && (
                      <p>{exp.startDate} - {exp.endDate}</p>
                    )}
                    {exp.location && <p className="text-xs">{exp.location}</p>}
                  </div>
                </div>
                {exp.description && (
                  <div className="text-sm text-gray-700 mt-2 whitespace-pre-line leading-relaxed">
                    {exp.description}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Education */}
      {data.education && data.education.length > 0 && data.education.some(edu => edu.degree || edu.school) && (
        <div className="mb-6">
          <h2 className="text-xl font-bold mb-4 uppercase tracking-wide">Education</h2>
          <div className="space-y-3">
            {data.education.map((edu, i) => (
              <div key={i} className="flex justify-between">
                <div>
                  <h3 className="font-bold text-base">{edu.degree || 'Degree'}</h3>
                  <p className="text-sm text-gray-700">{edu.school || 'School'}</p>
                  {edu.location && <p className="text-xs text-gray-600">{edu.location}</p>}
                </div>
                {edu.startDate && edu.endDate && (
                  <div className="text-sm text-gray-600">
                    {edu.startDate} - {edu.endDate}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Skills */}
      {data.skills && Array.isArray(data.skills) && data.skills.length > 0 && (
        <div>
          <h2 className="text-xl font-bold mb-3 uppercase tracking-wide">Skills</h2>
          <p className="text-sm text-gray-700">{data.skills.join(' • ')}</p>
        </div>
      )}
    </div>
  );
}

// ============ Professional 模板 ============
function ProfessionalTemplate({ data }: { data: ResumeData }) {
  return (
    <div className="w-[595px] min-h-[842px] bg-white border-8 border-blue-900 shadow-lg">
      {/* 头部 - 深蓝色背景 */}
      <div className="bg-blue-900 text-white px-12 py-8 text-center">
        <h1 className="text-4xl font-bold mb-2">
          {data.contact.fullName || 'Your Name'}
        </h1>
        <p className="text-base opacity-90 mb-3">
          {data.contact.title || 'Your Job Title'}
        </p>
        <div className="text-sm opacity-80 flex justify-center gap-3 flex-wrap">
          {data.contact.location && <span>{data.contact.location}</span>}
          {data.contact.phone && (
            <>
              {data.contact.location && <span>•</span>}
              <span>{data.contact.phone}</span>
            </>
          )}
          {data.contact.email && (
            <>
              {(data.contact.location || data.contact.phone) && <span>•</span>}
              <span>{data.contact.email}</span>
            </>
          )}
        </div>
      </div>

      {/* 内容区域 */}
      <div className="px-12 py-8">
        {/* Summary */}
        {data.summary && (
          <div className="mb-6">
            <h2 className="text-xl font-bold mb-3 text-blue-900 uppercase border-b-2 border-blue-900 pb-1">
              Summary
            </h2>
            <p className="text-sm text-gray-700 leading-relaxed">{data.summary}</p>
          </div>
        )}

        {/* Experience */}
        {data.experience && data.experience.length > 0 && data.experience.some(exp => exp.position || exp.company) && (
          <div className="mb-6">
            <h2 className="text-xl font-bold mb-4 text-blue-900 uppercase border-b-2 border-blue-900 pb-1">
              Experience
            </h2>
            <div className="space-y-5">
              {data.experience.map((exp, i) => (
                <div key={i}>
                  <div className="flex justify-between items-start mb-1">
                    <div>
                      <h3 className="font-bold text-base text-blue-900">{exp.position || 'Position'}</h3>
                      <p className="text-sm text-gray-700 italic">{exp.company || 'Company'}</p>
                    </div>
                    <div className="text-sm text-gray-600 text-right">
                      {exp.startDate && exp.endDate && (
                        <p>{exp.startDate} - {exp.endDate}</p>
                      )}
                      {exp.location && <p className="text-xs">{exp.location}</p>}
                    </div>
                  </div>
                  {exp.description && (
                    <div className="text-sm text-gray-700 mt-2 whitespace-pre-line leading-relaxed">
                      {exp.description}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Education */}
        {data.education && data.education.length > 0 && data.education.some(edu => edu.degree || edu.school) && (
          <div className="mb-6">
            <h2 className="text-xl font-bold mb-4 text-blue-900 uppercase border-b-2 border-blue-900 pb-1">
              Education
            </h2>
            <div className="space-y-3">
              {data.education.map((edu, i) => (
                <div key={i} className="flex justify-between">
                  <div>
                    <h3 className="font-bold text-base">{edu.degree || 'Degree'}</h3>
                    <p className="text-sm text-gray-700">{edu.school || 'School'}</p>
                    {edu.location && <p className="text-xs text-gray-600">{edu.location}</p>}
                  </div>
                  {edu.startDate && edu.endDate && (
                    <div className="text-sm text-gray-600">
                      {edu.startDate} - {edu.endDate}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Skills */}
        {data.skills && Array.isArray(data.skills) && data.skills.length > 0 && (
          <div>
            <h2 className="text-xl font-bold mb-3 text-blue-900 uppercase border-b-2 border-blue-900 pb-1">
              Skills
            </h2>
            <p className="text-sm text-gray-700">{data.skills.join(' • ')}</p>
          </div>
        )}
      </div>
    </div>
  );
}

// ============ Modern 模板 ============
function ModernTemplate({ data }: { data: ResumeData }) {
  return (
    <div className="w-[595px] min-h-[842px] bg-gray-50 shadow-lg">
      {/* 头部 - 渐变灰色背景 */}
      <div className="bg-gradient-to-r from-gray-700 to-gray-900 px-12 py-10">
        <h1 className="text-4xl font-bold text-white mb-2">
          {data.contact.fullName || 'Your Name'}
        </h1>
        <p className="text-xl text-blue-400 mb-4">
          {data.contact.title || 'Your Job Title'}
        </p>
        <div className="text-sm text-gray-300 flex gap-4 flex-wrap">
          {data.contact.location && <span>📍 {data.contact.location}</span>}
          {data.contact.phone && <span>📞 {data.contact.phone}</span>}
          {data.contact.email && <span>✉️ {data.contact.email}</span>}
        </div>
      </div>

      {/* 内容区域 */}
      <div className="px-12 py-8 bg-white">
        {/* Summary */}
        {data.summary && (
          <div className="mb-6">
            <h2 className="text-lg font-bold mb-3 text-gray-800 flex items-center gap-2">
              <span className="w-1 h-6 bg-blue-500"></span>
              SUMMARY
            </h2>
            <p className="text-sm text-gray-700 leading-relaxed pl-3">{data.summary}</p>
          </div>
        )}

        {/* Experience */}
        {data.experience && data.experience.length > 0 && data.experience.some(exp => exp.position || exp.company) && (
          <div className="mb-6">
            <h2 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
              <span className="w-1 h-6 bg-blue-500"></span>
              EXPERIENCE
            </h2>
            <div className="space-y-5 pl-3">
              {data.experience.map((exp, i) => (
                <div key={i}>
                  <div className="flex justify-between items-start mb-1">
                    <div>
                      <h3 className="font-bold text-base text-gray-900">{exp.position || 'Position'}</h3>
                      <p className="text-sm text-blue-600 font-medium">{exp.company || 'Company'}</p>
                    </div>
                    <div className="text-sm text-gray-500 text-right">
                      {exp.startDate && exp.endDate && (
                        <p className="font-medium">{exp.startDate} - {exp.endDate}</p>
                      )}
                      {exp.location && <p className="text-xs">{exp.location}</p>}
                    </div>
                  </div>
                  {exp.description && (
                    <div className="text-sm text-gray-700 mt-2 whitespace-pre-line leading-relaxed">
                      {exp.description}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Education */}
        {data.education && data.education.length > 0 && data.education.some(edu => edu.degree || edu.school) && (
          <div className="mb-6">
            <h2 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
              <span className="w-1 h-6 bg-blue-500"></span>
              EDUCATION
            </h2>
            <div className="space-y-3 pl-3">
              {data.education.map((edu, i) => (
                <div key={i} className="flex justify-between">
                  <div>
                    <h3 className="font-bold text-base">{edu.degree || 'Degree'}</h3>
                    <p className="text-sm text-gray-700">{edu.school || 'School'}</p>
                    {edu.location && <p className="text-xs text-gray-600">{edu.location}</p>}
                  </div>
                  {edu.startDate && edu.endDate && (
                    <div className="text-sm text-gray-500 font-medium">
                      {edu.startDate} - {edu.endDate}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Skills */}
        {data.skills && Array.isArray(data.skills) && data.skills.length > 0 && (
          <div>
            <h2 className="text-lg font-bold mb-3 text-gray-800 flex items-center gap-2">
              <span className="w-1 h-6 bg-blue-500"></span>
              SKILLS
            </h2>
            <div className="flex flex-wrap gap-2 pl-3">
              {data.skills.map((skill, i) => (
                <span
                  key={i}
                  className="text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded-full border border-gray-300"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}