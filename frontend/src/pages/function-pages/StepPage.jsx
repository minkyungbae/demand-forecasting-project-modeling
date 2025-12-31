import PropTypes from 'prop-types';

// MUI
import { Box, Typography, Stack, Divider } from '@mui/material';

// project components
import MainCard from 'components/MainCard';

export default function StepPage({ step, title }) {
  return (
    <Box>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        AI 분석 엔진이 데이터를 처리하고 결과를 생성하는 중입니다.
      </Typography>

      {/* 메인 콘텐츠 */}
      <Stack spacing={3}>
        {/* Step Status */}
        <MainCard title="Step Status">
          <Stack spacing={1}>
            <Typography variant="body2">데이터 업로드</Typography>
            <Typography variant="body2" color="primary">
              {step}단계 진행 중
            </Typography>

            <Divider sx={{ my: 1 }} />

            {[1, 2, 3, 4].map((s) => (
              <Typography
                key={s}
                variant="body2"
                color={s === step ? 'primary' : 'text.secondary'}
              >
                {s}단계 {s === step ? '진행 중' : '대기'}
              </Typography>
            ))}
          </Stack>
        </MainCard>

        {/* AI Insights */}
        <MainCard title="AI Insights">
          <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
            현재 {step}단계 분석에서 데이터의 <b>계절성</b>이 강하게 관찰되고
            있습니다. 다음 단계에서는 이를 반영한 예측 모델을 구성할
            예정입니다.
          </Typography>
        </MainCard>
      </Stack>
    </Box>
  );
}

StepPage.propTypes = {
  step: PropTypes.number.isRequired,
  title: PropTypes.string.isRequired
};
