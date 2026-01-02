
import React, { useState } from 'react';

interface LoginViewProps {
  onLoginSuccess: (username: string) => void;
  onCancel: () => void;
  onSignupClick?: () => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLoginSuccess, onCancel, onSignupClick }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!formData.username || !formData.email || !formData.password) {
      setError('모든 필드를 입력해주세요.');
      return;
    }

    if (!formData.email.includes('@')) {
      setError('유효한 이메일 주소를 입력해주세요.');
      return;
    }

    // 로그인 시뮬레이션 성공
    onLoginSuccess(formData.username);
  };

  return (
    <div className="flex items-center justify-center min-h-[70vh] animate-in fade-in zoom-in-95 duration-500">
      <div className="bg-white p-10 rounded-2xl shadow-xl border border-gray-100 w-full max-w-md">
        <div className="text-center mb-10">
          <div className="w-16 h-16 bg-primary-light rounded-2xl flex items-center justify-center mx-auto mb-4 rotate-3">
            <svg className="w-8 h-8 text-primary-main" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 00-2 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 className="text-2xl font-black text-gray-800 tracking-tight">서비스 로그인</h2>
          <p className="text-sm text-gray-400 mt-2 font-medium">분석 솔루션을 확인하려면 로그인하세요.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {error && (
            <div className="bg-red-50 text-red-500 text-xs p-3 rounded-lg border border-red-100 font-bold animate-shake">
              {error}
            </div>
          )}
          
          <div className="space-y-1.5">
            <label className="text-[11px] font-black text-gray-500 uppercase ml-1">Username</label>
            <input 
              type="text" 
              placeholder="사용자 이름을 입력하세요"
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-main focus:ring-4 focus:ring-primary-light outline-none transition-all text-sm"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[11px] font-black text-gray-500 uppercase ml-1">Email Address</label>
            <input 
              type="email" 
              placeholder="abc@example.com"
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-main focus:ring-4 focus:ring-primary-light outline-none transition-all text-sm"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[11px] font-black text-gray-500 uppercase ml-1">Password</label>
            <input 
              type="password" 
              placeholder="••••••••"
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-main focus:ring-4 focus:ring-primary-light outline-none transition-all text-sm"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
            />
          </div>

          <div className="pt-4 flex flex-col gap-3">
            <button 
              type="submit"
              className="w-full bg-primary-main text-white py-4 rounded-xl font-black text-sm shadow-lg shadow-primary-light hover:bg-primary-dark transition-all active:scale-95"
            >
              로그인하기
            </button>
            <button 
              type="button"
              onClick={onCancel}
              className="w-full bg-gray-50 text-gray-500 py-3 rounded-xl font-bold text-xs hover:bg-gray-100 transition-all"
            >
              취소
            </button>
          </div>
        </form>

        <div className="mt-8 text-center">
          <p className="text-[11px] text-gray-400 font-medium">
            계정이 없으신가요? <span onClick={onSignupClick} className="text-primary-main font-bold cursor-pointer hover:underline">회원가입</span>
          </p>
        </div>
      </div>
    </div>
  );
};
