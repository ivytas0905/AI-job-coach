'use client';

import { useRouter } from 'next/navigation';

export default function ResumePage() {
  const router = useRouter();

  const goBack = () => {
    router.back();
  };

  const chooseBuild = () => {
    router.push('/dashboard/resume/build');
  };

  const chooseUpload = () => {
    router.push('/dashboard/resume/upload');
  };

  return (
    <div className="min-h-screen flex flex-col items-center p-8 bg-gradient-to-br from-indigo-500 to-purple-600">
      <style jsx global>{`
        .choice-card {
          transition: all 0.3s ease;
        }
        
        .choice-card:hover {
          transform: translateY(-10px);
          box-shadow: 0 30px 60px rgba(0,0,0,0.15);
        }
        
        .choice-card:active {
          transform: translateY(-8px) scale(0.98);
        }
        
        .btn:hover {
          transform: translateY(-2px);
        }
        
        .back-btn:hover {
          transform: translateY(-2px);
        }
      `}</style>
      
      <button 
        onClick={goBack}
        className="absolute top-8 left-8 bg-white bg-opacity-20 text-white border-none py-3 px-6 rounded-full cursor-pointer transition-all duration-300 backdrop-blur-sm hover:bg-opacity-30"
      >
        ← Back
      </button>
      
      <div className="text-center mb-12 text-white">
        <h1 className="text-4xl font-bold mb-2 text-shadow">
          Make Resume in Easy Way
        </h1>
        <p className="text-lg opacity-90 max-w-2xl leading-relaxed">
          Choose the best approach for you to create or optimize your resume and gain a competitive edge in your job search
        </p>
      </div>
      
      <div className="flex gap-8 max-w-4xl w-full flex-col md:flex-row">
        {/* Build Your Resume Card */}
        <div 
          onClick={chooseBuild}
          className="choice-card flex-1 bg-white rounded-3xl p-10 text-center shadow-xl cursor-pointer relative overflow-hidden group"
        >
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-400 to-cyan-400"></div>
          
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-400 to-cyan-400 flex items-center justify-center text-4xl text-white">
            
          </div>
          
          <h2 className="text-3xl font-bold mb-4 text-gray-800">
            Build Your Resume
          </h2>
          
          <p className="text-gray-600 leading-relaxed mb-8 text-base">
            Create a professional resume from scratch with our step-by-step guidance
          </p>
          
          <ul className="list-none mb-8 space-y-2">
            <li className="text-gray-700 flex items-center justify-center text-sm">
              <span className="text-green-500 font-bold mr-2">✓</span>
              AI-powered writing assistance
            </li>
            <li className="text-gray-700 flex items-center justify-center text-sm">
              <span className="text-green-500 font-bold mr-2">✓</span>
              Multiple professional templates
            </li>
            <li className="text-gray-700 flex items-center justify-center text-sm">
              <span className="text-green-500 font-bold mr-2">✓</span>
              Real-time preview
            </li>
            <li className="text-gray-700 flex items-center justify-center text-sm">
              <span className="text-green-500 font-bold mr-2">✓</span>
              Personalized customization
            </li>
          </ul>
          
          <button className="btn w-full bg-gradient-to-r from-blue-400 to-cyan-400 text-white border-none py-4 px-8 rounded-full text-base font-semibold cursor-pointer transition-all duration-300 uppercase tracking-wide hover:shadow-lg">
            Start Building
          </button>
        </div>

        {/* Upload Your Resume Card */}
        <div 
          onClick={chooseUpload}
          className="choice-card flex-1 bg-white rounded-3xl p-10 text-center shadow-xl cursor-pointer relative overflow-hidden group"
        >
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-green-400 to-teal-400"></div>
          
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-green-400 to-teal-400 flex items-center justify-center text-4xl text-white">
            📄
          </div>
          
          <h2 className="text-3xl font-bold mb-4 text-gray-800">
            Upload Your Resume
          </h2>
          
          <p className="text-gray-600 leading-relaxed mb-8 text-base">
            Upload your existing resume and get AI-driven professional optimization suggestions
          </p>
          
          <ul className="list-none mb-8 space-y-2">
            <li className="text-gray-700 flex items-center justify-center text-sm">
              <span className="text-green-500 font-bold mr-2">✓</span>
              Intelligent content analysis
            </li>
            <li className="text-gray-700 flex items-center justify-center text-sm">
              <span className="text-green-500 font-bold mr-2">✓</span>
              Keyword optimization tips
            </li>
            <li className="text-gray-700 flex items-center justify-center text-sm">
              <span className="text-green-500 font-bold mr-2">✓</span>
              Format enhancement
            </li>
            <li className="text-gray-700 flex items-center justify-center text-sm">
              <span className="text-green-500 font-bold mr-2">✓</span>
              ATS compatibility check
            </li>
          </ul>
          
          <button className="btn w-full bg-gradient-to-r from-green-400 to-teal-400 text-white border-none py-4 px-8 rounded-full text-base font-semibold cursor-pointer transition-all duration-300 uppercase tracking-wide hover:shadow-lg">
            Upload Resume
          </button>
        </div>
      </div>
    </div>
  );
}