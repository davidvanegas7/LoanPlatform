import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Layout from '../layout/Layout';

/**
 * Componente para rutas privadas que requieren autenticación
 */
const PrivateRoute = () => {
  const { isAuthenticated, loading } = useAuth();

  // Si aún se está cargando, mostrar un indicador
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // Si no está autenticado, redirigir al login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Renderizar el children dentro del layout principal
  return (
    <Layout>
      <Outlet />
    </Layout>
  );
};

export default PrivateRoute; 