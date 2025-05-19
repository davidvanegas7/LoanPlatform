import React from 'react';

/**
 * Componente de botón reutilizable con diferentes variantes
 * @param {string} variant - primary, secondary, danger, success
 * @param {string} size - sm, md, lg
 * @param {boolean} isLoading - muestra un indicador de carga
 * @param {boolean} fullWidth - botón de ancho completo
 * @param {Component} as - componente a renderizar (por defecto button)
 */
const Button = ({
  children,
  type = 'button',
  variant = 'primary',
  size = 'md',
  isLoading = false,
  fullWidth = false,
  disabled = false,
  onClick,
  className = '',
  as: Component = 'button',
  ...rest
}) => {
  // Clases base
  const baseClasses = 'inline-flex items-center justify-center';
  
  // Clases de variante
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500',
  };
  
  // Clases de tamaño
  const sizeClasses = {
    sm: 'text-sm py-1 px-3',
    md: 'text-sm py-2 px-4',
    lg: 'text-base py-3 px-6',
  };
  
  // Ancho completo
  const widthClass = fullWidth ? 'w-full' : '';
  
  // Deshabilitar
  const disabledClass = disabled || isLoading ? 'opacity-70 cursor-not-allowed' : '';
  
  // Combinación de clases
  const buttonClasses = [
    baseClasses,
    'rounded-md',
    'font-medium',
    'shadow-sm',
    'focus:outline-none focus:ring-2 focus:ring-offset-2',
    'transition-colors duration-200',
    variantClasses[variant] || variantClasses.primary,
    sizeClasses[size] || sizeClasses.md,
    widthClass,
    disabledClass,
    className,
  ].filter(Boolean).join(' ');
  
  const content = isLoading ? (
    <div className="flex items-center justify-center">
      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>Cargando...</span>
    </div>
  ) : (
    children
  );

  // Si Component es 'button', agregamos el tipo
  if (Component === 'button') {
    return (
      <Component
        type={type}
        className={buttonClasses}
        disabled={disabled || isLoading}
        onClick={onClick}
        {...rest}
      >
        {content}
      </Component>
    );
  }
  
  // Si es un componente personalizado, no pasamos el atributo 'type'
  return (
    <Component
      className={buttonClasses}
      onClick={disabled || isLoading ? undefined : onClick}
      aria-disabled={disabled || isLoading}
      tabIndex={disabled || isLoading ? -1 : undefined}
      {...rest}
    >
      {content}
    </Component>
  );
};

export default Button; 