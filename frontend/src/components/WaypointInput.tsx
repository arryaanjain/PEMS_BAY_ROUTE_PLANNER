// WaypointInput component - add new waypoints

import { useState } from 'react';
import { Plus } from 'lucide-react';
import { Button } from './Button';

interface WaypointInputProps {
  onAdd: (name: string) => void;
}

export function WaypointInput({ onAdd }: WaypointInputProps) {
  const [value, setValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) {
      onAdd(value.trim());
      setValue('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Add a location..."
        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
      <Button type="submit" size="md" className="flex items-center gap-2">
        <Plus className="w-5 h-5" />
        Add
      </Button>
    </form>
  );
}
