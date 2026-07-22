import api from '../api/api';

export const facultyService = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get(`/faculty/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getById: async (facultyId) => {
    const response = await api.get(`/faculty/${facultyId}`);
    return response.data;
  },

  create: async (facultyData) => {
    const response = await api.post('/faculty/', facultyData);
    return response.data;
  },

  update: async (facultyId, facultyData) => {
    const response = await api.put(`/faculty/${facultyId}`, facultyData);
    return response.data;
  },

  delete: async (facultyId) => {
    const response = await api.delete(`/faculty/${facultyId}`);
    return response.data;
  },
};
