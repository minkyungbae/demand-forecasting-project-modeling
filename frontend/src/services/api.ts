import axios from 'axios';

const api = axios.create({
    baseURL: 'http://192.168.0.17:8000',
    withCredentials: false,
});

// 회원가입 요청 타입
export interface RegisterPayload {
    username: string;
    password: string;
    name: string;
    user_type?: 'admin' | 'premium' | 'basic';
  }
  
  // 회원가입 API 함수
  export const register = async (
    payload: RegisterPayload
  ) => {
    const response = await api.post('/auth/register', payload);
    return response.data;
  };
  