import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  FiHome, 
  FiFileText, 
  FiDollarSign, 
  FiCreditCard, 
  FiUser, 
  FiSettings,
} from 'react-icons/fi';

/**
 * Componente de barra lateral
 */
const Sidebar = () => {
  const location = useLocation();

  // Opciones del menú
  const menuItems = [
    { name: 'Dashboard', path: '/dashboard', icon: <FiHome size={20} /> },
    { name: 'Solicitudes', path: '/loan-applications', icon: <FiFileText size={20} /> },
    { name: 'Préstamos', path: '/loans', icon: <FiDollarSign size={20} /> },
    { name: 'Pagos', path: '/payments', icon: <FiCreditCard size={20} /> },
  ];

  // Verificar si una ruta está activa
  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <div className="flex flex-shrink-0">
      <div className="flex flex-col w-64">
        <div className="flex flex-col flex-grow border-r border-gray-200 pt-2 pb-4 bg-white overflow-y-auto h-screen">

          <div className="mt-5 flex-grow flex flex-col">
            <nav className="flex-1 px-2 space-y-1">
              {menuItems.map((item) => (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive(item.path)
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <div
                    className={`mr-3 ${
                      isActive(item.path) ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                  >
                    {item.icon}
                  </div>
                  {item.name}
                </Link>
              ))}
            </nav>
            
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar; 