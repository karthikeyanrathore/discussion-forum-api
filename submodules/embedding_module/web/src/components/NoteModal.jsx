import React from 'react';

// Modal component to display full note content
// Props:
// - note: the note object to display
// - onClose: function to call when closing the modal
const NoteModal = ({ note, onClose }) => {
  // If no note is provided, don't render anything
  if (!note) return null;

  // Handle clicking outside the modal (on backdrop) to close
  const handleBackdropClick = (e) => {
    // Only close if clicking the backdrop itself, not the modal content
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Handle escape key to close modal
  React.useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    // Add event listener when modal opens
    document.addEventListener('keydown', handleEscape);

    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';

    // Cleanup: remove listener and restore scroll when modal closes
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [onClose]);

  return (
    // Backdrop - semi-transparent dark overlay
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      {/* Modal Content */}
      <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-start">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              {note.title}
            </h2>
            <p className="text-sm text-gray-500">
              Created: {new Date(note.createdAt).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>
          
          {/* Close Button */}
          <button
            onClick={onClose}
            className="ml-4 text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close modal"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6">
          <p className="text-gray-700 text-base leading-relaxed whitespace-pre-wrap">
            {note.content}
          </p>
        </div>

        {/* Modal Footer */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 p-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default NoteModal;