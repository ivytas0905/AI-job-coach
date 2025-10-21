// pages/build-resume/components/steps/SkillsStep.tsx
import { useState, KeyboardEvent } from 'react';
import { ResumeData } from '../../form/[template]';

interface SkillsStepProps {
  data: ResumeData;
  onChange: (section: 'skills', data: any) => void;
}

export function SkillsStep({ data, onChange }: SkillsStepProps) {
  const [skills, setSkills] = useState<string[]>(
    data.skills.length > 0 ? data.skills : []
  );
  const [inputValue, setInputValue] = useState('');

  const handleAddSkill = () => {
    const trimmed = inputValue.trim();
    if (trimmed && !skills.includes(trimmed)) {
      const updated = [...skills, trimmed];
      setSkills(updated);
      onChange('skills', updated);
      setInputValue('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddSkill();
    }
  };

  const removeSkill = (index: number) => {
    const updated = skills.filter((_, i) => i !== index);
    setSkills(updated);
    onChange('skills', updated);
  };

  // 常用技能建议
  const suggestedSkills = [
    'JavaScript',
    'Python',
    'React',
    'Node.js',
    'TypeScript',
    'SQL',
    'Git',
    'AWS',
    'Communication',
    'Leadership',
    'Project Management',
    'Problem Solving',
  ];

  const addSuggestedSkill = (skill: string) => {
    if (!skills.includes(skill)) {
      const updated = [...skills, skill];
      setSkills(updated);
      onChange('skills', updated);
    }
  };

  return (
    <div className="space-y-6">
      <p className="text-sm text-gray-600">
        Add skills relevant to the job you're applying for. Include both technical skills and soft skills.
      </p>

      {/* 输入框 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Add Your Skills
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g., JavaScript, Leadership, etc."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            onClick={handleAddSkill}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Add
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Press Enter or click Add to add a skill
        </p>
      </div>

      {/* 已添加的技能 */}
      {skills.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">
            Your Skills ({skills.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {skills.map((skill, index) => (
              <div
                key={index}
                className="group flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-full border border-blue-200 hover:bg-blue-100 transition-colors"
              >
                <span className="text-sm font-medium">{skill}</span>
                <button
                  onClick={() => removeSkill(index)}
                  className="text-blue-600 hover:text-red-600 transition-colors"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 推荐技能 */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">
          Suggested Skills (click to add)
        </h3>
        <div className="flex flex-wrap gap-2">
          {suggestedSkills
            .filter((skill) => !skills.includes(skill))
            .map((skill, index) => (
              <button
                key={index}
                onClick={() => addSuggestedSkill(skill)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-full border border-gray-300 hover:bg-blue-50 hover:text-blue-600 hover:border-blue-300 transition-all text-sm"
              >
                + {skill}
              </button>
            ))}
        </div>
      </div>
    </div>
  );
}