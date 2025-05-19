import React from 'react';
import { useField } from 'formik';

/**
 * Componente de checkbox para formularios con Formik
 */
const FormCheckbox = ({ label, helpText, ...props }) => {
  const [field, meta] = useField({ ...props, type: 'checkbox' });
  const hasError = meta.touched && meta.error;

  return (
    <div className="mb-4">
      <div className="flex items-start">
        <div className="flex items-center h-5">
          <input
            type="checkbox"
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            {...field}
            {...props}
          />
        </div>
        {label && (
          <div className="ml-3 text-sm">
            <label htmlFor={props.id || props.name} className="font-medium text-gray-700">
              {label}
            </label>
            {helpText && !hasError && (
              <p className="text-gray-500">{helpText}</p>
            )}
          </div>
        )}
      </div>
      {hasError && (
        <div className="form-error mt-1">{meta.error}</div>
      )}
    </div>
  );
};

export default FormCheckbox; 