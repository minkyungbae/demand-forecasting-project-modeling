
import React, { useMemo } from 'react';
import { 
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    Line, ComposedChart
} from 'recharts';
import type{ ProductData } from '../types';

interface DataDashboardProps {
  data: ProductData[];
}

export const DataDashboard: React.FC<DataDashboardProps> = ({ data }) => {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    // 데이터 집계
    const map: Record<string, { name: string; totalQty: number; totalSales: number }> = {};
    data.forEach(item => {
      const name = String(item.product_name || '기타').trim();
      const qty = Number(item.Quantity) || 0;
      const price = Number(item.Price) || 0;
      
      if (!map[name]) map[name] = { name, totalQty: 0, totalSales: 0 };
      map[name].totalQty += qty;
      // Price가 단가인지 총액인지에 따라 다르지만 보통 Price * Qty가 매출
      map[name].totalSales += (qty * price);
    });

    // 매출액 기준 상위 8개 상품 선정
    return Object.values(map)
      .sort((a, b) => b.totalSales - a.totalSales)
      .slice(0, 8);
  }, [data]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-gray-100 shadow-2xl rounded-lg text-xs min-w-[150px]">
          <p className="font-bold text-gray-800 mb-2 border-b border-gray-50 pb-2">{label}</p>
          {payload.map((p: any, i: number) => (
            <div key={i} className="flex justify-between gap-6 py-1">
              <span className="text-gray-500 font-medium">{p.name}</span>
              <span className="font-bold" style={{ color: p.color }}>
                {p.name.includes('매출') ? `${p.value.toLocaleString()}원` : `${p.value.toLocaleString()}개`}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* 요약 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">총 상품 수</p>
          <h4 className="text-2xl font-bold text-gray-800">{new Set(data.map(d => d.product_name)).size}종</h4>
        </div>
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">총 판매량</p>
          <h4 className="text-2xl font-bold text-primary-main">{data.reduce((sum, d) => sum + d.Quantity, 0).toLocaleString()}개</h4>
        </div>
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm border-l-4 border-l-green-500">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">예상 총 매출</p>
          <h4 className="text-2xl font-bold text-green-600">
            {data.reduce((sum, d) => sum + (d.Quantity * d.Price), 0).toLocaleString()}원
          </h4>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* 상품명 기반 판매량 막대 차트 (Bar) */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col h-[450px]">
          <div className="px-6 py-5 border-b border-gray-50 flex items-center justify-between bg-white">
            <div>
              <h3 className="text-base font-bold text-gray-800">상품별 판매 비중</h3>
              <p className="text-[11px] text-gray-400 mt-0.5">상위 8개 품목 수량 분석</p>
            </div>
          </div>
          <div className="flex-1 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 30, top: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f0f0f0" />
                <XAxis type="number" hide />
                <YAxis 
                  dataKey="name" 
                  type="category" 
                  width={110} 
                  tick={{ fontSize: 11, fill: '#595959', fontWeight: 500 }} 
                  tickFormatter={(v) => v.length > 10 ? `${v.substring(0, 10)}..` : v}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f5f5f5' }} />
                <Bar 
                  dataKey="totalQty" 
                  name="판매 수량" 
                  fill="#1677ff" 
                  radius={[0, 4, 4, 0]} 
                  barSize={20}
                  animationDuration={1500}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 매출액 및 판매량 추이 꺾은선 차트 (Line) */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col h-[450px]">
          <div className="px-6 py-5 border-b border-gray-50 flex items-center justify-between bg-white">
            <div>
              <h3 className="text-base font-bold text-gray-800">매출 및 판매량 추이</h3>
              <p className="text-[11px] text-gray-400 mt-0.5">상품별 상관관계 분석</p>
            </div>
            <div className="flex gap-4">
               <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-green-500"></span>
                  <span className="text-[10px] font-bold text-gray-500">매출액</span>
               </div>
               <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                  <span className="text-[10px] font-bold text-gray-500">판매량</span>
               </div>
            </div>
          </div>
          <div className="flex-1 p-4 pb-12">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 20, right: 20, left: 0, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                <XAxis 
                  dataKey="name" 
                  tick={{ fontSize: 10, fill: '#8c8c8c' }} 
                  interval={0} 
                  angle={-35} 
                  textAnchor="end" 
                  height={50}
                />
                {/* Fixed: Use yAxisId instead of yId */}
                <YAxis 
                  yAxisId="left"
                  tick={{ fontSize: 10, fill: '#bfbfbf' }} 
                  axisLine={false} 
                  tickLine={false} 
                  tickFormatter={(v) => `${(v/10000).toLocaleString()}만`} 
                />
                {/* Fixed: Use yAxisId instead of yId */}
                <YAxis 
                  yAxisId="right"
                  orientation="right"
                  tick={{ fontSize: 10, fill: '#bfbfbf' }} 
                  axisLine={false} 
                  tickLine={false} 
                />
                <Tooltip content={<CustomTooltip />} />
                {/* Fixed: Use yAxisId instead of yId */}
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="totalSales" 
                  name="매출 금액" 
                  stroke="#52c41a" 
                  strokeWidth={3} 
                  dot={{ r: 4, fill: '#fff', strokeWidth: 2, stroke: '#52c41a' }} 
                  activeDot={{ r: 6 }}
                  animationDuration={2000}
                />
                {/* Fixed: Use yAxisId instead of yId */}
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="totalQty" 
                  name="판매 수량" 
                  stroke="#1677ff" 
                  strokeWidth={2} 
                  strokeDasharray="5 5"
                  dot={{ r: 3, fill: '#fff', strokeWidth: 2, stroke: '#1677ff' }} 
                  animationDuration={2000}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
};
