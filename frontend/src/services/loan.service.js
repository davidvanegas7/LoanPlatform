import api from './api';

/**
 * Servicio para manejar los préstamos
 */
const LoanService = {
  /**
   * Obtener todos los préstamos
   * @param {Object} params - Parámetros de filtrado y paginación
   * @returns {Promise} - Promesa con la respuesta
   */
  getAll: async (params = {}) => {
    try {
      const response = await api.get('/loans/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Obtener un préstamo por ID
   * @param {number} id - ID del préstamo
   * @returns {Promise} - Promesa con la respuesta
   */
  getById: async (id) => {
    try {
      const response = await api.get(`/loans/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Obtener los pagos de un préstamo
   * @param {number} id - ID del préstamo
   * @param {Object} params - Parámetros de filtrado y paginación
   * @returns {Promise} - Promesa con la respuesta
   */
  getPayments: async (id, params = {}) => {
    try {
      const response = await api.get(`/payments/loan/${id}`, { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Crear un nuevo pago para un préstamo
   * @param {number} id - ID del préstamo
   * @param {Object} paymentData - Datos del pago
   * @returns {Promise} - Promesa con la respuesta
   */
  createPayment: async (id, paymentData) => {
    try {
      const response = await api.post(`/loans/${id}/payments/`, paymentData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Obtener el historial de un préstamo
   * @param {number} id - ID del préstamo
   * @returns {Promise} - Promesa con la respuesta
   */
  getHistory: async (id) => {
    try {
      const response = await api.get(`/loans/${id}/history/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Cerrar un préstamo (pagarlo completamente)
   * @param {number} id - ID del préstamo
   * @returns {Promise} - Promesa con la respuesta
   */
  close: async (id) => {
    try {
      const response = await api.post(`/loans/${id}/close/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Obtener resumen del préstamo
   * @param {number} id - ID del préstamo
   * @returns {Promise} - Promesa con la respuesta
   */
  getSummary: async (id) => {
    try {
      const response = await api.get(`/loans/${id}/summary/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default LoanService; 