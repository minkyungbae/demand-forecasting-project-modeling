
import React, { useRef, useState } from 'react';
import type { FilePayload } from '../types';
import { uploadCsvFile } from '../services/api';

interface FileUploadProps {
  onDataLoaded: (payload: FilePayload) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onDataLoaded }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [headers, setHeaders] = useState<string[]>([]);
  const [selectedTargetColumn, setSelectedTargetColumn] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  // 1. 파일 선택 및 로컬 헤더 추출
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      if (text) {
        const firstLine = text.split(/\r?\n/)[0];
        // 쉼표, 세미콜론, 탭 대응
        const delimiter = firstLine.includes(';') ? ';' : (firstLine.includes('\t') ? '\t' : ',');
        const extractedHeaders = firstLine
          .split(delimiter)
          .map(h => h.replace(/["\r\n]/g, '').trim())
          .filter(h => h.length > 0);
        
        setHeaders(extractedHeaders);
        setSelectedFile(file);
        setSelectedTargetColumn(null);
      }
    };
    reader.readAsText(file);
  };

  // 2. 최종 서버 업로드 및 분석
  const handleUpload = async () => {
    if (!selectedFile || !selectedTargetColumn || isUploading) return;

    try {
      setIsUploading(true);
      const result = await uploadCsvFile(selectedFile, selectedTargetColumn);

      onDataLoaded({
        file_id: result.file_id,
        filename: result.filename,
        columns: result.columns || headers,
        row_count: result.row_count,
        matched_quantity_column: result.matched_quantity_column,
        matched_price_column: result.matched_price_column,
        data: (result as any).data || [] 
      } as any);

    } catch (error: any) {
      console.error('Upload error details:', error.response?.data || error.message);
      alert(`오류: ${error.response?.data?.detail || '서버와 통신 중 문제가 발생했습니다.'}`);
    }
  };

  const resetSelection = () => {
    setSelectedFile(null);
    setHeaders([]);
    setSelectedTargetColumn(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-6 animate-in fade-in duration-500">
      {/* 1단계: 파일 업로드 칸 */}
      <div 
        className={`relative w-full p-8 border-2 border-dashed rounded-2xl transition-all overflow-hidden
          ${selectedFile 
            ? 'bg-blue-50/30 border-primary-main shadow-inner py-6' 
            : 'bg-white border-gray-200 hover:border-primary-main hover:bg-primary-light/10 cursor-pointer group'
          }`}
        onClick={() => !selectedFile && fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".csv"
          className="hidden"
        />
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all
              ${selectedFile ? 'bg-primary-main text-white' : 'bg-primary-light text-primary-main group-hover:scale-110'}
            `}>
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
            </div>
            <div>
              <h3 className={`font-black tracking-tight ${selectedFile ? 'text-primary-dark text-base' : 'text-gray-800 text-lg'}`}>
                {selectedFile ? selectedFile.name : '분석할 CSV 파일을 업로드하세요'}
              </h3>
              <p className="text-xs text-gray-400 font-medium">
                {selectedFile ? `${(selectedFile.size / 1024).toFixed(1)} KB | 파일이 선택되었습니다.` : 'CSV 형식을 지원합니다 (최대 50MB)'}
              </p>
            </div>
          </div>
          
          {selectedFile && (
            <button 
              onClick={(e) => { e.stopPropagation(); resetSelection(); }}
              className="px-3 py-1.5 rounded-lg border border-gray-200 text-gray-400 hover:text-red-500 hover:border-red-100 transition-all text-[11px] font-bold bg-white"
            >
              파일 변경
            </button>
          )}
        </div>
      </div>

      {/* 2단계: 컬럼 선택 영역 (파일 업로드 후에만 나타남) */}
      {selectedFile && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-xl overflow-hidden animate-in slide-in-from-top-4 duration-500">
          <div className="p-5 border-b border-gray-50 flex items-center justify-between bg-gray-50/30">
            <div>
              <h3 className="text-sm font-black text-gray-700 uppercase tracking-wider">타겟 컬럼 설정</h3>
              <p className="text-[11px] text-gray-400 mt-0.5">예측의 기준이 될 주요 컬럼을 하나 선택해주세요.</p>
            </div>
            {selectedTargetColumn && (
               <div className="flex items-center gap-2 px-3 py-1 bg-green-50 text-green-600 rounded-full border border-green-100">
                 <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                 <span className="text-[10px] font-black uppercase">Ready</span>
               </div>
            )}
          </div>

          <div className="p-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {headers.map((header) => (
                <button
                  key={header}
                  onClick={() => setSelectedTargetColumn(header)}
                  disabled={isUploading}
                  className={`px-4 py-3 rounded-xl text-[11px] font-black transition-all border text-center truncate
                    ${selectedTargetColumn === header 
                      ? 'bg-primary-main text-white border-primary-main shadow-lg ring-2 ring-primary-light scale-[1.02]' 
                      : 'bg-white text-gray-500 border-gray-100 hover:border-primary-main hover:bg-gray-50'
                    }
                    ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                >
                  {header}
                </button>
              ))}
            </div>

            <div className="mt-8 pt-6 border-t border-gray-50">
              <button
                onClick={handleUpload}
                disabled={!selectedTargetColumn || isUploading}
                className={`w-full py-4 rounded-xl font-black text-sm shadow-xl transition-all flex items-center justify-center gap-3
                  ${selectedTargetColumn && !isUploading
                    ? 'bg-primary-main text-white hover:bg-primary-dark hover:shadow-primary-light active:scale-95'
                    : 'bg-gray-100 text-gray-300 cursor-not-allowed shadow-none'
                  }
                `}
              >
                {isUploading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    서버 분석 및 데이터 동기화 중...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
                    CSV 파일 분석 시작하기
                  </>
                )}
              </button>
              {!selectedTargetColumn && !isUploading && (
                <p className="mt-4 text-center text-[11px] text-gray-400 font-bold uppercase tracking-widest animate-pulse">
                  Step 2: 타겟 컬럼을 선택하여 분석을 시작하세요
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 보안 문구 */}
      <div className="flex justify-center items-center gap-8 opacity-40 grayscale">
        <div className="flex items-center gap-2">
          <svg className="w-3 h-3 text-primary-main" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944a11.954 11.954 0 007.834 3.056A11.954 11.954 0 0110 18.056a11.954 11.954 0 01-7.834-3.056zM10 8a1 1 0 011 1v3a1 1 0 11-2 0V9a1 1 0 011-1zm0-4a1 1 0 100 2 1 1 0 000-2z" clipRule="evenodd" /></svg>
          <span className="text-[10px] font-black uppercase">AES-256 Encrypted</span>
        </div>
        <div className="flex items-center gap-2">
          <svg className="w-3 h-3 text-primary-main" fill="currentColor" viewBox="0 0 20 20"><path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1a1 1 0 10-2 0v1a1 1 0 102 0zM13 16v-1a1 1 0 10-2 0v1a1 1 0 102 0zM16.464 14.95a1 1 0 10-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707z" /></svg>
          <span className="text-[10px] font-black uppercase">Real-time Processing</span>
        </div>
      </div>
    </div>
  );
};
