import { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';

// material-ui
import Button from '@mui/material/Button';
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import Grid from '@mui/material/Grid';
import Link from '@mui/material/Link';
import InputAdornment from '@mui/material/InputAdornment';
import InputLabel from '@mui/material/InputLabel';
import OutlinedInput from '@mui/material/OutlinedInput';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';

// third-party
import * as Yup from 'yup';
import { Formik } from 'formik';

// project imports
import IconButton from 'components/@extended/IconButton';
import AnimateButton from 'components/@extended/AnimateButton';
import { strengthColor, strengthIndicator } from 'utils/password-strength';

// assets
import EyeOutlined from '@ant-design/icons/EyeOutlined';
import EyeInvisibleOutlined from '@ant-design/icons/EyeInvisibleOutlined';

// ============================|| JWT - REGISTER ||============================ //

export default function AuthRegister() {
  const [level, setLevel] = useState();
  const [showPassword, setShowPassword] = useState(false);

  {/* 보안 문제로 API키를 발급받아야 제공할 수 있어서 기능 구현 멈추었음. 25년 12월 31일 */}
  // // 소셜 로그인 리다이렉트 핸들러
  // const handleSocialLogin = (platform) => {
  //   const currentDomain = window.location.origin; // 현재 접속한 주소 (localhost 혹은 실제 도메인)
  //   const redirectUri = `${currentDomain}/login/callback`; // 가입 완료 후 돌아올 주소

  //   let authUrl = '';

  //   switch (platform) {
  //     case 'google':
  //       // 구글 로그인 화면으로 이동
  //       authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_GOOGLE_CLIENT_ID&redirect_uri=${redirectUri}&response_type=token&scope=email profile`;
  //       break;
  //     case 'naver':
  //       // 네이버 로그인 화면으로 이동
  //       authUrl = `https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id=YOUR_NAVER_CLIENT_ID&redirect_uri=${redirectUri}&state=RANDOM_STATE`;
  //       break;
  //     case 'kakao':
  //       // 카카오 로그인 화면으로 이동
  //       authUrl = `https://kauth.kakao.com/oauth/authorize?client_id=YOUR_KAKAO_CLIENT_ID&redirect_uri=${redirectUri}&response_type=code`;
  //       break;
  //     default:
  //       break;
  //   }

  //   // 실제 키값이 입력되지 않았을 경우 안내
  //   if (authUrl.includes('YOUR_')) {
  //     alert(`${platform} 개발자 센터에서 발급받은 실제 Client ID를 코드에 넣어야 사용자들이 가입할 수 있습니다.`);
  //   } else {
  //     window.location.href = authUrl;
  //   }
  // };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleMouseDownPassword = (event) => {
    event.preventDefault();
  };

  const changePassword = (value) => {
    const temp = strengthIndicator(value);
    setLevel(strengthColor(temp));
  };

  useEffect(() => {
    changePassword('');
  }, []);

  return (
    <>
      <Grid container spacing={3}>

        {/* 기존 회원가입 폼 */}
        <Grid item xs={12}>
          <Formik
            initialValues={{
              firstname: '',
              email: '',
              password: '',
              submit: null
            }}
            validationSchema={Yup.object().shape({
              firstname: Yup.string().max(255).required('성함은 필수 입력입니다.'),
              email: Yup.string().email('Must be a valid email').max(255).required('Email is required'),
              password: Yup.string()
                .required('Password is required')
                .test('no-leading-trailing-whitespace', 'Password cannot start or end with spaces', (value) => value === value.trim())
                .max(10, 'Password must be less than 10 characters')
            })}
          >
            {({ errors, handleBlur, handleChange, touched, values }) => (
              <form noValidate>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Stack spacing={1}>
                      <InputLabel htmlFor="firstname-signup">성함*</InputLabel>
                      <OutlinedInput
                        id="firstname-login"
                        type="firstname"
                        value={values.firstname}
                        name="firstname"
                        onBlur={handleBlur}
                        onChange={handleChange}
                        placeholder="신짱구"
                        fullWidth
                        error={Boolean(touched.firstname && errors.firstname)}
                      />
                    </Stack>
                    {touched.firstname && errors.firstname && (
                      <FormHelperText error id="helper-text-firstname-signup">
                        {errors.firstname}
                      </FormHelperText>
                    )}
                  </Grid>
                  <Grid item xs={12}>
                    <Stack spacing={1}>
                      <InputLabel htmlFor="email-signup">이메일*</InputLabel>
                      <OutlinedInput
                        fullWidth
                        error={Boolean(touched.email && errors.email)}
                        id="email-login"
                        type="email"
                        value={values.email}
                        name="email"
                        onBlur={handleBlur}
                        onChange={handleChange}
                        placeholder="abc123@example.com"
                      />
                    </Stack>
                    {touched.email && errors.email && (
                      <FormHelperText error id="helper-text-email-signup">
                        {errors.email}
                      </FormHelperText>
                    )}
                  </Grid>
                  <Grid item xs={12}>
                    <Stack spacing={1}>
                      <InputLabel htmlFor="password-signup">비밀번호</InputLabel>
                      <OutlinedInput
                        fullWidth
                        error={Boolean(touched.password && errors.password)}
                        id="password-signup"
                        type={showPassword ? 'text' : 'password'}
                        value={values.password}
                        name="password"
                        onBlur={handleBlur}
                        onChange={(e) => {
                          handleChange(e);
                          changePassword(e.target.value);
                        }}
                        endAdornment={
                          <InputAdornment position="end">
                            <IconButton
                              aria-label="toggle password visibility"
                              onClick={handleClickShowPassword}
                              onMouseDown={handleMouseDownPassword}
                              edge="end"
                              color="secondary"
                            >
                              {showPassword ? <EyeOutlined /> : <EyeInvisibleOutlined />}
                            </IconButton>
                          </InputAdornment>
                        }
                        placeholder="******"
                      />
                    </Stack>
                    {touched.password && errors.password && (
                      <FormHelperText error id="helper-text-password-signup">
                        {errors.password}
                      </FormHelperText>
                    )}
                    <FormControl fullWidth sx={{ mt: 2 }}>
                      <Grid container spacing={2} alignItems="center">
                        <Grid item>
                          <Box sx={{ bgcolor: level?.color, width: 85, height: 8, borderRadius: '7px' }} />
                        </Grid>
                        <Grid item>
                          <Typography variant="subtitle1" fontSize="0.75rem">
                            {level?.label}
                          </Typography>
                        </Grid>
                      </Grid>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2">
                      가입함으로써 귀하는 당사의 &nbsp;
                      <Link variant="subtitle2" component={RouterLink} to="#">
                        서비스 약관
                      </Link>
                      &nbsp; 및 &nbsp;
                      <Link variant="subtitle2" component={RouterLink} to="#">
                        개인정보 처리방침
                      </Link>에 동의하게 됩니다.
                    </Typography>
                  </Grid>
                  {errors.submit && (
                    <Grid item xs={12}>
                      <FormHelperText error>{errors.submit}</FormHelperText>
                    </Grid>
                  )}
                  <Grid item xs={12}>
                    <AnimateButton>
                      <Button fullWidth size="large" variant="contained" color="primary" type="submit">
                        계정 만들기
                      </Button>
                    </AnimateButton>
                  </Grid>
                </Grid>
              </form>
            )}
          </Formik>
        </Grid>

        {/* 소셜 로그인 버튼 섹션 */}
        <Grid item xs={12}>
          {/* 화면에 구분선 추가 */}
          <Divider sx={{ my: 1 }}>
            <Typography variant="caption" color="textSecondary">
              또는 다음으로 로그인
            </Typography>
          </Divider>

          <Stack 
            direction="row"           // 가로 방향 나열
            spacing={3}               // 버튼 사이 간격
            justifyContent="center"   // 중앙 정렬
            alignItems="center"
            sx={{ mt: 2, mb: 2 }}     // 상하 여백 (필요시)
          >
            {/* Google 버튼 */}
            <AnimateButton>
              <Button
                variant="outlined"
                color="secondary"
                onClick={() => handleSocialLogin('google')}
                sx={{ 
                  minWidth: '55px', 
                  width: '110px', 
                  height: '55px', 
                  borderRadius: '5%', // 동그랗게 만들기
                  p: 0
                }}
              >
                Google
              </Button>
            </AnimateButton>

            {/* 네이버 버튼 */}
            <AnimateButton>
              <Button
                variant="outlined"
                onClick={() => handleSocialLogin('naver')}
                sx={{ 
                  minWidth: '55px', 
                  width: '110px', 
                  height: '55px', 
                  borderRadius: '5%',
                  color: '#03C75A', 
                  borderColor: '#03C75A', 
                  '&:hover': { borderColor: '#02b350', bgcolor: '#f0fff5' },
                  p: 0
                }}
              >
                Naver
              </Button>
            </AnimateButton>

            {/* 카카오 버튼 */}
            <AnimateButton>
              <Button
                variant="outlined"
                onClick={() => handleSocialLogin('kakao')}
                sx={{ 
                  minWidth: '55px', 
                  width: '110px', 
                  height: '55px', 
                  borderRadius: '5%',
                  color: '#3C1E1E', 
                  borderColor: '#FEE500', 
                  bgcolor: '#FEE500', 
                  '&:hover': { bgcolor: '#fada0a', borderColor: '#fada0a' },
                  p: 0
                }}
              >
                Kakao
              </Button>
            </AnimateButton>
          </Stack>
        </Grid>
      </Grid>
    </>
  );
}