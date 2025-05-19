import React from 'react';
import { useField } from 'formik';

/**
 * Componente de área de texto para formularios con Formik
 */
const FormTextarea = ({ label, helpText, ...props }) => {
  const [field, meta] = useField(props);
  const hasError = meta.touched && meta.error;

  return (
    <div className="mb-4">
      {label && (
        <label htmlFor={props.id || props.name} className="form-label">
          {label}
        </label>
      )}
      <textarea
        className={`form-input min-h-[100px] ${hasError ? 'border-red-500 focus:ring-red-500' : ''}`}
        {...field}
        {...props}
      />
      {helpText && !hasError && (
        <p className="mt-1 text-sm text-gray-500">{helpText}</p>
      )}
      {hasError && (
        <div className="form-error">{meta.error}</div>
      )}
    </div>
  );
};

export default FormTextarea; 