
import { useState } from 'react';
import { ResumeData } from '../../form/[template]';

interface SummaryStepProps {
  data: ResumeData;
  onChange: (section: 'summary', data: any) => void;
}

export function SummaryStep({ data, onChange }: SummaryStepProps) {
  const [summary, setSummary] = useState(data.summary || '');
  const [enhancing, setEnhancing] = useState(false);

  const handleChange = (value: string) => {
    setSummary(value);
    onChange('summary', value);
  };

  const handleAIEnhance = async () => {
    if (!summary.trim()) {
      alert('Please enter a summary first');
      return;
    }

    setEnhancing(true);

    try {
      const response = await fetch('/api/resume/enhance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: summary }),
      });

      if (!response.ok) {
        throw new Error('Enhancement failed');
      }

      const { enhanced } = await response.json();
      handleChange(enhanced);
    } catch (error) {
      console.error('AI enhancement failed:', error);
      alert('Failed to enhance content. Please try again.');
    } finally {
      setEnhancing(false);
    }
  };

  const exampleSummary = `Experienced software engineer with 5+ years of expertise in full-stack development. Proven track record of delivering scalable applications and leading cross-functional teams. Passionate about clean code and innovative solutions.`;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-gray-600 mb-4">
          Write a brief summary that highlights your professional experience, key skills, and career objectives. This is your elevator pitch!
        </p>

        {/* AI 增强按钮 */}
        <div className="flex justify-between items-center mb-2">
          <label className="text-sm font-medium text-gray-700">
            Professional Summary
          </label>
          <button
            onClick={handleAIEnhance}
            disabled={enhancing}
            className="flex items-center gap-2 px-4 py-1.5 bg-gradient-to-r from-purple-600 to-blue-600 text-white text-sm rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {enhancing ? (
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
          value={summary}
          onChange={(e) => handleChange(e.target.value)}
          rows={6}
          placeholder="Write a brief professional summary about yourself..."
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        />

        <div className="flex justify-between items-center mt-2">
          <p className="text-xs text-gray-500">
            Tip: Keep it concise (2-4 sentences) and highlight your most relevant qualifications
          </p>
          <p className="text-xs text-gray-500">
            {summary.length} characters
          </p>
        </div>
      </div>

      {/* 示例 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">
          💡 Example Summary
        </h3>
        <p className="text-sm text-gray-700 italic">
          "{exampleSummary}"
        </p>
      </div>

      {/* 完成提示 */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-green-900 mb-2">
          🎉 Almost Done!
        </h3>
        <p className="text-sm text-gray-700">
          After completing this step, you can review your resume and download it in your preferred format.
        </p>
      </div>
    </div>
  );
}