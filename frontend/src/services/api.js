import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

// Crear una instancia de axios con la URL base y configuración para CORS
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:5001/api/v1',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: true,
});

// Interceptor para agregar el token de autenticación a todas las solicitudes
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y errores
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Si el error es 401 (no autorizado) y no es un reintento
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Verificar si el token ha expirado
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const decoded = jwtDecode(token);
          const currentTime = Date.now() / 1000;
          
          // Si el token ha expirado, redirigir al login
          if (decoded.exp < currentTime) {
            localStorage.removeItem('token');
            window.location.href = '/login';
            return Promise.reject(error);
          }
        } catch (e) {
          localStorage.removeItem('token');
          window.location.href = '/login';
          return Promise.reject(error);
        }
      }
      
      // Si no hay token, redirigir al login
      window.location.href = '/login';
      return Promise.reject(error);
    }
    
    return Promise.reject(error);
  }
);

export default api; 