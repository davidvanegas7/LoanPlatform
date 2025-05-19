import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/common/PrivateRoute';
import PublicRoute from './components/common/PublicRoute';

// Páginas públicas
import Login from './pages/Login';
import Register from './pages/Register';

// Páginas privadas
import Dashboard from './pages/Dashboard';
import LoanApplicationForm from './pages/LoanApplicationForm';
import LoanApplications from './pages/LoanApplications';
import LoanApplicationDetails from './pages/LoanApplicationDetails';
import Loans from './pages/Loans';
import LoanDetails from './pages/LoanDetails';
import Payments from './pages/Payments';
import Profile from './pages/Profile';
import Settings from './pages/Settings';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Rutas públicas */}
          <Route element={<PublicRoute restricted={true} />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Route>

          {/* Rutas privadas */}
          <Route element={<PrivateRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/loan-applications/new" element={<LoanApplicationForm />} />
            <Route path="/loan-applications" element={<LoanApplications />} />
            <Route path="/loan-applications/:id" element={<LoanApplicationDetails />} />
            <Route path="/loans" element={<Loans />} />
            <Route path="/loans/:id" element={<LoanDetails />} />
            <Route path="/payments" element={<Payments />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
          </Route>

          {/* Redireccionamiento a dashboard o login según autenticación */}
          <Route
            path="*"
            element={<Navigate to="/dashboard" replace />}
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App; 