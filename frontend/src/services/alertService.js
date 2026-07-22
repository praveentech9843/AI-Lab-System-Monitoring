import api from '../api/api';

export const alertService = {
  getByStudent: async (studentId, skip = 0, limit = 100) => {
    const response = await api.get(`/alerts/student/${studentId}?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getBySession: async (sessionId, skip = 0, limit = 100) => {
    const response = await api.get(`/alerts/session/${sessionId}?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  create: async (alertData) => {
    const response = await api.post('/alerts/', alertData);
    return response.data;
  },

  delete: async (alertId) => {
    const response = await api.delete(`/alerts/${alertId}`);
    return response.data;
  },
};
