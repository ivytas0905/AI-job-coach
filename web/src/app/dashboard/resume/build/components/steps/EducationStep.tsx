
import { useState } from 'react';
import { ResumeData } from '../../form/[template]/page';

interface EducationStepProps {
  data: ResumeData;
  onChange: (section: 'education', data: unknown) => void;
}

export function EducationStep({ data, onChange }: EducationStepProps) {
  const [educations, setEducations] = useState(
    data.education.length > 0
      ? data.education
      : [
          {
            degree: '',
            school: '',
            startDate: '',
            endDate: '',
            location: '',
          },
        ]
  );

  const handleChange = (index: number, field: string, value: string) => {
    const updated = [...educations];
    updated[index] = { ...updated[index], [field]: value };
    setEducations(updated);
    onChange('education', updated);
  };

  const addEducation = () => {
    const newEdu = {
      degree: '',
      school: '',
      startDate: '',
      endDate: '',
      location: '',
    };
    const updated = [...educations, newEdu];
    setEducations(updated);
    onChange('education', updated);
  };

  const removeEducation = (index: number) => {
    if (educations.length === 1) {
      return;
    }
    const updated = educations.filter((_, i) => i !== index);
    setEducations(updated);
    onChange('education', updated);
  };

  return (
    <div className="space-y-6">
      <p className="text-sm text-gray-600">
        Add your most recent education first. If you have multiple degrees, only add the most recent and relevant ones.
      </p>

      {educations.map((edu, index) => (
        <div
          key={index}
          className="p-5 border-2 border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
        >
          {/* 标题 */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-700">
              Education {index + 1}
            </h3>
            {educations.length > 1 && (
              <button
                onClick={() => removeEducation(index)}
                className="text-red-600 text-sm hover:text-red-700 font-medium"
              >
                Remove
              </button>
            )}
          </div>

          {/* 学位和学校 */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Degree <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={edu.degree}
                onChange={(e) => handleChange(index, 'degree', e.target.value)}
                placeholder="e.g., Bachelor of Science"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                e.g., Bachelor&apos;s, Master&apos;s, PhD
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                School/University <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={edu.school}
                onChange={(e) => handleChange(index, 'school', e.target.value)}
                placeholder="e.g., Northeastern University"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* 地点 */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Location
            </label>
            <input
              type="text"
              value={edu.location}
              onChange={(e) => handleChange(index, 'location', e.target.value)}
              placeholder="e.g., San Francisco, CA"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* 日期 */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="text"
                value={edu.startDate}
                onChange={(e) => handleChange(index, 'startDate', e.target.value)}
                placeholder="e.g., 2019 or Sep 2019"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Graduation Date
              </label>
              <input
                type="text"
                value={edu.endDate}
                onChange={(e) => handleChange(index, 'endDate', e.target.value)}
                placeholder="e.g., 2023 or Expected 2025"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>
      ))}

      {/* 添加更多教育经历 */}
      <button
        onClick={addEducation}
        className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50 transition-all font-medium"
      >
        + Add Another Education
      </button>
    </div>
  );
}