import React from 'react';
import Modal from '../common/Modal';

const PrivacyPolicy = ({ isOpen, onClose }) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Política de Privacidad / Privacy Policy"
      size="lg"
    >
      <div className="space-y-6">
        {/* Español */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Política de Privacidad</h2>
          <div className="prose prose-sm max-w-none">
            <p>Última actualización: {new Date().toLocaleDateString()}</p>
            
            <h3>1. Recopilación de Información</h3>
            <p>Recopilamos información que usted nos proporciona directamente, incluyendo nombre, correo electrónico, información de contacto y datos relacionados con préstamos y pagos.</p>
            
            <h3>2. Uso de la Información</h3>
            <p>Utilizamos su información para:</p>
            <ul>
              <li>Proporcionar y mantener nuestros servicios</li>
              <li>Procesar transacciones</li>
              <li>Enviar notificaciones importantes</li>
              <li>Mejorar nuestros servicios</li>
            </ul>
            
            <h3>3. Protección de Datos</h3>
            <p>Implementamos medidas de seguridad técnicas y organizativas para proteger su información personal contra acceso no autorizado o divulgación.</p>
            
            <h3>4. Compartir Información</h3>
            <p>No vendemos ni compartimos su información personal con terceros, excepto cuando sea necesario para proporcionar nuestros servicios o cumplir con obligaciones legales.</p>
            
            <h3>5. Sus Derechos</h3>
            <p>Usted tiene derecho a acceder, corregir o eliminar su información personal. Para ejercer estos derechos, contáctenos a través de los canales proporcionados.</p>
          </div>
        </div>

        {/* English */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Privacy Policy</h2>
          <div className="prose prose-sm max-w-none">
            <p>Last updated: {new Date().toLocaleDateString()}</p>
            
            <h3>1. Information Collection</h3>
            <p>We collect information that you provide directly to us, including name, email, contact information, and data related to loans and payments.</p>
            
            <h3>2. Use of Information</h3>
            <p>We use your information to:</p>
            <ul>
              <li>Provide and maintain our services</li>
              <li>Process transactions</li>
              <li>Send important notifications</li>
              <li>Improve our services</li>
            </ul>
            
            <h3>3. Data Protection</h3>
            <p>We implement technical and organizational security measures to protect your personal information against unauthorized access or disclosure.</p>
            
            <h3>4. Information Sharing</h3>
            <p>We do not sell or share your personal information with third parties, except when necessary to provide our services or comply with legal obligations.</p>
            
            <h3>5. Your Rights</h3>
            <p>You have the right to access, correct, or delete your personal information. To exercise these rights, contact us through the provided channels.</p>
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default PrivacyPolicy; 