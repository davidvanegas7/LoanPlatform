import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import FormInput from '../components/forms/FormInput';
import FormSelect from '../components/forms/FormSelect';
import FormTextarea from '../components/forms/FormTextarea';
import Button from '../components/common/Button';
import Alert from '../components/common/Alert';
import Card from '../components/common/Card';
import LoanApplicationService from '../services/loan-application.service';

/**
 * Página de solicitud de préstamo con pasos
 */
const LoanApplicationForm = () => {
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [currentStep, setCurrentStep] = useState(1);
  const [applicationId, setApplicationId] = useState(null);
  const [businessName, setBusinessName] = useState('');
  const [isApproved, setIsApproved] = useState(false);
  const [offerDetails, setOfferDetails] = useState(null);

  // Esquemas de validación para cada paso
  const validationSchemas = {
    // Paso 1 - Información inicial
    1: Yup.object({
      business_name: Yup.string()
        .required('El nombre del negocio es obligatorio')
        .max(100, 'El nombre no puede exceder los 100 caracteres'),
      tax_id: Yup.string()
        .required('El número de identificación fiscal es obligatorio')
        .matches(/^[0-9]{9}$/, 'El formato debe ser de 9 dígitos'),
    }),
    
    // Paso 2 - Información del negocio
    2: Yup.object({
      business_type: Yup.string()
        .required('El tipo de negocio es obligatorio'),
      industry: Yup.string()
        .required('La industria es obligatoria'),
      business_years: Yup.number()
        .required('Los años de operación del negocio son obligatorios')
        .positive('Los años deben ser positivos')
        .integer('Los años deben ser números enteros'),
    }),
    
    // Paso 3 - Información financiera
    3: Yup.object({
      annual_revenue: Yup.number()
        .required('Los ingresos anuales son obligatorios')
        .positive('Los ingresos deben ser positivos'),
      monthly_profit: Yup.number()
        .required('El beneficio mensual es obligatorio')
        .positive('El beneficio debe ser positivo'),
      bank_name: Yup.string()
        .required('El nombre del banco es obligatorio'),
      account_number: Yup.string()
        .required('El número de cuenta es obligatorio')
        .matches(/^[0-9]{4,17}$/, 'El número de cuenta debe tener entre 4 y 17 dígitos'),
    }),
    
    // Paso 4 - Detalles del préstamo
    4: Yup.object({
      loan_amount: Yup.number()
        .required('El monto del préstamo es obligatorio')
        .positive('El monto debe ser positivo')
        .max(50000, 'El monto máximo es $50,000'),
      loan_purpose: Yup.string()
        .required('El propósito del préstamo es obligatorio')
        .max(500, 'El propósito no puede exceder los 500 caracteres'),
      loan_term: Yup.number()
        .required('El plazo del préstamo es obligatorio')
        .positive('El plazo debe ser positivo')
        .integer('El plazo debe ser un número entero')
        .oneOf([6, 12, 24, 36, 48, 60], 'El plazo debe ser 6, 12, 24, 36, 48 o 60 meses'),
    }),
  };

  // Valores iniciales para cada paso
  const initialValues = {
    // Paso 1
    business_name: '',
    tax_id: '',
    loan_purpose: '',
    
    // Paso 2
    business_type: '',
    industry: '',
    business_years: '',
    
    // Paso 3
    annual_revenue: '',
    monthly_profit: '',
    bank_name: '',
    account_number: '',
    
    // Paso 4
    loan_amount: '',
    loan_term: '',
  };

  // Opciones para el campo de industria
  const industryOptions = [
    { value: '', label: 'Seleccionar industria' },
    { value: 'retail', label: 'Comercio minorista' },
    { value: 'hospitality', label: 'Hostelería' },
    { value: 'technology', label: 'Tecnología' },
    { value: 'healthcare', label: 'Salud' },
    { value: 'education', label: 'Educación' },
    { value: 'manufacturing', label: 'Manufactura' },
    { value: 'finance', label: 'Finanzas' },
    { value: 'construction', label: 'Construcción' },
    { value: 'agriculture', label: 'Agricultura' },
    { value: 'other', label: 'Otro' },
  ];

  // Opciones para el tipo de negocio
  const businessTypeOptions = [
    { value: '', label: 'Seleccionar tipo de negocio' },
    { value: 'llc', label: 'LLC (Sociedad de Responsabilidad Limitada)' },
    { value: 'corporation', label: 'Corporación' },
    { value: 'partnership', label: 'Sociedad' },
    { value: 'sole_proprietorship', label: 'Empresario Individual' },
    { value: 'other', label: 'Otro' },
  ];

  // Opciones para el plazo del préstamo
  const loanTermOptions = [
    { value: '', label: 'Seleccionar plazo' },
    { value: '1', label: '1 mes' },
    { value: '3', label: '3 meses' },
    { value: '6', label: '6 meses' },
    { value: '9', label: '9 meses' },
    { value: '12', label: '12 meses' },
    { value: '18', label: '18 meses' },
    { value: '24', label: '24 meses' },
  ];

  // Manejar envío del formulario para cada paso
  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      setError('');
      setSuccess('');
      // Procesar los datos según el paso actual
      switch (currentStep) {
        case 1:
          // Crear una nueva solicitud de préstamo
          const response = await LoanApplicationService.create({
            business_name: values.business_name,
            tax_id: values.tax_id,
          });
          
          setApplicationId(response.application.id);
          setBusinessName(values.business_name);
          setCurrentStep(2);
          setSuccess('Información inicial guardada. Continuando al siguiente paso...');
          break;
          
        case 2:
          // Guardar información del negocio
          await LoanApplicationService.saveBusinessInfo(applicationId, {
            business_name: businessName,
            business_type: values.business_type,
            industry: values.industry,
            business_years: parseInt(values.business_years),
          });
          
          setCurrentStep(3);
          setSuccess('Información del negocio guardada. Continuando al siguiente paso...');
          break;
          
        case 3:
          // Guardar información financiera
          await LoanApplicationService.saveFinancialInfo(applicationId, {
            annual_revenue: parseFloat(values.annual_revenue),
            monthly_profit: parseFloat(values.monthly_profit),
            business_bank_account: {
              bank_name: values.bank_name,
              account_number: values.account_number
            }
          });
          
          setCurrentStep(4);
          setSuccess('Información financiera guardada. Continuando al siguiente paso...');
          break;
          
        case 4:
          // Guardar detalles del préstamo
          await LoanApplicationService.saveLoanDetails(applicationId, {
            loan_amount: parseFloat(values.loan_amount),
            loan_purpose: values.loan_purpose,
            loan_term: parseInt(values.loan_term),
          });
          
          // Enviar la solicitud para aprobación
          const submitResponse = await LoanApplicationService.submit(applicationId);
          setOfferDetails(submitResponse.application);
          
          if (submitResponse.application.status === 'approved') {
            setIsApproved(true);
            setSuccess('¡Su solicitud ha sido aprobada! Revise los detalles y decida si desea aceptar la oferta.');
          } else {
            setSuccess('Solicitud enviada. Le notificaremos cuando tengamos una respuesta.');
          }
          
          setCurrentStep(5);
          break;
          
        default:
          break;
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Error al procesar su solicitud. Inténtelo de nuevo más tarde.');
    } finally {
      setSubmitting(false);
    }
  };

  // Manejar aceptación de la oferta de préstamo
  const handleAcceptOffer = async () => {
    try {
      setError('');
      setSuccess('');
      
      await LoanApplicationService.fund(applicationId, {
        interest_rate: offerDetails.loan_interest_rate * 100,
        term_days: offerDetails.loan_term * 30
      });
      
      setSuccess('¡Préstamo financiado con éxito! Redirigiendo...');
      setTimeout(() => {
        navigate('/loans');
      }, 4000);
    } catch (err) {
      setError(err.response?.data?.message || 'Error al financiar el préstamo. Inténtelo de nuevo más tarde.');
    }
  };

  // Manejar rechazo de la oferta de préstamo
  const handleRejectOffer = async () => {
    try {
      setError('');
      setSuccess('');
      
      await LoanApplicationService.cancel(applicationId);
      
      setSuccess('Oferta rechazada con éxito. Redirigiendo...');
      setTimeout(() => {
        navigate('/loan-applications');
      }, 4000);
    } catch (err) {
      setError(err.response?.data?.message || 'Error al rechazar la oferta. Inténtelo de nuevo más tarde.');
    }
  };

  // Renderizar el título y subtítulo según el paso actual
  const renderStepHeader = () => {
    const headers = {
      1: {
        title: 'Información inicial',
        subtitle: 'Para comenzar, necesitamos algunos datos básicos sobre su negocio.',
      },
      2: {
        title: 'Información del negocio',
        subtitle: 'Háblenos un poco más sobre su empresa y sector.',
      },
      3: {
        title: 'Información financiera',
        subtitle: 'Ahora necesitamos algunos datos financieros para evaluar su solicitud.',
      },
      4: {
        title: 'Detalles del préstamo',
        subtitle: 'Por último, indíquenos los detalles específicos del préstamo que necesita.',
      },
      5: {
        title: 'Revisión de la oferta',
        subtitle: 'Revise los detalles de su solicitud y oferta de préstamo.',
      },
    };

    return (
      <div className="pb-5 border-b border-gray-200">
        <h1 className="text-2xl font-semibold text-gray-900">
          Solicitar un préstamo - Paso {currentStep} de 5: {headers[currentStep]?.title}
        </h1>
        <p className="mt-2 max-w-4xl text-sm text-gray-500">
          {headers[currentStep]?.subtitle}
        </p>
      </div>
    );
  };

  // Renderizar el indicador de progreso
  const renderProgressBar = () => {
    const totalSteps = 5;
    const progress = (currentStep / totalSteps) * 100;

    return (
      <div className="mb-6">
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className="bg-blue-600 h-2.5 rounded-full"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <div className="flex justify-between mt-2 text-xs text-gray-500">
          <span>Inicio</span>
          <span>Aprobación</span>
        </div>
      </div>
    );
  };

  // Renderizar el formulario según el paso actual
  const renderStepForm = () => {
    switch (currentStep) {
      case 1:
        return (
          <Formik
            initialValues={initialValues}
            validationSchema={validationSchemas[1]}
            onSubmit={handleSubmit}
          >
            {({ isSubmitting }) => (
              <Form className="space-y-6">
                <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                  <div className="sm:col-span-6">
                    <FormInput
                      label="Nombre del negocio"
                      name="business_name"
                      type="text"
                      placeholder="Mi Empresa S.A."
                    />
                  </div>

                  <div className="sm:col-span-3">
                    <FormInput
                      label="Número de identificación fiscal (9 dígitos)"
                      name="tax_id"
                      type="text"
                      placeholder="123456789"
                    />
                  </div>
                </div>

                <div className="pt-5">
                  <div className="flex justify-end">
                    <Button
                      type="button"
                      variant="secondary"
                      className="mr-3"
                      onClick={() => navigate(-1)}
                    >
                      Cancelar
                    </Button>
                    <Button
                      type="submit"
                      variant="primary"
                      isLoading={isSubmitting}
                    >
                      Continuar
                    </Button>
                  </div>
                </div>
              </Form>
            )}
          </Formik>
        );

      case 2:
        return (
          <Formik
            initialValues={initialValues}
            validationSchema={validationSchemas[2]}
            onSubmit={handleSubmit}
          >
            {({ isSubmitting }) => (
              <Form className="space-y-6">
                <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                  <div className="sm:col-span-3">
                    <FormSelect
                      label="Tipo de negocio"
                      name="business_type"
                      options={businessTypeOptions}
                    />
                  </div>

                  <div className="sm:col-span-3">
                    <FormSelect
                      label="Industria"
                      name="industry"
                      options={industryOptions}
                    />
                  </div>

                  <div className="sm:col-span-2">
                    <FormInput
                      label="Años de operación del negocio"
                      name="business_years"
                      type="number"
                      placeholder="5"
                    />
                  </div>
                </div>

                <div className="pt-5">
                  <div className="flex justify-end">
                    <Button
                      type="button"
                      variant="secondary"
                      className="mr-3"
                      onClick={() => setCurrentStep(1)}
                    >
                      Atrás
                    </Button>
                    <Button
                      type="submit"
                      variant="primary"
                      isLoading={isSubmitting}
                    >
                      Continuar
                    </Button>
                  </div>
                </div>
              </Form>
            )}
          </Formik>
        );

      case 3:
        return (
          <Formik
            initialValues={initialValues}
            validationSchema={validationSchemas[3]}
            onSubmit={handleSubmit}
          >
            {({ isSubmitting }) => (
              <Form className="space-y-6">
                <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                  <div className="sm:col-span-3">
                    <FormInput
                      label="Ingresos anuales ($)"
                      name="annual_revenue"
                      type="number"
                      placeholder="100000"
                    />
                  </div>

                  <div className="sm:col-span-3">
                    <FormInput
                      label="Beneficio mensual ($)"
                      name="monthly_profit"
                      type="number"
                      placeholder="8000"
                    />
                  </div>

                  <div className="sm:col-span-6">
                    <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">
                      Información bancaria
                    </h3>
                  </div>

                  <div className="sm:col-span-3">
                    <FormInput
                      label="Nombre del banco"
                      name="bank_name"
                      type="text"
                      placeholder="Banco Nacional"
                    />
                  </div>

                  <div className="sm:col-span-3">
                    <FormInput
                      label="Número de cuenta"
                      name="account_number"
                      type="text"
                      placeholder="1234567890"
                    />
                  </div>
                </div>

                <div className="pt-5">
                  <div className="flex justify-end">
                    <Button
                      type="button"
                      variant="secondary"
                      className="mr-3"
                      onClick={() => setCurrentStep(2)}
                    >
                      Atrás
                    </Button>
                    <Button
                      type="submit"
                      variant="primary"
                      isLoading={isSubmitting}
                    >
                      Continuar
                    </Button>
                  </div>
                </div>
              </Form>
            )}
          </Formik>
        );

      case 4:
        return (
          <Formik
            initialValues={initialValues}
            validationSchema={validationSchemas[4]}
            onSubmit={handleSubmit}
          >
            {({ isSubmitting }) => (
              <Form className="space-y-6">
                <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                  <div className="sm:col-span-3">
                    <FormInput
                      label="Monto del préstamo ($)"
                      name="loan_amount"
                      type="number"
                      placeholder="10000"
                      helpText="Monto máximo: $50,000"
                    />
                  </div>

                  <div className="sm:col-span-3">
                    <FormSelect
                      label="Plazo del préstamo"
                      name="loan_term"
                      options={loanTermOptions}
                    />
                  </div>

                  <div className="sm:col-span-6">
                    <FormTextarea
                      label="Propósito detallado del préstamo"
                      name="loan_purpose"
                      placeholder="Describa con más detalle cómo utilizará el préstamo..."
                      rows={3}
                    />
                  </div>
                </div>

                <div className="pt-5">
                  <div className="flex justify-end">
                    <Button
                      type="button"
                      variant="secondary"
                      className="mr-3"
                      onClick={() => setCurrentStep(3)}
                    >
                      Atrás
                    </Button>
                    <Button
                      type="submit"
                      variant="primary"
                      isLoading={isSubmitting}
                    >
                      Enviar solicitud
                    </Button>
                  </div>
                </div>
              </Form>
            )}
          </Formik>
        );

      case 5:
        // Mostrar detalles de la oferta y opciones para aceptar/rechazar
        if (isApproved && offerDetails) {
          return (
            <div className="space-y-6">
              <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Detalles de la oferta de préstamo</h3>
                  <p className="mt-1 max-w-2xl text-sm text-gray-500">Revise los términos antes de aceptar.</p>
                </div>
                <div className="border-t border-gray-200">
                  <dl>
                    <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-500">Monto aprobado</dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        ${offerDetails.loan_amount?.toLocaleString()}
                      </dd>
                    </div>
                    <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-500">Tasa de interés anual</dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        {offerDetails.loan_interest_rate * 100}%
                      </dd>
                    </div>
                    <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-500">Plazo del préstamo</dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        {offerDetails.loan_term} meses
                      </dd>
                    </div>
                    <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-500">Pago mensual estimado</dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        ${offerDetails.loan_monthly_payment?.toLocaleString()}
                      </dd>
                    </div>
                    <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-500">Costo total del préstamo</dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        ${offerDetails.loan_total_amount?.toLocaleString()}
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>

              <div className="pt-5">
                <div className="flex justify-end">
                  <Button
                    type="button"
                    variant="secondary"
                    className="mr-3"
                    onClick={handleRejectOffer}
                  >
                    Rechazar oferta
                  </Button>
                  <Button
                    type="button"
                    variant="primary"
                    onClick={handleAcceptOffer}
                  >
                    Aceptar oferta
                  </Button>
                </div>
              </div>
            </div>
          );
        } else {
          return (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">Solicitud enviada</h3>
              <p className="mt-1 text-sm text-gray-500">
                Su solicitud ha sido enviada correctamente. Le notificaremos cuando tengamos una respuesta.
              </p>
              <div className="mt-6">
                <Button
                  type="button"
                  variant="primary"
                  onClick={() => navigate('/loan-applications')}
                >
                  Ver mis solicitudes
                </Button>
              </div>
            </div>
          );
        }

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {renderStepHeader()}
      {renderProgressBar()}

      <Card>
        {error && (
          <Alert 
            type="error"
            message={error}
            className="mb-6"
          />
        )}
        
        {success && (
          <Alert 
            type="success"
            message={success}
            className="mb-6"
          />
        )}

        {renderStepForm()}
      </Card>
    </div>
  );
};

export default LoanApplicationForm; 