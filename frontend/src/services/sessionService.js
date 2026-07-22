import api from '../api/api';

export const sessionService = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get(`/sessions/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getById: async (sessionId) => {
    const response = await api.get(`/sessions/${sessionId}`);
    return response.data;
  },

  create: async (sessionData) => {
    const response = await api.post('/sessions/', sessionData);
    return response.data;
  },

  update: async (sessionId, sessionData) => {
    const response = await api.put(`/sessions/${sessionId}`, sessionData);
    return response.data;
  },

  delete: async (sessionId) => {
    const response = await api.delete(`/sessions/${sessionId}`);
    return response.data;
  },
};
