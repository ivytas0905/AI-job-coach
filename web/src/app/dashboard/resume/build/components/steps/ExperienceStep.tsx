
import { useState } from 'react';
import { ResumeData } from '../../form/[template]/page';

interface ExperienceStepProps {
  data: ResumeData;
  onChange: (section: 'experience', data: unknown) => void;
}

export function ExperienceStep({ data, onChange }: ExperienceStepProps) {
  const [experiences, setExperiences] = useState(
    data.experience.length > 0
      ? data.experience
      : [
          {
            position: '',
            company: '',
            startDate: '',
            endDate: '',
            location: '',
            description: '',
          },
        ]
  );

  const [enhancing, setEnhancing] = useState<number | null>(null);

  const handleChange = (index: number, field: string, value: string) => {
    const updated = [...experiences];
    updated[index] = { ...updated[index], [field]: value };
    setExperiences(updated);
    onChange('experience', updated);
  };

  const addExperience = () => {
    const newExp = {
      position: '',
      company: '',
      startDate: '',
      endDate: '',
      location: '',
      description: '',
    };
    const updated = [...experiences, newExp];
    setExperiences(updated);
    onChange('experience', updated);
  };

  const removeExperience = (index: number) => {
    if (experiences.length === 1) {
      // 至少保留一个
      return;
    }
    const updated = experiences.filter((_, i) => i !== index);
    setExperiences(updated);
    onChange('experience', updated);
  };

  // AI 优化功能
  const handleAIEnhance = async (index: number) => {
    const description = experiences[index].description;
    
    if (!description.trim()) {
      alert('Please enter a description first');
      return;
    }

    setEnhancing(index);

    try {
      const response = await fetch('/api/resume/enhance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: description }),
      });

      if (!response.ok) {
        throw new Error('Enhancement failed');
      }

      const { enhanced } = await response.json();
      handleChange(index, 'description', enhanced);
    } catch (error) {
      console.error('AI enhancement failed:', error);
      alert('Failed to enhance content. Please try again.');
    } finally {
      setEnhancing(null);
    }
  };

  return (
    <div className="space-y-6">
      {experiences.map((exp, index) => (
        <div
          key={index}
          className="p-5 border-2 border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
        >
          {/* 标题 */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-700">
              Experience {index + 1}
            </h3>
            {experiences.length > 1 && (
              <button
                onClick={() => removeExperience(index)}
                className="text-red-600 text-sm hover:text-red-700 font-medium"
              >
                Remove
              </button>
            )}
          </div>

          {/* 职位和公司 */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={exp.position}
                onChange={(e) => handleChange(index, 'position', e.target.value)}
                placeholder="e.g., Software Engineer"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={exp.company}
                onChange={(e) => handleChange(index, 'company', e.target.value)}
                placeholder="e.g., Verizon Wireless"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* 日期和地点 */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="text"
                value={exp.startDate}
                onChange={(e) => handleChange(index, 'startDate', e.target.value)}
                placeholder="e.g., Jun 2013"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="text"
                value={exp.endDate}
                onChange={(e) => handleChange(index, 'endDate', e.target.value)}
                placeholder="e.g., Mar 2017 or Present"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location
              </label>
              <input
                type="text"
                value={exp.location}
                onChange={(e) => handleChange(index, 'location', e.target.value)}
                placeholder="e.g., San Francisco, CA"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* 工作描述 */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-medium text-gray-700">
                Job Description
              </label>
              <button
                onClick={() => handleAIEnhance(index)}
                disabled={enhancing === index}
                className="flex items-center gap-2 px-4 py-1.5 bg-gradient-to-r from-purple-600 to-blue-600 text-white text-sm rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {enhancing === index ? (
                  <>
                    <span className="animate-spin">⚙️</span>
                    Enhancing...
                  </>
                ) : (
                  <>
                    ✨ AI Enhance
                  </>
                )}
              </button>
            </div>
            <textarea
              value={exp.description}
              onChange={(e) => handleChange(index, 'description', e.target.value)}
              rows={6}
              placeholder="Describe your responsibilities and achievements...&#10;&#10;Example:&#10;• Developed and maintained scalable software applications&#10;• Collaborated with cross-functional teams&#10;• Led code reviews and mentored junior engineers"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
            <p className="text-xs text-gray-500 mt-1">
              Tip: Use bullet points to highlight your key achievements
            </p>
          </div>
        </div>
      ))}

      {/* 添加更多经历 */}
      <button
        onClick={addExperience}
        className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50 transition-all font-medium"
      >
        + Add Another Experience
      </button>
    </div>
  );
}