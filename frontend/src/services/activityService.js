import api from '../api/api';

export const activityService = {
  getByStudent: async (studentId, skip = 0, limit = 100) => {
    const response = await api.get(`/activities/student/${studentId}?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getBySession: async (sessionId, skip = 0, limit = 100) => {
    const response = await api.get(`/activities/session/${sessionId}?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  create: async (activityData) => {
    const response = await api.post('/activities/', activityData);
    return response.data;
  },

  delete: async (activityId) => {
    const response = await api.delete(`/activities/${activityId}`);
    return response.data;
  },
};
