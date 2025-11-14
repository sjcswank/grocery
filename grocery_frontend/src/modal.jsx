import React from 'react';
import ReactDOM from 'react-dom';
import { X } from 'lucide-react';
import './modal.css'; // Add styling in Step C

const Modal = ({ isOpen, onClose, title, children, closeText, onConfirm }) => {
  if (!isOpen) return null;

  return ReactDOM.createPortal(
    // The overlay handles clicks outside the modal to close it
    <div className="modal-overlay" onClick={onClose}>
      {/* StopPropagation prevents clicks inside the modal from closing it */}
      <div className="modal-content flex flex-col max-h-screen bg-white rounded-lg shadow-sm p-4 mb-6" onClick={e => e.stopPropagation()}>
        <div className="flex modal-header ">
          <h4 className="modal-title text-lg font-medium text-neutral-700 mb-4 w-1/2">{title}</h4>
          <button onClick={onClose} className="modal-close-button flex w-1/2 justify-end">
            <X size={18} />
          </button>
        </div>
        {/* {modalError && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
                    {modalError}
                    </div>
                )} */}
        <div className="modal-body overflow-y-auto grow">
          {children} {/* This renders content passed from the parent */}
        </div>
        <div>
          <button className='px-4 py-2 bg-neutral-800 text-white rounded-md hover:bg-neutral-700 transition-colors' onClick={onConfirm}>{closeText}</button>
        </div>
      </div>
    </div>,
    document.getElementById('modal-root')
  );
};

export default Modal;
