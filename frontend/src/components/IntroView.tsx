
import React from 'react';

interface IntroViewProps {
  onStart: () => void;
}

export const IntroView: React.FC<IntroViewProps> = ({ onStart }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] w-full relative">
      {/* Title Section */}
      <div className="text-center mb-16 animate-in fade-in slide-in-from-top-4 duration-700">
        <h1 className="text-3xl font-extrabold text-gray-800 mb-2">지능형 수요 예측 서비스</h1>
        <p className="text-lg text-gray-500 font-medium">데이터 분석을 통한 비즈니스 최적화 솔루션</p>
        <p className="text-sm text-gray-400 mt-6 max-w-lg mx-auto leading-relaxed">
        재고를 좀 더 효율적으로 예측하고 발주할 수 있도록 저희 AI가 도와드리겠습니다.<br />
        AI 서비스를 통해 편하고 가독성 있게 결과를 확인하실 수 있습니다.
        </p>
      </div>

      {/* Diagram Container */}
      <div className="relative w-full max-w-4xl h-[500px] flex items-center justify-center">
        
        {/* Center Start Button */}
        <button 
          onClick={onStart}
          className="z-20 w-44 h-44 rounded-full bg-[#cbdcf7] border-2 border-[#a3b9e0] shadow-[0_10px_30px_rgba(0,0,0,0.1)] hover:shadow-[0_15px_40px_rgba(0,0,0,0.15)] hover:scale-105 transition-all duration-300 flex flex-col items-center justify-center text-gray-700 group"
        >
          <span className="text-xl font-bold tracking-tighter">분석</span>
          <span className="text-2xl font-black mb-1">Start</span>
          <span className="text-sm font-semibold opacity-80 uppercase">Button</span>
          <div className="mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
             <svg className="w-6 h-6 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 14l-7 7m0 0l-7-7m7 7V3" /></svg>
          </div>
        </button>

        {/* Process Cards */}
        {/* 1st Process: Top Left */}
        <div className="absolute top-0 left-4 md:left-20 w-64 p-6 bg-[#abc9f4] rounded-2xl shadow-sm border-2 border-gray-300 animate-in fade-in slide-in-from-left-8 duration-1000 delay-100">
          <h4 className="text-lg font-bold text-gray-800 mb-2 text-center">1번째 과정</h4>
          <p className="text-sm text-gray-700 text-center font-medium leading-relaxed italic">입력받은 데이터를 분석합니다.</p>
        </div>

        {/* 2nd Process: Top Right */}
        <div className="absolute top-0 right-4 md:right-20 w-64 p-6 bg-[#f5f5f5] rounded-2xl shadow-md border-2 border-gray-300 animate-in fade-in slide-in-from-right-8 duration-1000 delay-300">
          <h4 className="text-lg font-bold text-gray-800 mb-2 text-center">2번째 과정</h4>
          <p className="text-sm text-gray-600 text-center font-medium leading-relaxed italic">입력받은 데이터 분석 결과를 시각화합니다.</p>
        </div>

        {/* 4th Process: Bottom Left */}
        <div className="absolute bottom-0 left-4 md:left-20 w-64 p-6 bg-[#f5f5f5] rounded-2xl shadow-md border-2 border-gray-300 animate-in fade-in slide-in-from-left-8 duration-1000 delay-500">
          <h4 className="text-lg font-bold text-gray-800 mb-2 text-center">4번째 과정</h4>
          <p className="text-sm text-gray-600 text-center font-medium leading-relaxed italic">학습한 모델이 내린 솔루션 결과를 알려줍니다.</p>
        </div>

        {/* 3rd Process: Bottom Right */}
        <div className="absolute bottom-0 right-4 md:right-20 w-64 p-6 bg-[#abc9f4] rounded-2xl shadow-sm border-2 border-gray-300 animate-in fade-in slide-in-from-right-8 duration-1000 delay-700">
          <h4 className="text-lg font-bold text-gray-800 mb-2 text-center">3번째 과정</h4>
          <p className="text-sm text-gray-700 text-center font-medium leading-relaxed italic">모델 학습 및 수용 예측을 진행하고,<br/>상관관계를 시각화하여 보여줍니다.</p>
        </div>

        {/* Decorative Connection Lines (SVG) */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-20" viewBox="0 0 800 500">
           <path d="M280 150 L350 200" stroke="#1677ff" strokeWidth="2" strokeDasharray="5,5" fill="none" />
           <path d="M520 150 L450 200" stroke="#1677ff" strokeWidth="2" strokeDasharray="5,5" fill="none" />
           <path d="M280 350 L350 300" stroke="#1677ff" strokeWidth="2" strokeDasharray="5,5" fill="none" />
           <path d="M520 350 L450 300" stroke="#1677ff" strokeWidth="2" strokeDasharray="5,5" fill="none" />
        </svg>
      </div>
    </div>
  );
};
