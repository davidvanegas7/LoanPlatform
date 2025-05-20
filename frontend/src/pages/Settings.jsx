import React, { useState, useEffect } from 'react';
import { FiGlobe } from 'react-icons/fi';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Alert from '../components/common/Alert';
import AuthService from '../services/auth.service';

/**
 * Página de configuración de usuario
 */
const Settings = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [settings, setSettings] = useState({
    language: 'en'
  });

  // Obtener la configuración del usuario al cargar el componente
  useEffect(() => {
    const fetchUserSettings = async () => {
      try {
        const user = await AuthService.getUserProfile();
        
        if (user) {
          setSettings(prev => ({
            ...prev,
            language: user.language || 'en'
          }));
        }
      } catch (error) {
        console.error('Error al obtener la configuración del usuario:', error);
      }
    };

    fetchUserSettings();
  }, []);

  const handleLanguageChange = (e) => {
    setSettings(prev => ({
      ...prev,
      language: e.target.value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Actualizar el idioma en el backend usando AuthService
      await AuthService.updateUserSettings({ language: settings.language });

      setMessage({
        type: 'success',
        text: 'Configuración guardada correctamente'
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || 'Error al guardar la configuración'
      });
      console.error('Error saving settings:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Configuración</h1>
      
      {message.text && (
        <Alert 
          type={message.type}
          message={message.text}
          className="mb-6"
        />
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <Card title="Preferencias">
          <div className="space-y-4">
            <div className="flex items-center">
              <FiGlobe className="text-gray-400 mr-3" />
              <span className="text-sm text-gray-700 mr-4">Idioma</span>
              <select
                value={settings.language}
                onChange={handleLanguageChange}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="es">Español</option>
                <option value="en">Inglés</option>
              </select>
            </div>
          </div>
        </Card>

        <div className="flex justify-end">
          <Button
            type="submit"
            variant="primary"
            disabled={loading}
          >
            {loading ? 'Guardando...' : 'Guardar Configuración'}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default Settings; 