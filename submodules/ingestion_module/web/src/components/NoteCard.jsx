import React from 'react';

// Component to display a single note
// Props:
// - note: object with { id, title, content, createdAt }
// - onClick: function to call when card is clicked
const NoteCard = ({ note, onClick }) => {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow cursor-pointer"
    >
      {/* Note Title */}
      <h3 className="font-semibold text-lg text-gray-800 mb-2">
        {note.title}
      </h3>
      
      {/* Note Content - truncated preview */}
      <p className="text-gray-600 mb-3 text-sm line-clamp-3">
        {note.content}
      </p>
      
      {/* Creation Date */}
      <div className="flex justify-between items-center">
        <p className="text-xs text-gray-400">
          {new Date(note.createdAt).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
          })}
        </p>
        
        {/* Click indicator */}
        <p className="text-xs text-blue-500 font-medium">
          Click to view 
        </p>
      </div>
    </div>
  );
};

export default NoteCard;