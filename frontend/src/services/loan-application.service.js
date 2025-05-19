import api from './api';

/**
 * Servicio para manejar las solicitudes de préstamos
 */
const LoanApplicationService = {
  /**
   * Obtener todas las solicitudes
   * @param {Object} params - Parámetros de filtrado y paginación
   * @returns {Promise} - Promesa con la respuesta
   */
  getAll: async (params = {}) => {
    try {
      const response = await api.get('/loan-applications', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Obtener una solicitud por ID
   * @param {number} id - ID de la solicitud
   * @returns {Promise} - Promesa con la respuesta
   */
  getById: async (id) => {
    try {
      const response = await api.get(`/loan-applications/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Crear una nueva solicitud de préstamo (Paso 1)
   * @param {Object} data - Datos iniciales de la solicitud (business_name, loan_purpose, tax_id)
   * @returns {Promise} - Promesa con la respuesta
   */
  create: async (data) => {
    try {
      const response = await api.post('/loan-applications', data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Actualizar una solicitud de préstamo
   * @param {number} id - ID de la solicitud
   * @param {Object} data - Datos a actualizar
   * @returns {Promise} - Promesa con la respuesta
   */
  update: async (id, data) => {
    try {
      const response = await api.put(`/loan-applications/${id}`, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Cancelar una solicitud de préstamo
   * @param {number} id - ID de la solicitud
   * @returns {Promise} - Promesa con la respuesta
   */
  cancel: async (id) => {
    try {
      const response = await api.post(`/loan-applications/${id}/cancel`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Enviar una solicitud para su aprobación
   * @param {number} id - ID de la solicitud
   * @returns {Promise} - Promesa con la respuesta
   */
  submit: async (id) => {
    try {
      const response = await api.post(`/loan-applications/${id}/submit`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Aprobar una solicitud de préstamo
   * @param {number} id - ID de la solicitud
   * @param {Object} approvalData - Datos de aprobación
   * @returns {Promise} - Promesa con la respuesta
   */
  approve: async (id, approvalData) => {
    try {
      const response = await api.post(`/loan-applications/${id}/approve`, approvalData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  /**
   * Rechazar una solicitud de préstamo
   * @param {number} id - ID de la solicitud
   * @param {Object} rejectionData - Datos de rechazo
   * @returns {Promise} - Promesa con la respuesta
   */
  reject: async (id, rejectionData) => {
    try {
      const response = await api.post(`/loan-applications/${id}/reject`, rejectionData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Guardar información del negocio (Paso 2)
   * @param {number} id - ID de la solicitud
   * @param {Object} data - Datos de la empresa (business_type, industry, business_years)
   * @returns {Promise} - Promesa con la respuesta
   */
  saveBusinessInfo: async (id, data) => {
    try {
      const response = await api.post(`/loan-applications/${id}/steps/business-info`, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Guardar información financiera (Paso 3)
   * @param {number} id - ID de la solicitud
   * @param {Object} data - Datos financieros (annual_revenue, business_bank_account, monthly_profit)
   * @returns {Promise} - Promesa con la respuesta
   */
  saveFinancialInfo: async (id, data) => {
    try {
      const response = await api.post(`/loan-applications/${id}/steps/financial-info`, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Guardar detalles del préstamo (Paso 4)
   * @param {number} id - ID de la solicitud
   * @param {Object} data - Datos del préstamo (loan_amount, loan_purpose, loan_term)
   * @returns {Promise} - Promesa con la respuesta
   */
  saveLoanDetails: async (id, data) => {
    try {
      const response = await api.post(`/loan-applications/${id}/steps/loan-details`, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Financiar un préstamo para una solicitud aprobada
   * @param {number} applicationId - ID de la solicitud
   * @returns {Promise} - Promesa con la respuesta
   */
  fund: async (applicationId) => {
    try {
      const response = await api.post(`/loans/application/${applicationId}/fund`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default LoanApplicationService; 