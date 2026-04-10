import React, { useState } from 'react';
import NoteCard from './components/NoteCard';
import NoteModal from './components/NoteModal';
import { mockNotes } from './mockNotes';

// Main App component
// Displays all notes in a grid layout with modal functionality
function App() {
  // State to track which note is currently selected (null if none)
  const [selectedNote, setSelectedNote] = useState(null);

  // Function to open a note in the modal
  const handleNoteClick = (note) => {
    setSelectedNote(note);
    console.log('Opened note:', note.title);
  };

  // Function to close the modal
  const handleCloseModal = () => {
    setSelectedNote(null);
    console.log('Closed modal');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            My Notes
          </h1>
          <p className="text-gray-600">
            Displaying {mockNotes.length} notes - Click any note to view in full
          </p>
        </div>
        
        {/* Notes Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mockNotes.map((note) => (
            <NoteCard
              key={note.id}
              note={note}
              onClick={() => handleNoteClick(note)}
            />
          ))}
        </div>
      </div>

      {/* Modal - only renders when a note is selected */}
      <NoteModal
        note={selectedNote}
        onClose={handleCloseModal}
      />
    </div>
  );
}

export default App;