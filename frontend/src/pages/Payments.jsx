import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiArrowLeft, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import Card from '../components/common/Card';
import Alert from '../components/common/Alert';
import PaymentService from '../services/payment.service';

const Payments = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [payments, setPayments] = useState([]);
  const [paymentsPage, setPaymentsPage] = useState(1);
  const [paymentsPerPage] = useState(100);
  const [paginatedPayments, setPaginatedPayments] = useState([]);

  useEffect(() => {
    const fetchPayments = async () => {
      try {
        setLoading(true);
        setError('');
        
        const response = await PaymentService.getAll({
          sort: 'created_at:desc'
        });
        setPayments(response.payments || []);
        setLoading(false);
        
      } catch (err) {
        setError('Error al cargar los pagos');
        console.error('Error fetching payments:', err);
        setLoading(false);
      }
    };

    fetchPayments();
  }, []);

  // Efecto para manejar cambios en la página de pagos
  useEffect(() => {
    const startIndex = (paymentsPage - 1) * paymentsPerPage;
    const endIndex = startIndex + paymentsPerPage;
    setPaginatedPayments(payments.slice(startIndex, endIndex));
  }, [paymentsPage, payments, paymentsPerPage]);

  // Función para cambiar de página
  const handlePageChange = (newPage) => {
    setPaymentsPage(newPage);
  };

  // Formatear fecha
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Formatear monto
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  // Estado del pago
  const getPaymentStatusBadge = (status) => {
    const statusConfig = {
      'paid': 'bg-green-100 text-green-800',
      'pending': 'bg-yellow-100 text-yellow-800',
      'late': 'bg-red-100 text-red-800',
    };

    const statusLabels = {
      'paid': 'Pagado',
      'pending': 'Pendiente',
      'late': 'Atrasado',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs ${statusConfig[status] || 'bg-gray-100 text-gray-800'}`}>
        {statusLabels[status] || status}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center">
        <Link to="/dashboard" className="mr-4">
          <FiArrowLeft className="h-5 w-5 text-gray-500" />
        </Link>
        <h1 className="text-2xl font-semibold text-gray-900">Pagos</h1>
      </div>

      {error && (
        <Alert 
          type="error"
          message={error}
          className="my-4"
        />
      )}

      <Card>
        {payments.length === 0 ? (
          <div className="text-center py-4">
            <p className="text-gray-500">No hay pagos para mostrar.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    #
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Préstamo
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monto
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fecha de vencimiento
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fecha de pago
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {paginatedPayments.map((payment) => (
                  <tr key={payment.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {payment.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      #{payment.loan_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(payment.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(payment.due_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getPaymentStatusBadge(payment.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {payment.payment_date ? formatDate(payment.payment_date) : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {/* Paginación */}
            {payments.length > paymentsPerPage && (
              <div className="px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
                <div className="flex-1 flex justify-between">
                  <button
                    onClick={() => handlePageChange(paymentsPage - 1)}
                    disabled={paymentsPage === 1}
                    className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white ${paymentsPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'}`}
                  >
                    <FiChevronLeft className="mr-2 h-5 w-5" />
                    Anterior
                  </button>
                  <span className="text-sm text-gray-700">
                    Página {paymentsPage} de {Math.ceil(payments.length / paymentsPerPage)}
                  </span>
                  <button
                    onClick={() => handlePageChange(paymentsPage + 1)}
                    disabled={paymentsPage >= Math.ceil(payments.length / paymentsPerPage)}
                    className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white ${paymentsPage >= Math.ceil(payments.length / paymentsPerPage) ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'}`}
                  >
                    Siguiente
                    <FiChevronRight className="ml-2 h-5 w-5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
};

export default Payments; 