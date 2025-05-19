import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { FiArrowLeft, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import Card from '../components/common/Card';
import Alert from '../components/common/Alert';
import LoanService from '../services/loan.service';

const LoanDetails = () => {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [loan, setLoan] = useState(null);
  const [payments, setPayments] = useState([]);
  const [paymentsPage, setPaymentsPage] = useState(1);
  const [paymentsPerPage] = useState(10);
  const [paginatedPayments, setPaginatedPayments] = useState([]);

  useEffect(() => {
    const fetchLoanDetails = async () => {
      try {
        setLoading(true);
        setError('');
        
        const response = await LoanService.getById(id);
        setLoan(response.loan || null);        

        const responsePayments = await LoanService.getPayments(id);
        setPayments(responsePayments.payments || []);
        
      } catch (err) {
        setError('Error al cargar los detalles del préstamo');
        console.error('Error fetching loan details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchLoanDetails();
  }, [id]);

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

  // Estado del préstamo
  const getLoanStatusBadge = (status) => {
    const statusConfig = {
      'active': 'bg-green-100 text-green-800',
      'closed': 'bg-gray-100 text-gray-800',
      'defaulted': 'bg-red-100 text-red-800',
    };

    const statusLabels = {
      'active': 'Activo',
      'closed': 'Cerrado',
      'defaulted': 'Vencido',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs ${statusConfig[status] || 'bg-gray-100 text-gray-800'}`}>
        {statusLabels[status] || status}
      </span>
    );
  };

  // Estado del pago
  const getPaymentStatusBadge = (status) => {
    const statusConfig = {
      'paid': 'bg-green-100 text-green-800',
      'scheduled': 'bg-yellow-100 text-yellow-800',
      'failed': 'bg-red-100 text-red-800',
      'processing': 'bg-blue-100 text-blue-800',
    };
  
    const statusLabels = {
      'paid': 'Pagado',
      'scheduled': 'Programado',
      'failed': 'Fallado',
      'processing': 'Procesando',
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

  if (!loan) {
    return (
      <div className="space-y-6">
        <div className="flex items-center">
          <Link to="/loans" className="mr-4">
            <FiArrowLeft className="h-5 w-5 text-gray-500" />
          </Link>
          <h1 className="text-2xl font-semibold text-gray-900">Préstamo no encontrado</h1>
        </div>
        <Alert type="error" message="No se pudo encontrar el préstamo solicitado" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center">
        <Link to="/loans" className="mr-4">
          <FiArrowLeft className="h-5 w-5 text-gray-500" />
        </Link>
        <h1 className="text-2xl font-semibold text-gray-900">
          Préstamo #{loan.id}
        </h1>
      </div>

      {error && (
        <Alert 
          type="error"
          message={error}
          className="my-4"
        />
      )}

      <Card title="Detalles del préstamo">
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Estado</h3>
              <div className="mt-1">
                {getLoanStatusBadge(loan.status)}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Fecha de inicio</h3>
              <p className="mt-1 text-sm text-gray-900">{formatDate(loan.start_date)}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Monto del préstamo</h3>
              <p className="mt-1 text-sm text-gray-900">{formatCurrency(loan.amount)}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Saldo restante</h3>
              <p className="mt-1 text-sm text-gray-900">{formatCurrency(loan.remaining_balance)}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Tasa de interés</h3>
              <p className="mt-1 text-sm text-gray-900">{loan.interest_rate * 100}%</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Plazo (días)</h3>
              <p className="mt-1 text-sm text-gray-900">{loan.term_days}</p>
            </div>
          </div>

          {loan.end_date && (
            <div>
              <h3 className="text-sm font-medium text-gray-500">Fecha de finalización</h3>
              <p className="mt-1 text-sm text-gray-900">{formatDate(loan.end_date)}</p>
            </div>
          )}
        </div>
      </Card>

      <Card title="Pagos">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  #
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
      </Card>
    </div>
  );
};

export default LoanDetails; 