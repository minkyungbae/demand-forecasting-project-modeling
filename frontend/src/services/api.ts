// ======================================================================
// src/services/api.ts
// 백엔드 API 요청 관리 파일
// ======================================================================

import axios from 'axios';
import type {
    RegisterPayload,
    AuthResponse,
    CsvUploadResponse,
} from '../types';

const api = axios.create({
    baseURL: 'http://192.168.0.17:8000',
    withCredentials: false,
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);


/* =======================
    Auth
======================= */

// 회원가입 API
export const register = async (
    payload: RegisterPayload
) => {
    const response = await api.post('/auth/register', payload);
    return response.data;
};

// 로그인 API
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


/* =======================
    File Upload
======================= */

// CSV 파일 업로드 API
export const uploadCsvFile = async (
    file: File,
    targetColumn?: string
): Promise<CsvUploadResponse> => {

    const formData = new FormData();
    formData.append('file', file);

    if (targetColumn) {
    formData.append('target_column', targetColumn);
    }

    const response = await api.post(
    '/files/upload',
    formData
    // ❗ Content-Type 직접 지정 금지
    );

    return response.data;
};
