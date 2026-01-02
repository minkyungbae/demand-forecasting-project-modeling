
import React, { useState, useRef, useEffect } from 'react';
import { Sidebar } from './Sidebar';
import type{ UserProfile } from '../types';

interface DashboardLayoutProps {
  children: React.ReactNode;
  currentStep: number;
  userProfile?: UserProfile | null;
  onDashboardClick?: () => void;
  onStepOneClick?: () => void;
  onStepTwoClick?: () => void;
  onStepThreeClick?: () => void;
  onLoginClick?: () => void;
  onSignupClick?: () => void;
  onLogout?: () => void;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ 
  children, 
  currentStep, 
  userProfile,
  onDashboardClick,   
  onStepOneClick,
  onStepTwoClick,
  onStepThreeClick,
  onLoginClick,
  onSignupClick,
  onLogout
}) => {
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const profileRef = useRef<HTMLDivElement>(null);

  // 외부 클릭 시 프로필 닫기
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setIsProfileOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="flex w-full h-full overflow-hidden bg-[#ebedef]">
      {/* Sidebar - 왼쪽 고정 */}
      <Sidebar 
        currentStep={currentStep} 
        onDashboardClick={onDashboardClick} 
        onStepOneClick={onStepOneClick}
        onStepTwoClick={onStepTwoClick}
        onStepThreeClick={onStepThreeClick}
        onLoginClick={onLoginClick}
        onSignupClick={onSignupClick}
      />

      {/* Main Container - 오른쪽 전체 */}
      <div className="flex-1 flex flex-col h-full min-w-0 overflow-hidden">
        {/* Top Navbar */}
        <header className="bg-white border-b border-[#d8dbe0] h-14 flex items-center justify-between px-6 shadow-sm flex-shrink-0 z-40">
          <div className="flex items-center gap-6">
            <button className="text-gray-500 hover:text-gray-800" onClick={onDashboardClick}>
              <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <nav className="hidden md:flex items-center gap-3 text-[13px] font-medium">
              <span className="text-gray-400 hover:text-primary-main cursor-pointer" onClick={onDashboardClick}>Dashboard</span>
              <span className="text-gray-300">/</span>
              <span className="text-gray-800">Product Analysis</span>
            </nav>
          </div>
          
          <div className="flex items-center gap-5">
            <div className="flex items-center gap-4 text-gray-400">
              <button className="hover:text-primary-main transition-colors"><svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg></button>
              <button className="hover:text-primary-main transition-colors"><svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg></button>
            </div>
            
            {/* Profile Section with Dropdown */}
            <div className="relative" ref={profileRef}>
              <div 
                className="flex items-center gap-3 pl-4 border-l border-[#d8dbe0] cursor-pointer group"
                onClick={() => setIsProfileOpen(!isProfileOpen)}
              >
                <div className="text-right hidden sm:block">
                  <p className="text-xs font-bold text-gray-700 leading-none mb-1 group-hover:text-primary-main transition-colors">
                    {userProfile?.name || 'Admin User'}
                  </p>
                  <p className="text-[10px] text-gray-400">{userProfile?.user_type || 'Super Admin'}</p>
                </div>
                <div className="w-8 h-8 rounded-full overflow-hidden border border-gray-200 bg-primary-main flex items-center justify-center text-white text-[10px] font-bold shadow-sm transition-transform active:scale-95 group-hover:shadow-md">
                  {userProfile?.name ? userProfile.name.substring(0,2).toUpperCase() : 'AD'}
                </div>
              </div>

              {/* Profile Dropdown Popover */}
              {isProfileOpen && (
                <div className="absolute right-0 mt-3 w-72 bg-white rounded-2xl shadow-2xl border border-gray-100 p-2 z-[100] animate-in fade-in zoom-in-95 duration-200 origin-top-right">
                  <div className="p-4 border-b border-gray-50 mb-2">
                    <h3 className="text-sm font-black text-gray-800 flex items-center gap-2 mb-1">
                      <svg className="w-4 h-4 text-primary-main" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                      내 프로필 정보
                    </h3>
                    <p className="text-[11px] text-gray-400 font-medium">사용자 계정 세부 사항을 확인하세요.</p>
                  </div>

                  {userProfile ? (
                    <div className="p-3 space-y-4">
                      <div className="space-y-3 bg-gray-50/50 rounded-xl p-3 border border-gray-50">
                        <div className="flex flex-col">
                          <span className="text-[10px] font-black text-gray-400 uppercase tracking-tighter">Email</span>
                          <span className="text-[12px] font-bold text-gray-700 break-all">{userProfile.email}</span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[10px] font-black text-gray-400 uppercase tracking-tighter">User Type</span>
                          <div className="flex items-center gap-2">
                            <span className="text-[12px] font-bold text-gray-700">{userProfile.user_type} Member</span>
                            {userProfile.user_type === 'Premium' && (
                              <span className="bg-primary-light text-primary-main px-2 py-0.5 rounded text-[9px] font-black">PRO</span>
                            )}
                          </div>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[10px] font-black text-gray-400 uppercase tracking-tighter">Account Created</span>
                          <span className="text-[12px] font-bold text-gray-700">{formatDate(userProfile.created_at)}</span>
                        </div>
                      </div>

                      <div className="pt-2">
                        <button 
                          onClick={() => {
                            setIsProfileOpen(false);
                            onLogout?.();
                          }}
                          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-red-50 text-red-500 text-xs font-black hover:bg-red-100 transition-colors"
                        >
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                          로그아웃
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="p-4 text-center">
                      <p className="text-xs text-gray-500 mb-4 font-medium">로그인이 되어있지 않습니다.</p>
                      <button 
                        onClick={() => {
                          setIsProfileOpen(false);
                          onLoginClick?.();
                        }}
                        className="w-full bg-primary-main text-white py-2 rounded-xl text-xs font-bold hover:bg-primary-dark shadow-sm"
                      >
                        로그인하러 가기
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-6 sm:p-10">
          <div className="max-w-7xl mx-auto w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
