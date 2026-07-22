import api from '../api/api';

export const studentService = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get(`/students/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getById: async (studentId) => {
    const response = await api.get(`/students/${studentId}`);
    return response.data;
  },

  create: async (studentData) => {
    const response = await api.post('/students/', studentData);
    return response.data;
  },

  update: async (studentId, studentData) => {
    const response = await api.put(`/students/${studentId}`, studentData);
    return response.data;
  },

  delete: async (studentId) => {
    const response = await api.delete(`/students/${studentId}`);
    return response.data;
  },
};
