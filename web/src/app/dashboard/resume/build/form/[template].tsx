// pages/build-resume/form/[template].tsx
import { useState } from 'react';
import { useRouter } from 'next/router';
import { ContactStep } from '../components/steps/ContactStep';
import { ExperienceStep } from '../components/steps/ExperienceStep';
import { EducationStep } from '../components/steps/EducationStep';
import { SkillsStep } from '../components/steps/SkillsStep';
import { SummaryStep } from '../components/steps/SummaryStep';
import { ResumePreview } from '../components/ResumePreview';

export interface ResumeData {
  contact: {
    fullName: string;
    title: string;
    location: string;
    phone: string;
    email: string;
  };
  experience: Array<{
    position: string;
    company: string;
    startDate: string;
    endDate: string;
    location: string;
    description: string;
  }>;
  education: Array<{
    degree: string;
    school: string;
    startDate: string;
    endDate: string;
    location: string;
  }>;
  skills: string[];
  summary: string;
}

export default function ResumeFormPage() {
  const router = useRouter();
  const { template } = router.query; // 获取选中的模板

  const [currentStep, setCurrentStep] = useState(0);
  const [resumeData, setResumeData] = useState<ResumeData>({
    contact: {
      fullName: '',
      title: '',
      location: '',
      phone: '',
      email: '',
    },
    experience: [],
    education: [],
    skills: [],
    summary: '',
  });

  const steps = [
    { component: ContactStep, title: 'Contact Information' },
    { component: ExperienceStep, title: 'Work Experience' },
    { component: EducationStep, title: 'Education' },
    { component: SkillsStep, title: 'Skills' },
    { component: SummaryStep, title: 'Summary' },
  ];

  const CurrentStepComponent = steps[currentStep].component;

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // 最后一步完成
      handleFinish();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    } else {
      // 第一步返回 = 返回模板选择页
      router.push('/build-resume');
    }
  };

  const handleFinish = async () => {
    // TODO: 提交数据到后端
    console.log('Resume completed:', resumeData);
    // router.push('/resume/preview'); // 跳转到预览页或下载页
  };

  const updateResumeData = (section: keyof ResumeData, data: unknown) => {
    setResumeData((prev) => ({
      ...prev,
      [section]: data,
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部进度条 */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              Step {currentStep + 1} of {steps.length}
            </div>
            <div className="flex-1 mx-8">
              <div className="h-2 bg-gray-200 rounded-full">
                <div
                  className="h-2 bg-blue-600 rounded-full transition-all duration-300"
                  style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
                />
              </div>
            </div>
            <div className="text-sm text-gray-500">
              Template: <span className="font-medium capitalize">{template}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* 左侧表单 - 7列 */}
          <div className="col-span-7">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold mb-6">
                {steps[currentStep].title}
              </h2>

              <CurrentStepComponent
                data={resumeData}
                onChange={updateResumeData}
              />

              {/* 底部导航按钮 */}
              <div className="flex justify-between mt-8 pt-6 border-t">
                <button
                  onClick={handlePrevious}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  {currentStep === 0 ? 'Back to Templates' : 'Previous'}
                </button>
                <button
                  onClick={handleNext}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {currentStep === steps.length - 1 ? 'Finish' : 'Next'}
                </button>
              </div>
            </div>
          </div>

          {/* 右侧预览 - 5列 */}
          <div className="col-span-5">
            <div className="sticky top-8">
              <ResumePreview 
                data={resumeData} 
                template={template as string} 
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}