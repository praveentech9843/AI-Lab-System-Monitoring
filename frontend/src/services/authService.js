import api from '../api/api';

export const authService = {
  // OAuth2 password flow login (POST /auth/token)
  login: async (credentials) => {
    const params = new URLSearchParams();
    params.append('username', credentials.username || credentials.email);
    params.append('password', credentials.password);

    const response = await api.post('/auth/token', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  // Student specific JSON login
  loginStudent: async (credentials) => {
    const response = await api.post('/auth/student/login', credentials);
    return response.data;
  },

  // Faculty specific JSON login
  loginFaculty: async (credentials) => {
    const response = await api.post('/auth/faculty/login', credentials);
    return response.data;
  },

  // Student registration
  registerStudent: async (studentData) => {
    const response = await api.post('/auth/student/register', studentData);
    return response.data;
  },

  // Faculty registration
  registerFaculty: async (facultyData) => {
    const response = await api.post('/auth/faculty/register', facultyData);
    return response.data;
  },
};
