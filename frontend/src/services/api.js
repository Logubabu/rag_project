import axios from 'axios';

// Use relative URL in production (single container), or localhost for local dev
const API_URL = import.meta.env.PROD ? '' : 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
});

export const uploadFiles = async (files) => {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
  }
  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const chat = async (query) => {
  const response = await api.post('/chat', { query });
  return response.data;
};

export const getDocuments = async () => {
  const response = await api.get('/documents');
  return response.data;
};

export const deleteDocument = async (id) => {
  const response = await api.delete(`/documents/${id}`);
  return response.data;
};
