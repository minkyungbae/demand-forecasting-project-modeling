
import React from 'react';

interface SidebarProps {
  currentStep: number;
  onDashboardClick?: () => void;
  onStepOneClick?: () => void;
  onStepTwoClick?: () => void;
  onStepThreeClick?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  currentStep, 
  onDashboardClick, 
  onStepOneClick, 
  onStepTwoClick,
  onStepThreeClick
}) => {
  const mainMenus = [
    { title: 'ForeCastly', active: true, onClick: onDashboardClick },
    { title: '로그인' },
    { title: '회원가입' },
  ];

  const functions = [
    { step: 1, label: '파일 업로드 및 분석', onClick: onStepOneClick },
    { step: 2, label: '모델 예측', onClick: onStepTwoClick },
    { step: 3, label: '솔루션 결과', onClick: onStepThreeClick },
  ];

  return (
    <aside className="w-64 bg-[#2c384a] text-white flex-shrink-0 flex flex-col h-full border-r border-gray-800 z-50 shadow-xl overflow-hidden">
      {/* Logo Section */}
      <div className="h-14 flex items-center px-6 gap-3 border-b border-gray-700 bg-[#242e3d] flex-shrink-0 cursor-pointer" onClick={onDashboardClick}>
        <div className="w-7 h-7 bg-[#1677ff] rounded flex items-center justify-center font-bold text-sm shadow-inner text-white">M</div>
        <span className="font-bold text-lg tracking-tight uppercase text-white">ForeCastly</span>
      </div>

      <div className="flex-1 py-6 overflow-y-auto">
        <div className="px-3 space-y-1">
          {mainMenus.map((menu, i) => (
            <button 
              key={i} 
              onClick={menu.onClick}
              className={`w-full flex items-center justify-between px-4 py-2.5 rounded transition-all hover:bg-gray-700 group ${menu.active && currentStep === 0 ? 'bg-[#1677ff] text-white shadow-md' : 'text-gray-300'}`}
            >
              <div className="flex items-center gap-3">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
                <span className="text-[13px] font-medium">{menu.title}</span>
              </div>
            </button>
          ))}
        </div>

        <div className="mt-10">
          <p className="px-7 text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-3">Function</p>
          <div className="px-3 space-y-1">
            {functions.map((fn) => (
              <button 
                key={fn.step} 
                onClick={fn.onClick}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded border-l-4 transition-all text-left ${currentStep === fn.step ? 'bg-gray-800/50 border-[#1677ff] text-white shadow-sm' : 'border-transparent text-white hover:bg-gray-700/30'}`}
              >
                <span className={`w-5 h-5 flex-shrink-0 rounded-full flex items-center justify-center text-[10px] font-bold bg-[#1677ff] text-white shadow-[0_0_10px_rgba(22,119,255,0.3)] ${currentStep === fn.step ? 'ring-2 ring-primary-light ring-offset-1 ring-offset-[#2c384a]' : ''}`}>
                  {fn.step}
                </span>
                <span className="text-[12px] whitespace-nowrap font-medium">{fn.step}단계 : {fn.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-gray-700 text-center flex-shrink-0">
        <button className="text-gray-500 hover:text-white transition-colors">
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" className="mx-auto">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>
    </aside>
  );
};
