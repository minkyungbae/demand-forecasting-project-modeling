import StepPage from '../pages/function-pages/StepPage';
import InputPage from '../pages/function-pages/InputPage';

const StepFunctionsRoutes = {
  path: 'function',
  children: [
    {
      path: 'step0',
      element: <InputPage step={0} title="분석할 파일 업로드" />
    },

    {
      path: 'step1',
      element: <StepPage step={1} title="분석 결과 반환" />
    },
    {
      path: 'step2',
      element: <StepPage step={2} title="시각화 결과 반환" />
    },
    {
      path: 'step3',
      element: <StepPage step={3} title="모델링 및 상관 관계" />
    },
    {
      path: 'step4',
      element: <StepPage step={4} title="최종 솔루션 결과" />
    }
  ]
};

export default StepFunctionsRoutes;
