
import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

// MUI
import {
  Box,
  Typography,
  Button,
  Stack,
  Divider,
  Paper,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  FormGroup,
  Chip,
  Grid
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';

export default function InputPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [columns, setColumns] = useState([]);
  const [config, setConfig] = useState({
    dateColumn: '',
    targetColumn: '',
    featureColumns: []
  });
  const fileInputRef = useRef(null);

  // CSV 파일에서 컬럼명 추출
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      const rows = text.split('\n');
      if (rows.length > 0) {
        // 첫 줄(헤더) 추출 및 클리닝
        const headers = rows[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
        setColumns(headers.filter(h => h !== ''));
      }
    };
    reader.readAsText(selectedFile);
  };

  const handleToggleFeature = (col) => {
    setConfig(prev => {
      const isSelected = prev.featureColumns.includes(col);
      return {
        ...prev,
        featureColumns: isSelected 
          ? prev.featureColumns.filter(c => c !== col)
          : [...prev.featureColumns, col]
      };
    });
  };

  const isReady = config.dateColumn && config.targetColumn;

  const handleStartAnalysis = () => {
    // 실제 서비스라면 여기서 config를 API로 전송하거나 전역 상태에 저장
    console.log('Analysis Config:', config);
    navigate('/function/step1');
  };

  return (
    <Box sx={{ maxWidth: 1000, mx: 'auto', pb: 8 }}>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        업로드한 파일의 컬럼을 확인하고, 수요 예측 모델에 사용할 변수들을 설정해 주세요.
      </Typography>

      <Stack spacing={4}>
        {/* 1. 업로드 카드 */}
        <Paper variant="outlined" sx={{ p: 4, borderRadius: 3, bgcolor: file ? 'grey.50' : 'white' }}>
          <Stack spacing={3} alignItems="center">
            <Box
              sx={{
                width: '100%',
                border: '2px dashed',
                borderColor: file ? 'primary.main' : 'grey.300',
                borderRadius: 3,
                p: 6,
                textAlign: 'center',
                bgcolor: file ? 'primary.lighter' : 'transparent',
                transition: 'all 0.3s ease'
              }}
            >
              <UploadFileIcon sx={{ fontSize: 56, color: file ? 'primary.main' : 'grey.400', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {file ? file.name : 'CSV 또는 Excel 파일을 업로드하세요'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                {file ? `파일 크기: ${(file.size / 1024).toFixed(1)} KB` : '데이터 기반 수요 예측의 첫 걸음입니다.'}
              </Typography>
              <Button variant="contained" component="label" size="large" sx={{ borderRadius: 2 }}>
                {file ? '파일 변경' : '파일 선택'}
                <input type="file" hidden accept=".csv" onChange={handleFileChange} />
              </Button>
            </Box>
          </Stack>
        </Paper>

        {/* 2. 컬럼 설정 카드 (파일 업로드 시에만 노출) */}
        {file && columns.length > 0 && (
          <Paper variant="outlined" sx={{ p: 4, borderRadius: 3 }}>
            <Stack spacing={4}>
              <Box className="flex items-center gap-2">
                <SettingsSuggestIcon color="primary" />
                <Typography variant="h5" sx={{ fontWeight: 600 }}>모델 피처(Feature) 구성</Typography>
              </Box>
              
              <Divider />

              <Grid container spacing={4}>
                {/* 날짜 컬럼 선택 */}
                <Grid item xs={12} md={6}>
                  <FormControl component="fieldset">
                    <FormLabel component="legend" sx={{ fontWeight: 700, mb: 1, color: 'text.primary' }}>
                      날짜 데이터 컬럼 (필수)
                    </FormLabel>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                      시계열 분석을 위한 기준 날짜 컬럼을 선택하세요.
                    </Typography>
                    <RadioGroup
                      value={config.dateColumn}
                      onChange={(e) => setConfig({ ...config, dateColumn: e.target.value })}
                    >
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {columns.map(col => (
                          <FormControlLabel
                            key={`date-${col}`}
                            value={col}
                            control={<Radio size="small" />}
                            label={<Typography variant="body2">{col}</Typography>}
                            sx={{
                              border: '1px solid',
                              borderColor: config.dateColumn === col ? 'primary.main' : 'grey.200',
                              borderRadius: 2,
                              px: 2,
                              py: 0.5,
                              m: 0,
                              bgcolor: config.dateColumn === col ? 'primary.lighter' : 'white'
                            }}
                          />
                        ))}
                      </Box>
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* 예측 대상 선택 */}
                <Grid item xs={12} md={6}>
                  <FormControl component="fieldset">
                    <FormLabel component="legend" sx={{ fontWeight: 700, mb: 1, color: 'text.primary' }}>
                      예측 대상 컬럼 (Target)
                    </FormLabel>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                      수요량을 나타내는 수치 데이터 컬럼을 선택하세요.
                    </Typography>
                    <RadioGroup
                      value={config.targetColumn}
                      onChange={(e) => setConfig({ ...config, targetColumn: e.target.value })}
                    >
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {columns.map(col => (
                          <FormControlLabel
                            key={`target-${col}`}
                            value={col}
                            control={<Radio size="small" color="secondary" />}
                            label={<Typography variant="body2">{col}</Typography>}
                            sx={{
                              border: '1px solid',
                              borderColor: config.targetColumn === col ? 'secondary.main' : 'grey.200',
                              borderRadius: 2,
                              px: 2,
                              py: 0.5,
                              m: 0,
                              bgcolor: config.targetColumn === col ? 'secondary.lighter' : 'white'
                            }}
                          />
                        ))}
                      </Box>
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* 학습 변수 다중 선택 */}
                <Grid item xs={12}>
                  <FormControl component="fieldset" sx={{ width: '100%' }}>
                    <FormLabel component="legend" sx={{ fontWeight: 700, mb: 1, color: 'text.primary' }}>
                      추가 학습 변수 (Features)
                    </FormLabel>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                      예측에 영향을 줄 수 있는 보조 변수들을 선택하세요 (예: 가격, 프로모션 여부 등).
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5 }}>
                      {columns.map(col => {
                        const isMain = config.dateColumn === col || config.targetColumn === col;
                        const isSelected = config.featureColumns.includes(col);
                        
                        return (
                          <Chip
                            key={`feature-${col}`}
                            label={col}
                            onClick={() => !isMain && handleToggleFeature(col)}
                            color={isSelected ? "primary" : "default"}
                            variant={isSelected ? "filled" : "outlined"}
                            disabled={isMain}
                            icon={isSelected ? <CheckCircleOutlineIcon /> : undefined}
                            sx={{ 
                              px: 1, 
                              height: 36, 
                              borderRadius: 2,
                              '&.Mui-disabled': { opacity: 0.5, borderStyle: 'dashed' }
                            }}
                          />
                        );
                      })}
                    </Box>
                  </FormControl>
                </Grid>
              </Grid>

              <Box sx={{ mt: 4, pt: 3, borderTop: '1px solid', borderColor: 'grey.100', display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  size="large"
                  disabled={!isReady}
                  onClick={handleStartAnalysis}
                  startIcon={<CheckCircleOutlineIcon />}
                  sx={{ 
                    px: 6, 
                    py: 1.5, 
                    borderRadius: 2,
                    fontSize: '1rem',
                    fontWeight: 700,
                    boxShadow: isReady ? '0 8px 16px rgba(24, 144, 255, 0.24)' : 'none'
                  }}
                >
                  분석 엔진 가동
                </Button>
              </Box>
            </Stack>
          </Paper>
        )}
      </Stack>
    </Box>
  );
}
