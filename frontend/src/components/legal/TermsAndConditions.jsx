import React from 'react';
import Modal from '../common/Modal';

const TermsAndConditions = ({ isOpen, onClose }) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Términos y Condiciones / Terms and Conditions"
      size="lg"
    >
      <div className="space-y-6">
        {/* Español */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Términos y Condiciones</h2>
          <div className="prose prose-sm max-w-none">
            <p>Última actualización: {new Date().toLocaleDateString()}</p>
            
            <h3>1. Aceptación de los Términos</h3>
            <p>Al acceder y utilizar LoanTracker, usted acepta estar sujeto a estos términos y condiciones. Si no está de acuerdo con alguna parte de estos términos, no podrá acceder al servicio.</p>
            
            <h3>2. Descripción del Servicio</h3>
            <p>LoanTracker es una plataforma diseñada para gestionar y dar seguimiento a préstamos y pagos. El servicio está sujeto a cambios, interrupciones o terminación en cualquier momento.</p>
            
            <h3>3. Cuentas de Usuario</h3>
            <p>Los usuarios son responsables de mantener la confidencialidad de sus credenciales de acceso y de todas las actividades que ocurran bajo su cuenta.</p>
            
            <h3>4. Uso Aceptable</h3>
            <p>Los usuarios acuerdan utilizar el servicio solo para fines legales y de acuerdo con estos términos. No se permite el uso indebido o fraudulento del servicio.</p>
            
            <h3>5. Limitación de Responsabilidad</h3>
            <p>LoanTracker no será responsable por daños indirectos, incidentales o consecuentes que resulten del uso o la imposibilidad de usar el servicio.</p>
          </div>
        </div>

        {/* English */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Terms and Conditions</h2>
          <div className="prose prose-sm max-w-none">
            <p>Last updated: {new Date().toLocaleDateString()}</p>
            
            <h3>1. Acceptance of Terms</h3>
            <p>By accessing and using LoanTracker, you agree to be bound by these terms and conditions. If you disagree with any part of these terms, you may not access the service.</p>
            
            <h3>2. Service Description</h3>
            <p>LoanTracker is a platform designed to manage and track loans and payments. The service is subject to change, interruption, or termination at any time.</p>
            
            <h3>3. User Accounts</h3>
            <p>Users are responsible for maintaining the confidentiality of their access credentials and for all activities that occur under their account.</p>
            
            <h3>4. Acceptable Use</h3>
            <p>Users agree to use the service only for lawful purposes and in accordance with these terms. Misuse or fraudulent use of the service is not permitted.</p>
            
            <h3>5. Limitation of Liability</h3>
            <p>LoanTracker shall not be liable for any indirect, incidental, or consequential damages resulting from the use or inability to use the service.</p>
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default TermsAndConditions; 