import React, { useState } from 'react';
import TermsAndConditions from '../legal/TermsAndConditions';
import PrivacyPolicy from '../legal/PrivacyPolicy';

/**
 * Componente de pie de página
 */
const Footer = () => {
  const currentYear = new Date().getFullYear();
  const [isTermsOpen, setIsTermsOpen] = useState(false);
  const [isPrivacyOpen, setIsPrivacyOpen] = useState(false);
  
  return (
    <>
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 md:flex md:items-center md:justify-between lg:px-8">
          <div className="flex justify-center space-x-6 md:order-2">
            <button
              onClick={() => setIsTermsOpen(true)}
              className="text-gray-400 hover:text-gray-500"
            >
              <span className="sr-only">Términos y condiciones</span>
              Términos y condiciones
            </button>
            <button
              onClick={() => setIsPrivacyOpen(true)}
              className="text-gray-400 hover:text-gray-500"
            >
              <span className="sr-only">Política de privacidad</span>
              Política de privacidad
            </button>
          </div>
          <div className="mt-8 md:mt-0 md:order-1">
            <p className="text-center text-sm text-gray-400">
              &copy; {currentYear} LoanTracker. Todos los derechos reservados.
            </p>
          </div>
        </div>
      </footer>

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

export default Footer; 