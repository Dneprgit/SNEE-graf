import axios from 'axios';

// Используем пустой baseURL - все пути указаны полностью в методах
// Это позволяет работать через nginx reverse proxy без необходимости задавать VITE_API_URL

//const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.MODE === 'production' ? '' : 'http://localhost:8001');

//const API_BASE_URL = 'http://localhost:8001';

//const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Health check
  async healthCheck() {
    const response = await api.get('/api/v1/health');
    return response.data;
  },

  // Получить профиль по умолчанию
  async getDefaultProfile() {
    const response = await api.get('/api/v1/default-profile');
    return response.data;
  },

  // Рассчитать диспетчерский график
  async calculateSchedule(data) {
    const response = await api.post('/api/v1/calculate', data);
    return response.data;
  },

  // Валидация профиля
  async validateProfile(loadProfile) {
    const response = await api.post('/api/v1/validate-profile', loadProfile);
    return response.data;
  },

  // Загрузить Excel файл
  async uploadExcel(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/v1/upload-excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default api;

