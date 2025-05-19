import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

/**
 * Componente para rutas públicas que no requieren autenticación
 * Redirige al dashboard si el usuario ya está autenticado
 */
const PublicRoute = ({ restricted = false }) => {
  const { isAuthenticated, loading } = useAuth();

  // Si aún se está cargando, mostrar un indicador
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // Si está autenticado y la ruta es restringida (como login), redirigir al dashboard
  if (isAuthenticated && restricted) {
    return <Navigate to="/dashboard" replace />;
  }

  // Renderizar el children
  return <Outlet />;
};

export default PublicRoute; 