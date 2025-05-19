import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { FiArrowLeft } from 'react-icons/fi';
import Card from '../components/common/Card';
import Alert from '../components/common/Alert';
import LoanApplicationService from '../services/loan-application.service';

const LoanApplicationDetails = () => {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [application, setApplication] = useState(null);

  useEffect(() => {
    const fetchApplicationDetails = async () => {
      try {
        setLoading(true);
        setError('');
        
        const response = await LoanApplicationService.getById(id);
        setApplication(response.application || null);
      } catch (err) {
        setError('Error al cargar los detalles de la solicitud');
        console.error('Error fetching loan application details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchApplicationDetails();
  }, [id]);

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
      'undecided': 'Indeciso',
      'under_review': 'En revisión',
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

  if (!application) {
    return (
      <div className="space-y-6">
        <div className="flex items-center">
          <Link to="/loan-applications" className="mr-4">
            <FiArrowLeft className="h-5 w-5 text-gray-500" />
          </Link>
          <h1 className="text-2xl font-semibold text-gray-900">Solicitud no encontrada</h1>
        </div>
        <Alert type="error" message="No se pudo encontrar la solicitud de préstamo" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center">
        <Link to="/loan-applications" className="mr-4">
          <FiArrowLeft className="h-5 w-5 text-gray-500" />
        </Link>
        <h1 className="text-2xl font-semibold text-gray-900">
          Solicitud #{application.id}
        </h1>
      </div>

      {error && (
        <Alert 
          type="error"
          message={error}
          className="my-4"
        />
      )}

      <Card title="Detalles de la solicitud">
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Empresa</h3>
              <div className="mt-1">
                {application.business_name}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Tax Id</h3>
              <p className="mt-1 text-sm text-gray-900">{application.tax_id}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Estado</h3>
              <div className="mt-1">
                {getLoanApplicationStatusBadge(application.status)}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Fecha de solicitud</h3>
              <p className="mt-1 text-sm text-gray-900">{formatDate(application.created_at)}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Monto solicitado</h3>
              <p className="mt-1 text-sm text-gray-900">{formatCurrency(application.loan_amount)}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Plazo (meses)</h3>
              <p className="mt-1 text-sm text-gray-900">{application.loan_term}</p>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-gray-500">Propósito del préstamo</h3>
            <p className="mt-1 text-sm text-gray-900">{application.loan_purpose || 'No especificado'}</p>
          </div>

          {application.comments && (
            <div>
              <h3 className="text-sm font-medium text-gray-500">Comentarios</h3>
              <p className="mt-1 text-sm text-gray-900">{application.comments}</p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default LoanApplicationDetails; 