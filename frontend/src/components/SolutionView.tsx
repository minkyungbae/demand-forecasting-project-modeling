
import React from 'react';
import { 
  Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  Area, AreaChart, Legend
} from 'recharts';
import type{ ProductData } from '../types';

interface SolutionViewProps {
  data: ProductData[];
  selectedColumn: string | null;
}

export const SolutionView: React.FC<SolutionViewProps> = ({ selectedColumn }) => {
  // 1. 가공된 예측 데이터 (시뮬레이션)
  const forecastData = [
    { name: '4월', actual: 4000, predict: 4000 },
    { name: '5월', actual: 3000, predict: 3000 },
    { name: '6월', actual: 2000, predict: 2000 },
    { name: '7월', actual: 2780, predict: 2780 },
    { name: '8월(예측)', predict: 3200 },
    { name: '9월(예측)', predict: 3900 },
    { name: '10월(예측)', predict: 4100 },
  ];

  // 2. 상관관계 데이터 (시뮬레이션 - 히트맵 스타일 그리드)
  const correlations = [
    { label: '가격', value: 0.85, color: 'bg-blue-600' },
    { label: '판매량', value: 0.92, color: 'bg-blue-700' },
    { label: '재고', value: 0.45, color: 'bg-blue-300' },
    { label: '날씨', value: 0.12, color: 'bg-blue-100' },
    { label: '할인율', value: 0.78, color: 'bg-blue-500' },
    { label: '광고비', value: 0.65, color: 'bg-blue-400' },
  ];

  return (
    <div className="space-y-6 animate-in fade-in duration-700">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 상단 왼쪽: 상관관계 분석 */}
        <div className="bg-white rounded-xl shadow-sm border border-[#d8dbe0] overflow-hidden flex flex-col h-[400px]">
          <div className="px-6 py-4 border-b border-[#f0f0f0] bg-[#fafafa]">
            <h3 className="text-sm font-bold text-gray-700 uppercase tracking-tight">Feature들의 상관관계 분석 (Heatmap)</h3>
          </div>
          <div className="flex-1 p-6 flex items-center justify-center">
             <div className="grid grid-cols-3 gap-2 w-full max-w-sm">
                {correlations.map((item, idx) => (
                  <div key={idx} className="flex flex-col items-center gap-1">
                    <div className={`w-full h-16 rounded shadow-inner flex items-center justify-center text-white font-bold text-xs ${item.color}`}>
                      {item.value}
                    </div>
                    <span className="text-[10px] font-bold text-gray-500">{item.label}</span>
                  </div>
                ))}
             </div>
          </div>
          <div className="px-6 py-3 bg-blue-50/50 text-[11px] text-blue-600 border-t border-blue-100 italic">
            * 1.0에 가까울수록 강한 양의 상관관계를 의미합니다.
          </div>
        </div>

        {/* 상단 오른쪽: 수요 예측 결과 그래프 */}
        <div className="bg-white rounded-xl shadow-sm border border-[#d8dbe0] overflow-hidden flex flex-col h-[400px]">
          <div className="px-6 py-4 border-b border-[#f0f0f0] bg-[#fafafa]">
            <h3 className="text-sm font-bold text-gray-700 uppercase tracking-tight">수요 예측 결과 그래프 (Target: {selectedColumn || 'Unknown'})</h3>
          </div>
          <div className="flex-1 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={forecastData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorPredict" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1677ff" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#1677ff" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="predict" name="예측치" stroke="#1677ff" fillOpacity={1} fill="url(#colorPredict)" strokeWidth={3} />
                <Line type="monotone" dataKey="actual" name="실제 판매량" stroke="#52c41a" strokeWidth={3} dot={{ r: 4 }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 하단: 솔루션 (결과에 대한 해석) */}
      <div className="bg-white rounded-xl shadow-sm border border-[#d8dbe0] overflow-hidden">
        <div className="px-6 py-4 border-b border-[#f0f0f0] bg-[#fafafa] flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <h3 className="text-sm font-bold text-gray-700 uppercase tracking-tight">AI 최적 솔루션 (결과에 대한 해석)</h3>
        </div>
        <div className="p-8 grid grid-cols-1 md:grid-cols-3 gap-8">
           <div className="space-y-3">
              <div className="text-xs font-black text-primary-main uppercase tracking-widest">Summary</div>
              <p className="text-sm text-gray-600 leading-relaxed">
                현재 분석 결과에 따르면 <strong>{selectedColumn}</strong> 항목은 가격 민감도가 매우 높게 나타나고 있습니다. 
                특히 주말 대비 평일 판매 비중이 20% 높으므로 주중 집중 마케팅이 권장됩니다.
              </p>
           </div>
           <div className="space-y-3">
              <div className="text-xs font-black text-green-600 uppercase tracking-widest">Inventory Strategy</div>
              <p className="text-sm text-gray-600 leading-relaxed">
                8월부터 시작되는 수요 상승에 대비하여 현재 재고 수준을 <strong>약 15% 상향 조정</strong>할 필요가 있습니다. 
                특히 리드타임이 긴 부품 위주로 선제적 발주를 진행하십시오.
              </p>
           </div>
           <div className="space-y-3">
              <div className="text-xs font-black text-orange-500 uppercase tracking-widest">Risk Factor</div>
              <p className="text-sm text-gray-600 leading-relaxed">
                상관관계 분석에서 '날씨' 변수와의 연계성이 낮아졌으나, 글로벌 공급망 이슈에 따른 단가 상승 압박이 존재합니다. 
                판매 목표 미달성 시 <strong>프로모션 예산 10% 증액</strong>을 고려하십시오.
              </p>
           </div>
        </div>
        <div className="bg-gray-50 p-4 border-t border-gray-100 flex justify-end">
           <button className="bg-primary-main text-white px-6 py-2 rounded-lg text-xs font-bold hover:bg-primary-dark transition-all shadow-md">
             상세 리포트 PDF 다운로드
           </button>
        </div>
      </div>
    </div>
  );
};
