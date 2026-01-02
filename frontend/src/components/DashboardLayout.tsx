
import React from 'react';
import { Sidebar } from './Sidebar';

interface DashboardLayoutProps {
  children: React.ReactNode;
  currentStep: number;
  userName?: string | null;
  onDashboardClick?: () => void;
  onStepOneClick?: () => void;
  onStepTwoClick?: () => void;
  onStepThreeClick?: () => void;
  onLoginClick?: () => void;
  onSignupClick?: () => void;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ 
  children, 
  currentStep, 
  userName,
  onDashboardClick,
  onStepOneClick,
  onStepTwoClick,
  onStepThreeClick,
  onLoginClick,
  onSignupClick
}) => {
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
            <div className="flex items-center gap-3 pl-4 border-l border-[#d8dbe0]">
              <div className="text-right hidden sm:block">
                <p className="text-xs font-bold text-gray-700 leading-none mb-1">{userName || 'Admin User'}</p>
                <p className="text-[10px] text-gray-400">{userName ? 'Member' : 'Super Admin'}</p>
              </div>
              <div className="w-8 h-8 rounded-full overflow-hidden border border-gray-200 bg-primary-main flex items-center justify-center text-white text-[10px] font-bold shadow-sm">
                {userName ? userName.substring(0,2).toUpperCase() : 'AD'}
              </div>
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
