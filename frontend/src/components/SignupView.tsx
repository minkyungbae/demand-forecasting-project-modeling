
import React, { useState } from 'react';
import { register } from '../services/api';

interface SignupViewProps {
    onSignupSuccess: () => void;
    onCancel: () => void;
    onLoginClick: () => void;
}

export const SignupView: React.FC<SignupViewProps> = ({ onSignupSuccess, onCancel, onLoginClick }) => {
    // form state
    const [formData, setFormData] = useState({
    username: '', // 이름
    email: '',
    password: '',
    confirmPassword: ''
    });

    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);


    // 회원가입 에러 처리
    const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (
        !formData.username ||
        !formData.email ||
        !formData.password ||
        !formData.confirmPassword
    ) {
        setError('모든 필드를 입력해주세요.');
        return;
    }

    if (!formData.email.includes('@')) {
        setError('유효한 이메일 주소를 입력해주세요.');
        return;
    }

    if (formData.password !== formData.confirmPassword) {
        setError('비밀번호가 일치하지 않습니다.');
        return;
    }

    // API call
    setIsLoading(true);

    try {
        const result  = await register({
        username: formData.email, // api에선 username == email
        password: formData.password,
        name: formData.username, // 사용자 이름
        user_type: 'basic',
    });

        // JWT 저장
        localStorage.setItem('access_token', result.access_token);

        // 성공 콜백
        onSignupSuccess();
        } catch (err: any) {
        console.error('Signup error:', err);
        setError(err.message || '회원가입에 실패했습니다.');
    } finally {
        setIsLoading(false);
        }
    };

    // ==================
    // UI
    // ==================
    return (
    <div className="flex items-center justify-center min-h-[70vh] animate-in fade-in zoom-in-95 duration-500">
        <div className="bg-white p-10 rounded-2xl shadow-xl border border-gray-100 w-full max-w-md">
        <div className="text-center mb-8">
            <div className="w-16 h-16 bg-primary-light rounded-2xl flex items-center justify-center mx-auto mb-4 -rotate-3">
            <svg className="w-8 h-8 text-primary-main" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            </div>
            <h2 className="text-2xl font-black text-gray-800 tracking-tight">회원가입</h2>
            <p className="text-sm text-gray-400 mt-2 font-medium">ForeCastly의 스마트한 분석 서비스를 시작하세요.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
            <div className="bg-red-50 text-red-500 text-xs p-3 rounded-lg border border-red-100 font-bold animate-pulse">
                {error}
            </div>
            )}
        
            <div className="space-y-1.5">
            <label className="text-[11px] font-black text-gray-500 uppercase ml-1">Name</label>
            <input 
                type="text" 
                placeholder="이름"
                disabled={isLoading}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary-main focus:ring-4 focus:ring-primary-light outline-none transition-all text-sm disabled:bg-gray-50"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
            />
            </div>

            <div className="space-y-1.5">
            <label className="text-[11px] font-black text-gray-500 uppercase ml-1">Email Address</label>
            <input 
                type="email" 
                placeholder="example@email.com"
                disabled={isLoading}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary-main focus:ring-4 focus:ring-primary-light outline-none transition-all text-sm disabled:bg-gray-50"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
            />
            </div>

            <div className="space-y-1.5">
            <label className="text-[11px] font-black text-gray-500 uppercase ml-1">Password</label>
            <input 
                type="password" 
                placeholder="비밀번호"
                disabled={isLoading}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary-main focus:ring-4 focus:ring-primary-light outline-none transition-all text-sm disabled:bg-gray-50"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
            />
            </div>

            <div className="space-y-1.5">
            <label className="text-[11px] font-black text-gray-500 uppercase ml-1">Confirm Password</label>
            <input 
                type="password" 
                placeholder="비밀번호 확인"
                disabled={isLoading}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary-main focus:ring-4 focus:ring-primary-light outline-none transition-all text-sm disabled:bg-gray-50"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
            />
            </div>

            <div className="pt-2 flex flex-col gap-3">
            <button 
                type="submit"
                disabled={isLoading}
                className="w-full bg-primary-main text-white py-3.5 rounded-xl font-black text-sm shadow-lg shadow-primary-light hover:bg-primary-dark transition-all active:scale-95 disabled:bg-gray-300 disabled:shadow-none flex items-center justify-center gap-2"
            >
                {isLoading ? (
                <>
                    <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    가입 요청 중...
                </>
                ) : '가입하기'}
            </button>
            </div>
        </form>

        <div className="mt-6">
            <div className="relative flex items-center justify-center mb-6">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-100"></div></div>
            <span className="relative bg-white px-4 text-[10px] font-black text-gray-400 uppercase">또는 소셜 계정으로 가입</span>
            </div>

            <div className="flex justify-center gap-4">
            <button className="w-12 h-12 rounded-full border border-gray-100 flex items-center justify-center hover:bg-gray-50 transition-colors shadow-sm">
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
            </button>
            <button className="w-12 h-12 rounded-full bg-[#03C75A] flex items-center justify-center hover:opacity-90 transition-opacity shadow-sm">
                <span className="text-white font-black text-lg">N</span>
            </button>
            <button className="w-12 h-12 rounded-full bg-[#FEE500] flex items-center justify-center hover:opacity-90 transition-opacity shadow-sm">
                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="#3C1E1E">
                <path d="M12 3c-4.97 0-9 3.185-9 7.115 0 2.553 1.706 4.8 4.27 6.054l-1.085 3.98c-.05.186.058.384.244.437.058.016.118.02.176.01.127-.015.244-.085.31-.194l4.634-3.13c.148.02.3.03.451.03 4.97 0 9-3.186 9-7.116C21 6.185 16.97 3 12 3z"/>
                </svg>
            </button>
            </div>
        </div>

        <div className="mt-8 text-center border-t border-gray-50 pt-6">
            <p className="text-[11px] text-gray-400 font-medium">
            이미 계정이 있으신가요? <span onClick={onLoginClick} className="text-primary-main font-bold cursor-pointer hover:underline ml-1">로그인</span>
            </p>
            <button onClick={onCancel} className="mt-4 text-[10px] text-gray-400 hover:text-gray-600 transition-colors">취소하고 돌아가기</button>
        </div>
        </div>
    </div>
    );
};
