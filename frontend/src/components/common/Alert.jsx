import React from 'react';
import { IoMdCheckmarkCircle, IoMdInformationCircle, IoMdWarning, IoMdClose } from 'react-icons/io';

/**
 * Componente de alerta reutilizable con diferentes variantes
 * @param {string} type - success, info, warning, error
 * @param {string} title - título de la alerta
 * @param {ReactNode} message - mensaje de la alerta
 * @param {boolean} closable - si la alerta puede ser cerrada
 */
const Alert = ({
  type = 'info',
  title,
  message,
  closable = false,
  onClose,
  className = '',
  ...rest
}) => {
  // Configuración según el tipo
  const alertConfig = {
    success: {
      icon: <IoMdCheckmarkCircle size={24} />,
      bgColor: 'bg-green-50',
      textColor: 'text-green-800',
      borderColor: 'border-green-200',
      iconColor: 'text-green-500',
    },
    info: {
      icon: <IoMdInformationCircle size={24} />,
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-800',
      borderColor: 'border-blue-200',
      iconColor: 'text-blue-500',
    },
    warning: {
      icon: <IoMdWarning size={24} />,
      bgColor: 'bg-yellow-50',
      textColor: 'text-yellow-800',
      borderColor: 'border-yellow-200',
      iconColor: 'text-yellow-500',
    },
    error: {
      icon: <IoMdWarning size={24} />,
      bgColor: 'bg-red-50',
      textColor: 'text-red-800',
      borderColor: 'border-red-200',
      iconColor: 'text-red-500',
    },
  };

  const config = alertConfig[type] || alertConfig.info;

  return (
    <div
      className={`px-4 py-3 rounded-md border ${config.bgColor} ${config.textColor} ${config.borderColor} ${className}`}
      role="alert"
      {...rest}
    >
      <div className="flex">
        <div className={`flex-shrink-0 ${config.iconColor}`}>
          {config.icon}
        </div>
        <div className="ml-3 w-full">
          {title && <h3 className="text-sm font-medium">{title}</h3>}
          {message && <div className="text-sm mt-1">{message}</div>}
        </div>
        {closable && (
          <button
            type="button"
            className={`ml-auto -mx-1.5 -my-1.5 ${config.bgColor} ${config.textColor} rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-${type}-50 focus:ring-${type}-500 p-1.5`}
            onClick={onClose}
          >
            <span className="sr-only">Cerrar</span>
            <IoMdClose className="h-5 w-5" />
          </button>
        )}
      </div>
    </div>
  );
};

export default Alert; 