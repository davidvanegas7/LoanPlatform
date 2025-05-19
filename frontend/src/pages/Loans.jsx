import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { FiArrowLeft, FiArrowRight } from 'react-icons/fi';
import Card from '../components/common/Card';
import Alert from '../components/common/Alert';
import LoanService from '../services/loan.service';

const Loans = () => {
  const [searchParams] = useSearchParams();
  const statusFilter = searchParams.get('status');
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [loans, setLoans] = useState([]);

  useEffect(() => {
    const fetchLoans = async () => {
      try {
        setLoading(true);
        setError('');
        
        const params = {};
        if (statusFilter) {
          params.status = statusFilter;
        }
        
        const response = await LoanService.getAll(params);
        setLoans(response.loans || []);
      } catch (err) {
        setError('Error al cargar los préstamos');
        console.error('Error fetching loans:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchLoans();
  }, [statusFilter]);

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

  let title = 'Préstamos';
  if (statusFilter) {
    const statusLabels = {
      'active': 'Activos',
      'closed': 'Cerrados',
      'defaulted': 'Vencidos',
    };
    title = `Préstamos ${statusLabels[statusFilter] || statusFilter}`;
  }

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
        <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
      </div>

      {error && (
        <Alert 
          type="error"
          message={error}
          className="my-4"
        />
      )}

      <Card>
        {loans.length === 0 ? (
          <div className="text-center py-4">
            <p className="text-gray-500">No hay préstamos para mostrar.</p>
            <Link to="/loan-applications/new" className="mt-2 inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-500">
              Solicitar un préstamo <FiArrowRight className="ml-1 h-4 w-4" />
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monto
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Saldo Restante
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fecha de Inicio
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loans.map((loan) => (
                  <tr key={loan.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      #{loan.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(loan.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(loan.remaining_balance)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(loan.start_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getLoanStatusBadge(loan.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <Link to={`/loans/${loan.id}`} className="text-blue-600 hover:text-blue-900">
                        Ver detalles
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};

export default Loans; 