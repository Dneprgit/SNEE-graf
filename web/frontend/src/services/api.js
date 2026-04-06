import axios from 'axios';

// Используем пустой baseURL - все пути указаны полностью в методах
// Это позволяет работать через nginx reverse proxy без необходимости задавать VITE_API_URL


// !!!!!!!! запускаем на сервере
//const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const API_BASE_URL = '';

//const API_BASE_URL = import.meta.env.VITE_API_URL || 
//  (import.meta.env.MODE === 'production' ? '' : 'http://localhost:8002');

//const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

// !!!!!!!! локально запускаем
//const API_BASE_URL = 'http://localhost:8002';


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

  // Получить каталог HTML-задач
  async getHtmlTasks() {
    const response = await api.get('/api/v1/html-tasks');
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

  // Рассчитать оптимальные параметры СНЭЭ
  async calculateOptimalParameters(data) {
    const response = await api.post('/api/v1/calculate-optimal-parameters', data);
    return response.data;
  },

  // =============== QP Варианты ===============
  
  // Рассчитать диспетчерский график (QP)
  async calculateSchedule_qp(data) {
    const response = await api.post('/api/v1/calculate-qp', data);
    return response.data;
  },

  // Рассчитать диспетчерский график (реальный HiGHS QP)
  async calculateSchedule_qp_highs(data) {
    const response = await api.post('/api/v1/calculate-qp-highs', data);
    return response.data;
  },

  // Рассчитать диспетчерский график (модифицированный HiGHS QP)
  async calculateSchedule_qp_highs_modified(data) {
    const response = await api.post('/api/v1/calculate-qp-highs-modified', data);
    return response.data;
  },

  // Рассчитать оптимальные параметры СНЭЭ (QP)
  async calculateOptimalParameters_qp(data) {
    const response = await api.post('/api/v1/calculate-optimal-parameters-qp', data);
    return response.data;
  },
};

export default api;

