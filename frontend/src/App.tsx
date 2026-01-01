
import React, { useState, useCallback } from 'react';
import { DataDashboard } from './components/DataDashboard';
import { FileUpload } from './components/FileUpload';
import { ProductData } from './types';

const App: React.FC = () => {
  const [data, setData] = useState<ProductData[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleDataLoaded = useCallback((newData: ProductData[]) => {
    setData(newData);
  }, []);

  const resetData = () => {
    setData([]);
  };

  return (
    <div className="min-h-screen bg-background text-gray-900">
      {/* Header */}
      <header className="bg-white border-b border-divider h-16 flex items-center px-8 sticky top-0 z-10 shadow-sm">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-main rounded-md flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-gray-800">Mantis Analytics</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-4 md:p-8">
        {!data.length ? (
          <div className="flex flex-col items-center justify-center min-h-[70vh]">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-2">데이터 분석 시작하기</h2>
              <p className="text-secondary">CSV 파일을 업로드하여 상품 현황 및 매출 추세를 한눈에 확인하세요.</p>
            </div>
            <FileUpload onDataLoaded={handleDataLoaded} />
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-gray-800">기본적인 데이터 분석 내용 출력</h2>
              <button 
                onClick={resetData}
                className="text-sm text-primary-main hover:underline font-medium"
              >
                다른 파일 업로드하기
              </button>
            </div>
            
            <DataDashboard data={data} />
            
            <div className="flex justify-end pt-4">
              <button 
                className="bg-primary-main hover:bg-primary-dark text-white font-semibold py-2.5 px-6 rounded shadow-mantis transition-all flex items-center gap-2"
                onClick={() => alert('심층 분석 페이지로 이동합니다 (준비 중)')}
              >
                심층 분석 하러 가기
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
