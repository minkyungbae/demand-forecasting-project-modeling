import React, { useState, useCallback } from 'react';
import { DashboardLayout } from './components/DashboardLayout';
import { DataDashboard } from './components/DataDashboard';
import { FileUpload } from './components/FileUpload';
import { IntroView } from './components/IntroView';
import { SolutionView } from './components/SolutionView';
import { LoginView } from './components/LoginView';
import { SignupView } from './components/SignupView';
import type { ProductData, FilePayload, UserProfile } from './types';

type ViewMode =
  | 'intro'
  | 'upload'
  | 'result'
  | 'predict'
  | 'solution'
  | 'login'
  | 'signup';

const App: React.FC = () => {
  // 분석 결과 데이터 (※ 추후 API 연동 예정)
  const [data, setData] = useState<ProductData[]>([]);

  // 업로드된 파일 정보
  const [fileInfo, setFileInfo] = useState<FilePayload | null>(null);

  const [selectedColumn, setSelectedColumn] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('intro');
  const [isPredicting, setIsPredicting] = useState(false);

  // 사용자 인증
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  /* =======================
      File Upload Callback
  ======================= */
  const handleDataLoaded = useCallback((payload: FilePayload) => {
    setFileInfo(payload);

    // 지금은 분석 API가 없으므로 data는 그대로 둠
    // 이후: file_id로 분석 API 호출 → setData()

    setViewMode('result');
  }, []);

  const resetAnalysis = () => {
    setData([]);
    setFileInfo(null);
    setSelectedColumn(null);
    setViewMode('intro');
  };

  const goToDashboard = () => setViewMode('intro');

  const handleStepOneClick = () => {
    fileInfo ? setViewMode('result') : setViewMode('upload');
  };

  const handleStepTwoClick = () => {
    if (!fileInfo) {
      alert('먼저 데이터를 업로드해주세요.');
      setViewMode('upload');
      return;
    }
    setViewMode('predict');
  };

  const handleStepThreeClick = () => {
    if (!isLoggedIn) {
      alert('3단계 결과는 회원만 확인 가능합니다.');
      setViewMode('login');
      return;
    }

    if (!fileInfo || !selectedColumn) {
      alert('예측 타겟을 선택해주세요.');
      setViewMode('result');
      return;
    }

    setViewMode('solution');
  };

  /* =======================
      Auth
  ======================= */
  const handleLoginSuccess = (userData: any) => {
    setIsLoggedIn(true);

    const profile: UserProfile = {
      user_id: userData.user_id || 'unknown',
      email: userData.email || '',
      name: userData.name || 'User',
      user_type: userData.user_type || 'Basic',
      created_at: userData.created_at || new Date().toISOString(),
    };

    setUserProfile(profile);
    alert(`${profile.name}님, 환영합니다!`);
    setViewMode('intro');
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserProfile(null);
    setViewMode('intro');
  };

  const handleSignupSuccess = () => {
    alert('회원가입이 완료되었습니다. 로그인해주세요.');
    setViewMode('login');
  };

  /* =======================
      Prediction (Mock)
  ======================= */
  const startPrediction = () => {
    if (!selectedColumn) return;

    setIsPredicting(true);
    setTimeout(() => {
      setIsPredicting(false);
      setViewMode('predict');
    }, 2000);
  };

  return (
    <DashboardLayout
      currentStep={
        viewMode === 'result' || viewMode === 'upload'
          ? 1
          : viewMode === 'predict'
          ? 2
          : viewMode === 'solution'
          ? 3
          : 0
      }
      userProfile={userProfile}
      onDashboardClick={goToDashboard}
      onStepOneClick={handleStepOneClick}
      onStepTwoClick={handleStepTwoClick}
      onStepThreeClick={handleStepThreeClick}
      onLoginClick={() => setViewMode('login')}
      onSignupClick={() => setViewMode('signup')}
      onLogout={handleLogout}
    >
      {/* =======================
          Views
      ======================= */}

      {viewMode === 'intro' && <IntroView onStart={() => setViewMode('upload')} />}

      {viewMode === 'upload' && (
        <div className="space-y-6">
          {/* 1. Breadcrumb (경로 표시) */}
          <nav className="flex items-center gap-2 text-[13px] font-medium">
            <span className="text-primary-main cursor-pointer" onClick={() => setViewMode('intro')}>Home</span>
            <span className="text-gray-300">/</span>
            <span className="text-gray-800 font-bold">Upload</span>
          </nav>

          {/* 2. Page Header (제목 및 뒤로 가기) */}
          <div className="bg-white rounded-xl border border-[#d8dbe0] p-6 flex items-center justify-between shadow-sm">
            <div>
              <h1 className="text-xl font-black text-gray-800 mb-1">데이터 업로드</h1>
              <p className="text-sm text-gray-400 font-medium">분석을 위해 CSV 파일을 업로드해주세요.</p>
            </div>
            <button 
              onClick={() => setViewMode('intro')}
              className="px-5 py-2 border border-[#d8dbe0] rounded-lg text-sm font-bold text-gray-600 hover:bg-gray-50 transition-all active:scale-95"
            >
              뒤로 가기
            </button>
          </div>

          {/* 3. STEP 1 카드 레이아웃 */}
          <div className="bg-white rounded-xl border border-[#d8dbe0] overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-[#f0f2f5] bg-[#f8f9fa]">
              <h2 className="text-sm font-black text-gray-800 uppercase tracking-tight">STEP 1 : 파일 업로드</h2>
            </div>
            <div className="p-16 flex justify-center items-center bg-white">
              <FileUpload onDataLoaded={handleDataLoaded} />
            </div>
          </div>
        </div>
      )}

      {viewMode === 'result' && fileInfo && (
        <>
          <DataDashboard data={data} />

          <div className="mt-8">
            <p className="text-sm mb-3 font-bold">
              예측 타겟 컬럼 선택
            </p>
            <div className="flex flex-wrap gap-2">
              {fileInfo.columns.map((col) => (
                <button
                  key={col}
                  onClick={() => setSelectedColumn(col)}
                  className={`px-3 py-1 rounded text-xs font-bold border ${
                    selectedColumn === col
                      ? 'bg-primary-main text-white'
                      : 'bg-white text-gray-500'
                  }`}
                >
                  {col}
                </button>
              ))}
            </div>

            <button
              onClick={startPrediction}
              disabled={!selectedColumn || isPredicting}
              className="mt-6 px-6 py-3 bg-primary-main text-white rounded font-bold"
            >
              AI 모델 예측 시작
            </button>
          </div>
        </>
      )}

      {(viewMode === 'predict' || viewMode === 'solution') && (
        <SolutionView data={data} selectedColumn={selectedColumn} />
      )}

      {viewMode === 'login' && (
        <LoginView
          onLoginSuccess={handleLoginSuccess}
          onCancel={() => setViewMode('intro')}
          onSignupClick={() => setViewMode('signup')}
        />
      )}

      {viewMode === 'signup' && (
        <SignupView
          onSignupSuccess={handleSignupSuccess}
          onCancel={() => setViewMode('intro')}
          onLoginClick={() => setViewMode('login')}
        />
      )}
    </DashboardLayout>
  );
};

export default App;
