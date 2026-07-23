import React from 'react';

interface PaywallModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const PaywallModal: React.FC<PaywallModalProps> = ({ isOpen, onClose }) => {
  return isOpen ? (
    <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center' }} onClick={onClose}>
      <div style={{ background: 'white', padding: '20px', borderRadius: '8px' }} onClick={(e) => e.stopPropagation()}>
        <h2>Upgrade Required</h2>
        <p>This feature requires a premium subscription.</p>
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  ) : null;
};

export default PaywallModal;
