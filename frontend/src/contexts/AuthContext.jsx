import React, { createContext, useContext, useState, useEffect } from 'react';
import AuthService from '../services/auth.service';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Verificar si hay un usuario autenticado al cargar la aplicación
    const checkAuthentication = () => {
      setLoading(true);
      if (AuthService.isAuthenticated()) {
        setCurrentUser(AuthService.getCurrentUser());
      }
      setLoading(false);
    };

    checkAuthentication();
  }, []);

  const login = async (email, password) => {
    try {
      setLoading(true);
      setError(null);
      const data = await AuthService.login(email, password);
      setCurrentUser(AuthService.getCurrentUser());
      return data;
    } catch (err) {
      setError(err.response?.data?.message || 'Error al iniciar sesión');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      setError(null);
      const data = await AuthService.register(userData);
      return data;
    } catch (err) {
      setError(err.response?.data?.message || 'Error al registrarse');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setCurrentUser(null);
    AuthService.logout();
  };

  const value = {
    currentUser,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!currentUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext; 