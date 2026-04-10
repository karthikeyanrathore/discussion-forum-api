import React from 'react';

const Navbar = () => {
  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-6xl mx-auto px-4 py-4">
        <h1 className="text-2xl font-bold text-gray-800">My Notes App</h1>
        <p className="text-sm text-gray-500">Create and manage your notes</p>
      </div>
    </nav>
  );
};

export default Navbar;