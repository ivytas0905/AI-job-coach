"use client"
import { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { ContactStep } from '../../components/steps/ContactStep';
import { ExperienceStep } from '../../components/steps/ExperienceStep';
import { EducationStep } from '../../components/steps/EducationStep';
import { SkillsStep } from '../../components/steps/SkillsStep';
import { SummaryStep } from '../../components/steps/SummaryStep';
import { ResumePreview } from '../../components/ResumePreview';

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
  targetJob:string;
}

export default function ResumeFormPage() {
  const router = useRouter();
  const params = useParams();
  const template = params.template as string;

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
    targetJob: '',
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const steps = [
    { component: ContactStep, title: 'Contact Information' },
    { component: ExperienceStep, title: 'Work Experience' },
    { component: EducationStep, title: 'Education' },
    { component: SkillsStep, title: 'Skills' },
    { component: SummaryStep, title: 'Summary' },
  ];

  const CurrentStepComponent = steps[currentStep].component;
  //添加验证函数
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    //validate Contact
    if (!resumeData.contact.fullName) {
      newErrors.fullName = 'Full name is required';
    }
    if (!resumeData.contact.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(resumeData.contact.email)) {
      newErrors.email = 'Invalid email format';
    }
    if(!resumeData.contact.phone) {
      newErrors.phone = 'Phone is required';
    }
    // 此处可不用验证 Experience，不能假定用户一定有工作经验
    // if (resumeData.experience.length === 0) {
    //   newErrors.experience = 'Add at least one work experience';
    // }
    
    //validate Education
    if (resumeData.education.length === 0) {
      newErrors.education = 'Add at least one education entry';
    }
    // 验证 Skills
    if (resumeData.skills.length === 0) {
      newErrors.skills = 'Add at least one skill';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

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
      router.push('/dashboard/resume/build');
    }
  };

  // const handleFinish = async () => {
  //   if(!validateForm()){
  //     alert('Please fill in all required contents before finishing.');
  //     return;
  //   }
  //   setIsSubmitting(true);
  //   try {
  //     // 调用 build API
  //     const response = await fetch('http://localhost:8000/api/resume/build/', {
  //       method: 'POST',
  //       headers: { 'Content-Type': 'application/json' },
  //       body: JSON.stringify({
  //         contact: resumeData.contact,
  //         experience: resumeData.experience,
  //         education: resumeData.education,
  //         skills: resumeData.skills,
  //         summary: resumeData.summary,
  //         enhanceWithAI: false
  //       })
  //     });
      
  //     const result = await response.json();
      
  //     if (result.success) {
  //       // 保存到 localStorage 或 state
  //       localStorage.setItem('resumeData', JSON.stringify(result.resume));
        
  //       // 跳转到预览页面
  //       router.push(`/dashboard/resume/build/preview/${template}`);
  //     }
  //   } catch (error) {
  //     console.error('Build failed:', error);
  //   }
  // };
  const handleFinish = async () => {
    if(!validateForm()){
      const errorMessages = Object.values(errors).join('\n');
      alert(`Please complete the following:\n\n${errorMessages}`);
      return;
    }
    setIsSubmitting(true);
    try {
      // 👇 在这里添加 log - 构建要发送的数据对象
      const requestData = {
        contact: resumeData.contact,
        experience: resumeData.experience,
        education: resumeData.education,
        skills: resumeData.skills,
        summary: resumeData.summary,
        enhanceWithAI: false
      };
      
      // 👇 打印查看数据结构
      console.log('=== 发送到后端的数据 ===');
      console.log(JSON.stringify(requestData, null, 2));
      console.log('======================');
      
      // 调用 build API
      const response = await fetch('http://localhost:8000/api/resume/build/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)  // 
      });
      
      // 👇 也可以看看响应
      console.log('响应状态:', response.status);
      const result = await response.json();
      console.log('响应数据:', result);
      
      if (result.success) {
        localStorage.setItem('resumeData', JSON.stringify(result.resume));
        router.push(`/dashboard/resume/build/preview/${template}`);
      }
    } catch (error) {
      console.error('Build failed:', error);
    } finally {
      setIsSubmitting(false);  // 👈 别忘了重置提交状态
    }
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