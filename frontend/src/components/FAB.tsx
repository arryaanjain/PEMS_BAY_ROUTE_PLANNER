// Floating Action Button (FAB) component

import { Plus } from 'lucide-react';

interface FABProps {
  onClick: () => void;
}

export function FAB({ onClick }: FABProps) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 w-16 h-16 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 active:bg-blue-800 transition-all duration-200 hover:scale-110 active:scale-95 flex items-center justify-center z-50"
      aria-label="Create new trip"
    >
      <Plus className="w-8 h-8" />
    </button>
  );
}
