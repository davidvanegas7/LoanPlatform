import api from './api';
import { jwtDecode } from 'jwt-decode';

/**
 * Servicio de autenticación
 */
const AuthService = {
  /**
   * Iniciar sesión
   * @param {string} email - Email del usuario
   * @param {string} password - Contraseña del usuario
   * @returns {Promise} - Promesa con la respuesta
   */
  login: async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });

      const { access_token } = response.data;
      
      // Guardar el token en localStorage
      localStorage.setItem('token', access_token);
      
      // Decodificar el token para obtener los datos del usuario
      const decodedToken = jwtDecode(access_token);
      localStorage.setItem('user', JSON.stringify(decodedToken));
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Registrar un nuevo usuario
   * @param {Object} userData - Datos del usuario
   * @returns {Promise} - Promesa con la respuesta
   */
  register: async (userData) => {
    try {
      const response = await api.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Cerrar sesión
   */
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    // Redirigir al login
    window.location.href = '/login';
  },
  
  /**
   * Verificar si el usuario está autenticado
   * @returns {boolean} - true si está autenticado, false en caso contrario
   */
  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    if (!token) {
      return false;
    }
    
    try {
      const decoded = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      
      // Verificar si el token ha expirado
      if (decoded.exp < currentTime) {
        // El token ha expirado, limpiar storage
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        return false;
      }
      
      return true;
    } catch (e) {
      return false;
    }
  },
  
  /**
   * Obtener el usuario actual
   * @returns {Object|null} - Datos del usuario o null si no está autenticado
   */
  getCurrentUser: () => {
    if (!AuthService.isAuthenticated()) {
      return null;
    }
    
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
  
  /**
   * Obtener el token actual
   * @returns {string|null} - Token o null si no está autenticado
   */
  getToken: () => {
    return localStorage.getItem('token');
  },

  /**
   * Obtener el perfil del usuario desde el API
   * @returns {Promise} - Promesa con la respuesta
   */
  getUserProfile: async () => {
    try {
      const response = await api.get('/auth/me');
      return response.data.user;
    } catch (error) {
      console.error('Error fetching user profile:', error);
      throw error;
    }
  },

  /**
   * Actualizar el perfil del usuario
   * @param {Object} userData - Datos actualizados del usuario
   * @returns {Promise} - Promesa con la respuesta
   */
  updateUserProfile: async (userData) => {
    try {
      const response = await api.put('/auth/me', userData);
      return response.data;
    } catch (error) {
      console.error('Error updating user profile:', error);
      throw error;
    }
  },

  /**
   * Actualizar la configuración del usuario
   * @param {Object} settingsData - Datos actualizados de la configuración
   * @returns {Promise} - Promesa con la respuesta
   */
  updateUserSettings: async (settingsData) => {
    try {
      const response = await api.put('/auth/settings', settingsData);
      return response.data;
    } catch (error) {
      console.error('Error updating user settings:', error);
      throw error;
    }
  }
};

export default AuthService; 