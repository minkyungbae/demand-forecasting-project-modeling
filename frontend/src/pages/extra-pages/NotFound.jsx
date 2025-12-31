import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <Box sx={{ textAlign: 'center', mt: 10 }}>
      <Typography variant="h2" gutterBottom>
        404
      </Typography>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        페이지를 찾을 수 없습니다.
      </Typography>

      <Button
        variant="contained"
        sx={{ mt: 3 }}
        onClick={() => navigate('/')}
      >
        홈으로 돌아가기
      </Button>
    </Box>
  );
}
