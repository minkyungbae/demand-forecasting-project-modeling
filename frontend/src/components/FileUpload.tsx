import React, { useRef, useState } from 'react';
import type { FilePayload } from '../types';
import { uploadCsvFile } from '../services/api';

interface FileUploadProps {
  onDataLoaded: (payload: FilePayload) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onDataLoaded }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || isUploading) return;

    try {
      setIsUploading(true);

      const result = await uploadCsvFile(file);

      setUploadedFileName(result.filename);

      onDataLoaded({
        file_id: result.file_id,
        filename: result.filename,
        columns: result.columns,
        row_count: result.row_count,
        matched_quantity_column: result.matched_quantity_column,
        matched_price_column: result.matched_price_column,
      });
    } catch (error) {
      console.error('Upload error:', error);
      alert('파일 업로드 중 오류가 발생했습니다.');
    } finally {
      setIsUploading(false);
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div
      className={`w-full max-w-md p-10 border-2 border-dashed rounded-xl bg-white transition-all text-center
        ${
          isUploading
            ? 'border-gray-300 cursor-not-allowed opacity-70'
            : 'border-[#d8dbe0] hover:border-primary-main cursor-pointer'
        }
      `}
      onClick={() => !isUploading && fileInputRef.current?.click()}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".csv"
        className="hidden"
      />

      <div className="flex flex-col items-center">
        <div className="w-12 h-12 bg-primary-light rounded-full flex items-center justify-center mb-3">
          <svg
            className="w-6 h-6 text-primary-main"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
            />
          </svg>
        </div>

        {isUploading ? (
          <span className="font-semibold text-gray-500">
            업로드 중입니다...
          </span>
        ) : uploadedFileName ? (
          <span className="font-semibold text-primary-main">
            {uploadedFileName} 업로드 완료 ✓
          </span>
        ) : (
          <span className="font-semibold text-gray-700 italic underline">
            여기를 클릭하여 CSV 업로드
          </span>
        )}

        <p className="text-xs text-secondary mt-2">
          CSV 파일은 서버에 저장되어 분석에 사용됩니다.
        </p>
      </div>
    </div>
  );
};
