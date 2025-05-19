import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiPlusCircle, FiCreditCard, FiFileText, FiDollarSign, FiArrowRight, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Alert from '../components/common/Alert';
import LoanApplicationService from '../services/loan-application.service';
import LoanService from '../services/loan.service';
import PaymentService from '../services/payment.service';
// import { useAuth } from '../contexts/AuthContext';

/**
 * Página de Panel de Control (Dashboard)
 */
const Dashboard = () => {
  // const { currentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [loanApplications, setLoanApplications] = useState([]);
  const [activeLoans, setActiveLoans] = useState([]);
  const [upcomingPayments, setUpcomingPayments] = useState([]);
  const [allUpcomingPayments, setAllUpcomingPayments] = useState([]);
  const [paymentsPage, setPaymentsPage] = useState(1);
  const [paymentsPerPage] = useState(10);
  const [summary, setSummary] = useState({
    totalActive: 0,
    totalApplications: 0,
    totalApproved: 0,
    totalRejected: 0,
  });

  // Cargar datos al montar el componente
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError('');

        // Cargar solicitudes de préstamos
        const loanAppsResponse = await LoanApplicationService.getAll({ 
          limit: 10, 
          sort: 'created_at:desc' 
        });

        setLoanApplications(loanAppsResponse.applications || []);

        // Cargar préstamos activos
        const loansResponse = await LoanService.getAll({ 
          status: 'active', 
          limit: 10, 
          sort: 'created_at:desc' 
        });

        setActiveLoans(loansResponse.loans || []);

        const paymentsResponse = await PaymentService.getAll({
          status: 'scheduled',
          sort: 'created_at:desc'
        });

        setAllUpcomingPayments(paymentsResponse.payments || []);
        setUpcomingPayments(paymentsResponse.payments?.slice(0, paymentsPerPage) || []);

        // Obtener resumen (esto sería un endpoint específico en tu API)
        setSummary({
          totalActive: loansResponse.loans.length || 0,
          totalApplications: loanAppsResponse.applications.length || 0,
          totalApproved: loanAppsResponse.applications.filter(app => app.status === 'approved').length || 0,
          totalRejected: loanAppsResponse.total || 0,
        });

      } catch (err) {
        setError('Error al cargar los datos del dashboard');
        // window.location.reload();
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [paymentsPerPage]);

  // Efecto para manejar cambios en la página de pagos
  useEffect(() => {
    const startIndex = (paymentsPage - 1) * paymentsPerPage;
    const endIndex = startIndex + paymentsPerPage;
    setUpcomingPayments(allUpcomingPayments.slice(startIndex, endIndex));
  }, [paymentsPage, allUpcomingPayments, paymentsPerPage]);

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

  // Estado de la aplicación de préstamo
  const getLoanApplicationStatusBadge = (status) => {
    const statusConfig = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'approved': 'bg-green-100 text-green-800',
      'rejected': 'bg-red-100 text-red-800',
      'declined': 'bg-red-100 text-red-800',
      'draft': 'bg-gray-100 text-gray-800',
      'undecided': 'bg-gray-100 text-gray-800',
      'under_review': 'bg-blue-100 text-blue-800',
    };

    const statusLabels = {
      'pending': 'Pendiente',
      'approved': 'Aprobada',
      'rejected': 'Rechazada',
      'declined': 'Declinada',
      'draft': 'Borrador',
      'under_review': 'En revisión',
      'undecided': 'Indeciso',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs ${statusConfig[status] || 'bg-gray-100 text-gray-800'}`}>
        {statusLabels[status] || status}
      </span>
    );
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

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <div className="mt-3 sm:mt-0">
          <Button 
            variant="primary"
            as={Link}
            to="/loan-applications/new"
          >
            <FiPlusCircle className="mr-2 h-5 w-5" />
            Solicitar préstamo
          </Button>
        </div>
      </div>

      {error && (
        <Alert 
          type="error"
          message={error}
          className="my-4"
        />
      )}
      
      {/* Tarjetas de estadísticas */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                <FiDollarSign className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Préstamos Activos
                  </dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {summary.totalActive}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-4 py-4 sm:px-6">
            <div className="text-sm">
              <Link to="/loans?status=active" className="font-medium text-blue-600 hover:text-blue-500">
                Ver todos <span className="sr-only">Préstamos Activos</span>
                <FiArrowRight className="ml-1 inline h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                <FiCreditCard className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Pagos Próximos
                  </dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {allUpcomingPayments.length}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-4 py-4 sm:px-6">
            <div className="text-sm">
              <Link to="/payments" className="font-medium text-blue-600 hover:text-blue-500">
                Ver todos <span className="sr-only">Pagos Próximos</span>
                <FiArrowRight className="ml-1 inline h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                <FiFileText className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Solicitudes Aprobadas
                  </dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {summary.totalApproved}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-4 py-4 sm:px-6">
            <div className="text-sm">
              <Link to="/loan-applications?status=approved" className="font-medium text-blue-600 hover:text-blue-500">
                Ver todas <span className="sr-only">Solicitudes Aprobadas</span>
                <FiArrowRight className="ml-1 inline h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      {/* Solicitudes recientes */}
      <Card title="Solicitudes de préstamos recientes">
        {loanApplications.length === 0 ? (
          <div className="text-center py-4">
            <p className="text-gray-500">No tienes solicitudes de préstamos.</p>
            <Link 
              to="/loan-applications/new" 
              className="mt-2 inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-500"
            >
              Solicitar un préstamo
              <FiArrowRight className="ml-1 h-4 w-4" />
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
                    Empresa
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monto Solicitado
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fecha
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
                {loanApplications.map((application) => (
                  <tr key={application.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      #{application.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {application.business_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(application.loan_amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(application.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getLoanApplicationStatusBadge(application.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <Link to={`/loan-applications/${application.id}`} className="text-blue-600 hover:text-blue-900">
                        Ver detalles
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="mt-4 text-right">
          <Link to="/loan-applications" className="text-sm font-medium text-blue-600 hover:text-blue-500">
            Ver todas las solicitudes <FiArrowRight className="ml-1 inline h-4 w-4" />
          </Link>
        </div>
      </Card>
      
      {/* Préstamos activos */}
      <Card title="Préstamos activos">
        {activeLoans.length === 0 ? (
          <div className="text-center py-4">
            <p className="text-gray-500">No tienes préstamos activos.</p>
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
                    Empresa
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
                {activeLoans.map((loan) => (
                  <tr key={loan.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      #{loan.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {loan.business_name}
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
        <div className="mt-4 text-right">
          <Link to="/loans" className="text-sm font-medium text-blue-600 hover:text-blue-500">
            Ver todos los préstamos <FiArrowRight className="ml-1 inline h-4 w-4" />
          </Link>
        </div>
      </Card>
      
      {/* Pagos próximos */}
      <Card title="Pagos próximos">
        {allUpcomingPayments.length === 0 ? (
          <div className="text-center py-4">
            <p className="text-gray-500">No tienes pagos próximos.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID de Préstamo
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monto
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fecha de Vencimiento
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
                {upcomingPayments.map((payment) => (
                  <tr key={payment.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <Link to={`/loans/${payment.loan_id}`} className="text-blue-600 hover:text-blue-900">
                        Ver préstamo
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {/* Paginación */}
            {allUpcomingPayments.length > paymentsPerPage && (
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
                    Página {paymentsPage} de {Math.ceil(allUpcomingPayments.length / paymentsPerPage)}
                  </span>
                  <button
                    onClick={() => handlePageChange(paymentsPage + 1)}
                    disabled={paymentsPage >= Math.ceil(allUpcomingPayments.length / paymentsPerPage)}
                    className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white ${paymentsPage >= Math.ceil(allUpcomingPayments.length / paymentsPerPage) ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'}`}
                  >
                    Siguiente
                    <FiChevronRight className="ml-2 h-5 w-5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
        <div className="mt-4 text-right">
          <Link to="/payments" className="text-sm font-medium text-blue-600 hover:text-blue-500">
            Ver todos los pagos <FiArrowRight className="ml-1 inline h-4 w-4" />
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default Dashboard; 