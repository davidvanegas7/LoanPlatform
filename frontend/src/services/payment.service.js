import api from './api';

/**
 * Servicio para manejar los pagos
 */
const PaymentService = {
  /**
   * Obtener todos los pagos
   * @param {Object} params - Parámetros de filtrado y paginación
   * @returns {Promise} - Promesa con la respuesta
   */
  getAll: async (params = {}) => {
    try {
      const response = await api.get('/payments/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Obtener un pago por ID
   * @param {number} id - ID del pago
   * @returns {Promise} - Promesa con la respuesta
   */
  getById: async (id) => {
    try {
      const response = await api.get(`/payments/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Registrar un nuevo pago
   * @param {Object} paymentData - Datos del pago
   * @returns {Promise} - Promesa con la respuesta
   */
  create: async (paymentData) => {
    try {
      const response = await api.post('/payments', paymentData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Actualizar un pago
   * @param {number} id - ID del pago
   * @param {Object} paymentData - Datos del pago
   * @returns {Promise} - Promesa con la respuesta
   */
  update: async (id, paymentData) => {
    try {
      const response = await api.put(`/payments/${id}`, paymentData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Marcar un pago como exitoso
   * @param {number} id - ID del pago
   * @returns {Promise} - Promesa con la respuesta
   */
  markAsSuccessful: async (id) => {
    try {
      const response = await api.post(`/payments/${id}/succeed`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Marcar un pago como fallido
   * @param {number} id - ID del pago
   * @param {Object} failureData - Datos del fallo
   * @returns {Promise} - Promesa con la respuesta
   */
  markAsFailed: async (id, failureData) => {
    try {
      const response = await api.post(`/payments/${id}/fail`, failureData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Generar archivo ACH para pagos pendientes
   * @param {string} date - Fecha para los pagos (YYYY-MM-DD)
   * @returns {Promise} - Promesa con la respuesta
   */
  generateAchFile: async (date) => {
    try {
      const response = await api.post('/payments/generate-ach-file', { date });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Procesar archivo de respuesta ACH
   * @param {File} file - Archivo de respuesta
   * @returns {Promise} - Promesa con la respuesta
   */
  processAchResponseFile: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/payments/process-ach-response', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default PaymentService; 