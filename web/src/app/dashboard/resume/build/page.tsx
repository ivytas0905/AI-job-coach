
import { useRouter } from 'next/router';

export default function BuildResumePage() {
  const router = useRouter();

  const templates = [
    {
      id: 'simple',
      name: 'Simple',
      preview: '/templates/simple-preview.png',
    },
    {
      id: 'professional',
      name: 'Professional',
      preview: '/templates/professional-preview.png',
    },
    {
      id: 'modern',
      name: 'Modern',
      preview: '/templates/modern-preview.png',
    },
  ];

  const handleSelectTemplate = (templateId: string) => {
    // 选择模板后，跳转到表单页面
    router.push(`/build-resume/form/${templateId}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4">
        {/* 标题 */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Choose a Template</h1>
          <p className="text-gray-600">
            Select a template to get started
          </p>
        </div>

        {/* 模板卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {templates.map((template) => (
            <button
              key={template.id}
              onClick={() => handleSelectTemplate(template.id)}
              className="group bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
            >
              {/* 预览图 */}
              <div className="aspect-[8.5/11] bg-gray-100 relative overflow-hidden">
                <img
                  src={template.preview}
                  alt={template.name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-blue-600 bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-300" />
              </div>

              {/* 模板名称 */}
              <div className="p-6 text-center">
                <h3 className="text-xl font-bold mb-3 group-hover:text-blue-600 transition-colors">
                  {template.name}
                </h3>
                <span className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg group-hover:bg-blue-700 transition-colors">
                  Choose Template
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}