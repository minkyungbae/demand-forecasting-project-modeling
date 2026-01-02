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


// 로그인 요청 타입
export interface AuthResponse {
    access_token: string;
    token_type: string;
    user?: {
        id: number;
        username: string;
        name: string;
        user_type: string;
    }
}

// 로그인 API 함수
export const login = async (
    username: string,
    password: string 
): Promise<AuthResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    });
    return response.data;
};
    