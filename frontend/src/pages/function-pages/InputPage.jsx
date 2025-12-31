import { useState } from 'react';

// MUI
import {
  Box,
  Typography,
  Button,
  Stack,
  Divider
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';

// project components
import MainCard from 'components/MainCard';

export default function InputPage() {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  return (
    <Box>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        수요 예측 분석을 위한 데이터를 업로드해 주세요.
      </Typography>

      {/* 업로드 카드 */}
      <MainCard title="데이터 파일 업로드">
        <Stack spacing={3} alignItems="center">
          {/* 드롭 영역 */}
          <Box
            sx={{
              width: '100%',
              border: '2px dashed',
              borderColor: 'primary.light',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              bgcolor: 'grey.50'
            }}
          >
            <UploadFileIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />

            <Typography variant="h6">
              CSV 또는 Excel 파일을 업로드하세요
            </Typography>

            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              드래그 앤 드롭 또는 버튼을 눌러 파일을 선택할 수 있습니다.
            </Typography>

            <Button variant="contained" component="label">
              파일 선택
              <input
                type="file"
                hidden
                accept=".csv,.xlsx"
                onChange={handleFileChange}
              />
            </Button>
          </Box>

          {/* 선택된 파일 정보 */}
          {file && (
            <>
              <Divider flexItem />

              <Box sx={{ width: '100%' }}>
                <Typography variant="subtitle1">선택된 파일</Typography>
                <Typography variant="body2" color="text.secondary">
                  {file.name}
                </Typography>
              </Box>
            </>
          )}

          {/* 다음 단계 버튼 */}
          <Button
            variant="contained"
            size="large"
            disabled={!file}
            sx={{ alignSelf: 'flex-end' }}
          >
            분석 시작
          </Button>
        </Stack>
      </MainCard>
    </Box>
  );
}
