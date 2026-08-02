import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
});

export const uploadFiles = async (files, onUploadProgress) => {
  const formData = new FormData();
  Array.from(files).forEach((file) => {
    formData.append('files', file);
  });

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress,
  });
  return response.data;
};

export const chat = async (question) => {
  const response = await api.post('/chat', { question });
  return response.data;
};

export const getDocuments = async () => {
  const response = await api.get('/documents');
  return response.data;
};

export const deleteDocument = async (id) => {
  const response = await api.delete(`/document/${id}`);
  return response.data;
};

export const getStatistics = async () => {
  const response = await api.get('/statistics');
  return response.data;
};

export const reindex = async () => {
  const response = await api.post('/reindex');
  return response.data;
};
