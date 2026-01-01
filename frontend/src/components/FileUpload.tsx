
import React, { useRef } from 'react';
import type{ ProductData, FilePayload } from '../types';

interface FileUploadProps {
  onDataLoaded: (payload: FilePayload) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onDataLoaded }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const buffer = await file.arrayBuffer();
      
      // 1. UTF-8로 먼저 디코딩 시도
      let decoder = new TextDecoder('utf-8', { fatal: true });
      let text = '';
      try {
        text = decoder.decode(buffer);
      } catch (e) {
        // UTF-8 디코딩 실패 시 EUC-KR로 시도
        text = new TextDecoder('euc-kr').decode(buffer);
      }

      // 2. BOM(Byte Order Mark) 제거 및 보이지 않는 제어 문자 제거
      // \uFEFF 는 UTF-8 BOM, \u0000-\u001F 는 제어 문자
      const cleanText = text
        .replace(/^\uFEFF/, '')
        .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F-\u009F]/g, '')
        .trim();

      const rows = cleanText.split(/\r?\n/);
      
      if (rows.length < 2) {
        alert('파일에 데이터가 충분하지 않습니다.');
        return;
      }

      const parseCSVLine = (line: string) => {
        const result = [];
        let cur = '';
        let inQuotes = false;
        for (let i = 0; i < line.length; i++) {
          const char = line[i];
          if (char === '"') {
            inQuotes = !inQuotes;
          } else if (char === ',' && !inQuotes) {
            // 따옴표 제거 및 불필요한 공백/특수문자 제거
            result.push(cur.trim().replace(/^"|"$/g, '').replace(/[\u200B-\u200D\uFEFF]/g, ''));
            cur = '';
          } else {
            cur += char;
          }
        }
        result.push(cur.trim().replace(/^"|"$/g, '').replace(/[\u200B-\u200D\uFEFF]/g, ''));
        return result;
      };

      // 헤더 정제: 문자열 앞뒤 이상한 기호나 보이지 않는 문자 최종 제거
      const rawHeaders = parseCSVLine(rows[0]).map(h => h.replace(/[^\w\sㄱ-ㅎㅏ-ㅣ가-힣_]/gi, '').trim() || h);

      const getIndex = (aliases: string[]) => 
        rawHeaders.findIndex(h => aliases.some(alias => h.toLowerCase().includes(alias.toLowerCase())));

      const nameIdx = getIndex(['product_name', '상품명', '제품', 'item']);
      const priceIdx = getIndex(['price', '가격', '단가', 'sales', '매출']);
      const qtyIdx = getIndex(['quantity', '판매량', '수량', 'qty', 'count']);

      const parsedData: ProductData[] = rows.slice(1)
        .filter(row => row.trim() !== '')
        .map(row => {
          const values = parseCSVLine(row);
          const obj: any = {};
          rawHeaders.forEach((header, idx) => {
            obj[header] = values[idx];
          });

          return {
            ...obj,
            product_name: values[nameIdx] || 'Unknown',
            Price: priceIdx !== -1 ? parseFloat((values[priceIdx] || '0').replace(/[^0-9.-]+/g, "")) || 0 : 0,
            Quantity: qtyIdx !== -1 ? parseInt((values[qtyIdx] || '0').replace(/[^0-9-]+/g, "")) || 0 : 0
          };
        })
        .filter(item => item.product_name !== 'Unknown');

      onDataLoaded({ data: parsedData, headers: rawHeaders });
    } catch (error) {
      console.error('File error:', error);
      alert('파일 처리 중 오류가 발생했습니다.');
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="w-full max-w-md p-10 border-2 border-dashed border-[#d8dbe0] rounded-xl bg-white hover:border-primary-main transition-all cursor-pointer text-center"
         onClick={() => fileInputRef.current?.click()}>
      <input type="file" ref={fileInputRef} onChange={handleFileChange} accept=".csv" className="hidden" />
      <div className="flex flex-col items-center">
        <div className="w-12 h-12 bg-primary-light rounded-full flex items-center justify-center mb-3">
          <svg className="w-6 h-6 text-primary-main" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
        </div>
        <span className="font-semibold text-gray-700 italic underline">여기를 클릭하여 CSV 업로드</span>
        <p className="text-xs text-secondary mt-2">한글(EUC-KR/UTF-8) 인코딩을 자동으로 감지합니다.</p>
      </div>
    </div>
  );
};
