import {
    UploadOutlined,
    SearchOutlined,
    LineChartOutlined,
    RadarChartOutlined,
    CheckSquareOutlined
  } from '@ant-design/icons';
  
  const functionMenu = {
    id: 'function',
    title: 'Function',
    type: 'group',
    children: [
      {
        id: 'function-upload',
        title: '0단계: 파일 업로드',
        type: 'item',
        url: '/function/step0',
        icon: UploadOutlined
      },
      {
        id: 'function-step1',
        title: '1단계: 분석 결과',
        type: 'item',
        url: '/function/step1',
        icon: SearchOutlined
      },
      {
        id: 'function-step2',
        title: '2단계: 시각화 결과',
        type: 'item',
        url: '/function/step2',
        icon: LineChartOutlined
      },
      {
        id: 'function-step3',
        title: '3단계: 모델 분석',
        type: 'item',
        url: '/function/step3',
        icon: RadarChartOutlined
      },
      {
        id: 'function-step4',
        title: '4단계: 최종 솔루션',
        type: 'item',
        url: '/function/step4',
        icon: CheckSquareOutlined
      }
    ]
  };
  
  export default functionMenu;
  