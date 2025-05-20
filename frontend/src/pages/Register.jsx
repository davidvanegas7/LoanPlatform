import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import FormInput from '../components/forms/FormInput';
import FormCheckbox from '../components/forms/FormCheckbox';
import Button from '../components/common/Button';
import Alert from '../components/common/Alert';
import TermsAndConditions from '../components/legal/TermsAndConditions';
import PrivacyPolicy from '../components/legal/PrivacyPolicy';
import { useAuth } from '../contexts/AuthContext';

/**
 * Página de registro de usuarios
 */
const Register = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isTermsOpen, setIsTermsOpen] = useState(false);
  const [isPrivacyOpen, setIsPrivacyOpen] = useState(false);

  // Esquema de validación con Yup
  const validationSchema = Yup.object({
    first_name: Yup.string()
      .required('El nombre es obligatorio')
      .min(2, 'El nombre debe tener al menos 2 caracteres'),
    last_name: Yup.string()
      .required('El apellido es obligatorio')
      .min(2, 'El apellido debe tener al menos 2 caracteres'),
    email: Yup.string()
      .email('Correo electrónico inválido')
      .required('El correo electrónico es obligatorio'),
    password: Yup.string()
      .required('La contraseña es obligatoria')
      .min(6, 'La contraseña debe tener al menos 6 caracteres'),
    password_confirmation: Yup.string()
      .oneOf([Yup.ref('password'), null], 'Las contraseñas deben coincidir')
      .required('Debes confirmar la contraseña'),
    business_name: Yup.string()
      .required('El nombre del negocio es obligatorio'),
    terms_accepted: Yup.boolean()
      .oneOf([true], 'Debes aceptar los términos y condiciones y la política de privacidad'),
  });

  // Valores iniciales del formulario
  const initialValues = {
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    password_confirmation: '',
    business_name: '',
    phone: '',
    terms_accepted: false,
  };

  // Manejar envío del formulario
  const handleSubmit = async (values, { setSubmitting, resetForm }) => {
    try {
      setError('');
      setSuccess('');
      
      // Crear objeto de datos para enviar
      const userData = {
        first_name: values.first_name,
        last_name: values.last_name,
        email: values.email,
        password: values.password,
        password_confirmation: values.password_confirmation,
      };
      
      await register(userData);
      
      // Mostrar mensaje de éxito
      setSuccess('¡Registro exitoso! Redirigiendo a la página de inicio de sesión...');
      resetForm();
      
      // Redirigir al login después de 2 segundos
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.message || 'Error al registrarse. Inténtalo de nuevo más tarde.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Crea tu cuenta
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            O{' '}
            <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
              inicia sesión si ya tienes una cuenta
            </Link>
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            {error && (
              <Alert 
                type="error"
                message={error}
                className="mb-4"
              />
            )}
            
            {success && (
              <Alert 
                type="success"
                message={success}
                className="mb-4"
              />
            )}

            <Formik
              initialValues={initialValues}
              validationSchema={validationSchema}
              onSubmit={handleSubmit}
            >
              {({ isSubmitting }) => (
                <Form className="space-y-6">
                  <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
                    <FormInput
                      label="Nombre"
                      name="first_name"
                      type="text"
                      autoComplete="given-name"
                      placeholder="Tu nombre"
                    />

                    <FormInput
                      label="Apellido"
                      name="last_name"
                      type="text"
                      autoComplete="family-name"
                      placeholder="Tu apellido"
                    />
                  </div>

                  <FormInput
                    label="Correo electrónico"
                    name="email"
                    type="email"
                    autoComplete="email"
                    placeholder="tucorreo@ejemplo.com"
                  />

                  <FormInput
                    label="Contraseña"
                    name="password"
                    type="password"
                    autoComplete="new-password"
                    placeholder="********"
                  />

                  <FormInput
                    label="Confirmar contraseña"
                    name="password_confirmation"
                    type="password"
                    autoComplete="new-password"
                    placeholder="********"
                  />

                  <FormCheckbox
                    name="terms_accepted"
                    label={
                      <span>
                        Acepto los{' '}
                        <button
                          type="button"
                          onClick={() => setIsTermsOpen(true)}
                          className="font-medium text-blue-600 hover:text-blue-500"
                        >
                          términos y condiciones
                        </button>
                        {' '}y la{' '}
                        <button
                          type="button"
                          onClick={() => setIsPrivacyOpen(true)}
                          className="font-medium text-blue-600 hover:text-blue-500"
                        >
                          política de privacidad
                        </button>
                      </span>
                    }
                  />

                  <div>
                    <Button
                      type="submit"
                      variant="primary"
                      fullWidth
                      isLoading={isSubmitting}
                    >
                      Registrarse
                    </Button>
                  </div>
                </Form>
              )}
            </Formik>
          </div>
        </div>
      </div>

      <TermsAndConditions
        isOpen={isTermsOpen}
        onClose={() => setIsTermsOpen(false)}
      />

      <PrivacyPolicy
        isOpen={isPrivacyOpen}
        onClose={() => setIsPrivacyOpen(false)}
      />
    </>
  );
};

export default Register; 