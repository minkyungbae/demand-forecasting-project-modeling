import { useState } from 'react';

// material-ui components
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';

// 기존 프로젝트 내 컴포넌트 활용
import MainCard from 'components/MainCard';

// 이미지 스타일 정의
const processImageStyle = {
  width: '100%',
  height: '120px', // 이미지 높이 조절
  objectFit: 'contain', // 이미지 비율 유지
  marginBottom: '8px',
  borderRadius: '8px'
};

// 중앙 버튼 스타일
const circleButtonStyle = {
  width: 200,
  height: 200,
  borderRadius: '50%',
  border: '2px solid #1890ff', // 강조 색상 적용
  backgroundColor: '#fff',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  alignItems: 'center',
  cursor: 'pointer',
  transition: 'all 0.3s',
  boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  '&:hover': {
    backgroundColor: '#e6f7ff',
    transform: 'scale(1.05)'
  },
  textAlign: 'center'
};

export default function DashboardDefault() {
  return (
    <Box sx={{ p: 3, maxWidth: '1200px', margin: '0 auto' }}>
      {/* 상단 제목 영역 */}
      <MainCard sx={{ bgcolor: '#f8f9fa', textAlign: 'center', py: 3, mb: 4 }}>
        <Typography variant="h1" fontWeight="700">ForeCastly</Typography>
        <Typography variant="h6" color="textSecondary">재고를 좀 더 효율적으로 예측하고 발주할 수 있도록 저희 AI가 도와드리겠습니다..</Typography>
        <Typography variant="h6" color="textSecondary">AI 서비스를 통해 편하고 가독성 있게 결과를 확인하실 수 있습니다.</Typography>
      </MainCard>

      <Typography variant="h5" textAlign="center" sx={{ mb: 6, color: '#555' }}>
        수요 예측 결과가 도출되기까지의 과정
      </Typography>

      {/* 메인 레이아웃 Grid */}
      <Grid container spacing={4} alignItems="center" justifyContent="center">
        
        {/* 왼쪽: 1단계와 4단계 */}
        <Grid item xs={12} md={4}>
          <Stack spacing={4}>
            <MainCard title="파일 분석 결과 반환" sx={{ textAlign: 'center' }}>
              {/* 이미지 삽입부 */}
              <img src="/assets/images/process/step1.png" alt="파일 분석 결과" style={processImageStyle} />
              <Typography variant="body2" color="textSecondary">첫 번째 단계</Typography>
            </MainCard>

            <MainCard title="최종 솔루션 결과 반환" sx={{ textAlign: 'center' }}>
              <img src="/assets/images/process/step4.png" alt="솔루션 결과" style={processImageStyle} />
              <Typography variant="body2" color="textSecondary">최종 단계</Typography>
            </MainCard>
          </Stack>
        </Grid>

        {/* 중앙: 분석 시작 버튼 */}
        <Grid item xs={12} md={4} sx={{ display: 'flex', justifyContent: 'center' }}>
          <Box sx={circleButtonStyle}>
            <Typography variant="h6">분석 시작하기</Typography>
            <Typography variant="h3" fontWeight="bold" color="primary">Start</Typography>
          </Box>
        </Grid>

        {/* 오른쪽: 2단계와 3단계 */}
        <Grid item xs={12} md={4}>
          <Stack spacing={4}>
            <MainCard title="분석 결과 시각적 반환" sx={{ textAlign: 'center' }}>
              <img src="/assets/images/process/step2.png" alt="시각화" style={processImageStyle} />
              <Typography variant="body2" color="textSecondary">두 번째 단계</Typography>
            </MainCard>

            <MainCard title="모델링 및 상관 관계 봔환" sx={{ textAlign: 'center' }}>
              <img src="/assets/images/process/step3.png" alt="예측 모델링" style={processImageStyle} />
              <Typography variant="body2" color="textSecondary">세 번째 단계</Typography>
            </MainCard>
          </Stack>
        </Grid>

      </Grid>
    </Box>
  );
}