
import React, { useState, useCallback } from 'react';
import { DashboardLayout } from './components/DashboardLayout';
import { DataDashboard } from './components/DataDashboard';
import { FileUpload } from './components/FileUpload';
import { IntroView } from './components/IntroView';
import type{ ProductData, FilePayload } from './types';

type ViewMode = 'intro' | 'upload' | 'result' | 'predict';

const App: React.FC = () => {
  const [data, setData] = useState<ProductData[]>([]);
  const [headers, setHeaders] = useState<string[]>([]);
  const [selectedColumn, setSelectedColumn] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('intro');
  const [isPredicting, setIsPredicting] = useState(false);

  const handleDataLoaded = useCallback((payload: FilePayload) => {
    setData(payload.data);
    // 한 번 더 헤더 클리닝 (보이지 않는 제어 문자 및 BOM 제거)
    const cleanedHeaders = payload.headers.map(h => 
      h.replace(/[\u0000-\u001F\u007F-\u009F\uFEFF\u200B-\u200D]/g, '').trim()
    );
    setHeaders(cleanedHeaders);
    setViewMode('result');
  }, []);

  const resetAnalysis = () => {
    setData([]);
    setHeaders([]);
    setSelectedColumn(null);
    setViewMode('intro');
  };

  const goToDashboard = () => setViewMode('intro');

  const handleStepOneClick = () => {
    if (data.length > 0) setViewMode('result');
    else setViewMode('upload');
  };

  const handleStepTwoClick = () => {
    if (data.length > 0) setViewMode('predict');
    else alert('먼저 데이터를 업로드해주세요.');
  };

  const startPrediction = () => {
    if (!selectedColumn) return;
    setIsPredicting(true);
    // AI 모델 예측 시뮬레이션
    setTimeout(() => {
      setIsPredicting(false);
      setViewMode('predict');
    }, 2000);
  };

  return (
    <DashboardLayout 
      currentStep={viewMode === 'result' || viewMode === 'upload' ? 1 : (viewMode === 'predict' ? 2 : 0)} 
      onDashboardClick={goToDashboard}
      onStepOneClick={handleStepOneClick}
      onStepTwoClick={handleStepTwoClick}
    >
      <div className="space-y-6">
        {/* Breadcrumb Info */}
        <div className="flex items-center gap-2 text-[13px] text-gray-500">
          <span className="text-primary-main hover:underline cursor-pointer" onClick={() => setViewMode('intro')}>Home</span>
          <span className="text-gray-300">/</span>
          <span className="font-semibold text-gray-800 capitalize">{viewMode}</span>
        </div>

        {viewMode === 'intro' && (
          <IntroView onStart={() => setViewMode('upload')} />
        )}

        {viewMode === 'upload' && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
             <div className="bg-white p-6 rounded-lg border border-[#d8dbe0] shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                <div>
                  <h1 className="text-2xl font-bold text-gray-800">데이터 업로드</h1>
                  <p className="text-sm text-gray-500 mt-1">분석을 위해 CSV 파일을 업로드해주세요.</p>
                </div>
                <button onClick={() => setViewMode('intro')} className="bg-gray-50 text-gray-600 px-4 py-2 rounded text-sm font-bold border border-gray-100 hover:bg-gray-100 transition-colors">뒤로 가기</button>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-[#d8dbe0] overflow-hidden">
                <div className="bg-[#f8f9fa] border-b border-[#d8dbe0] px-6 py-4">
                  <h2 className="text-sm font-bold text-gray-700 uppercase tracking-tight">Step 1 : 파일 업로드</h2>
                </div>
                <div className="p-12 flex flex-col items-center">
                  <FileUpload onDataLoaded={handleDataLoaded} />
                </div>
              </div>
          </div>
        )}

        {viewMode === 'result' && data.length > 0 && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
            <div className="bg-white p-6 rounded-lg border border-[#d8dbe0] shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-800">1단계 : 파일 분석 결과</h1>
                <p className="text-sm text-gray-500 mt-1">업로드된 상품 데이터를 기반으로 분석된 지표와 시각화입니다.</p>
              </div>
              <div className="flex gap-3">
                <button onClick={() => setViewMode('upload')} className="bg-primary-light text-primary-main px-4 py-2 rounded text-sm font-bold border border-primary-light hover:bg-white hover:border-primary-main transition-colors">다른 파일 분석</button>
                <button onClick={resetAnalysis} className="bg-red-50 text-red-600 px-4 py-2 rounded text-sm font-bold border border-red-100 hover:bg-red-100 transition-colors">초기화</button>
              </div>
            </div>

            <DataDashboard data={data} />
            
            {/* 컬럼 선택 및 예측 섹션 */}
            <div className="bg-white rounded-xl shadow-sm border border-[#d8dbe0] overflow-hidden">
              <div className="bg-[#f8f9fa] border-b border-[#d8dbe0] px-6 py-4">
                <h2 className="text-sm font-bold text-gray-700 uppercase tracking-tight">2단계 : 모델 예측 설정</h2>
              </div>
              <div className="p-8">
                <p className="text-sm font-medium text-gray-600 mb-4">예측하고 싶은 컬럼(타겟)을 하나 선택해주세요:</p>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-8">
                  {headers.map((header) => (
                    <button
                      key={header}
                      onClick={() => setSelectedColumn(header)}
                      className={`px-4 py-2.5 rounded-lg text-xs font-bold transition-all border break-all ${
                        selectedColumn === header 
                        ? 'bg-primary-main text-white border-primary-main shadow-md ring-2 ring-primary-light' 
                        : 'bg-white text-gray-500 border-gray-200 hover:border-primary-main hover:text-primary-main'
                      }`}
                    >
                      {header}
                    </button>
                  ))}
                </div>
                
                <div className="flex justify-center">
                  <button
                    onClick={startPrediction}
                    disabled={!selectedColumn || isPredicting}
                    className={`px-10 py-4 rounded-full font-black text-lg shadow-lg transition-all flex items-center gap-3 ${
                      selectedColumn && !isPredicting
                      ? 'bg-[#1677ff] text-white hover:scale-105 active:scale-95'
                      : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    {isPredicting ? (
                      <>
                        <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        모델 예측 분석 중...
                      </>
                    ) : (
                      <>
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
                        AI 모델 예측 시작
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {viewMode === 'predict' && (
          <div className="space-y-6 animate-in zoom-in-95 duration-500">
            <div className="bg-white p-8 rounded-xl border border-primary-light shadow-xl text-center">
              <div className="w-20 h-20 bg-primary-light rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-10 h-10 text-primary-main" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
              </div>
              <h1 className="text-2xl font-black text-gray-800">예측 분석이 완료되었습니다!</h1>
              <p className="text-gray-500 mt-2">선택한 컬럼: <span className="text-primary-main font-bold">[{selectedColumn}]</span></p>
              
              <div className="mt-10 grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
                <div className="p-6 bg-[#f8f9fa] rounded-lg border border-gray-100">
                  <h3 className="font-bold text-gray-700 mb-3">💡 예측 인사이트</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    '{selectedColumn}' 데이터를 기반으로 모델이 학습을 마쳤습니다. 향후 3개월간 해당 지표는 
                    판매 패턴과 계절적 요인에 의해 약 <span className="text-green-600 font-bold">12.5% 상승</span>할 것으로 예측됩니다.
                  </p>
                </div>
                <div className="p-6 bg-[#f8f9fa] rounded-lg border border-gray-100">
                  <h3 className="font-bold text-gray-700 mb-3">📈 모델 성능</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs"><span>정확도 (Accuracy)</span><span className="font-bold">94.2%</span></div>
                    <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden"><div className="bg-primary-main h-full w-[94%]"></div></div>
                    <div className="flex justify-between text-xs mt-4"><span>신뢰도 (Confidence)</span><span className="font-bold">88.7%</span></div>
                    <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden"><div className="bg-green-500 h-full w-[88%]"></div></div>
                  </div>
                </div>
              </div>

              <button 
                onClick={() => setViewMode('result')}
                className="mt-8 text-primary-main font-bold hover:underline"
              >
                ← 다시 설정하기
              </button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default App;
