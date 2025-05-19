import React from 'react';

/**
 * Componente de tarjeta reutilizable
 * @param {string} title - Título de la tarjeta
 * @param {ReactNode} children - Contenido de la tarjeta
 */
const Card = ({ 
  title, 
  children, 
  className = '', 
  titleClassName = '',
  bodyClassName = '',
  ...rest 
}) => {
  return (
    <div className={`card ${className}`} {...rest}>
      {title && (
        <div className={`mb-4 pb-2 border-b border-gray-200 ${titleClassName}`}>
          <h3 className="text-xl font-semibold">{title}</h3>
        </div>
      )}
      <div className={bodyClassName}>
        {children}
      </div>
    </div>
  );
};

export default Card; 