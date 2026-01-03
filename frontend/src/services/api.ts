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

export const register = async (payload: RegisterPayload) => {
    const response = await api.post('/auth/register', payload);
    return response.data;
};

export const login = async (email: string, password: string): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
};

export const uploadCsvFile = async (file: File, targetColumn?: string): Promise<CsvUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (targetColumn) {
        formData.append('target_column', targetColumn);
    }
    const response = await api.post('/files/upload', formData);
    return response.data;
};

// 시각화 관련 API
export const getCountBar = async (fileId: string) => {
    const response = await api.get(`/visualizations/${fileId}/products/count-bar`);
    return response.data;
};

export const getSumBar = async (fileId: string) => {
    const response = await api.get(`/visualizations/${fileId}/products/sum-bar`);
    return response.data;
};

export const getTop10Bar = async (fileId: string) => {
    const response = await api.get(`/visualizations/${fileId}/products/count-bar/top10`);
    return response.data;
};

export const getProductTrend = async (fileId: string, productName: string) => {
    const response = await api.get(`/visualizations/${fileId}/products/${encodeURIComponent(productName)}/trend`);
    return response.data;
};
