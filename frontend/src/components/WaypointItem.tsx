// WaypointItem component - single draggable waypoint

import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical, X } from 'lucide-react';
import type { Waypoint } from '../types';

interface WaypointItemProps {
  waypoint: Waypoint;
  index: number;
  onDelete: (id: string) => void;
}

export function WaypointItem({ waypoint, index, onDelete }: WaypointItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: waypoint.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="bg-white border border-gray-200 rounded-lg p-3 flex items-center gap-3 shadow-sm"
    >
      <button
        {...attributes}
        {...listeners}
        className="cursor-grab active:cursor-grabbing text-gray-400 hover:text-gray-600"
        aria-label="Drag to reorder"
      >
        <GripVertical className="w-5 h-5" />
      </button>
      
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-700 text-sm font-semibold">
            {index + 1}
          </span>
          <span className="text-gray-900 font-medium">{waypoint.name}</span>
        </div>
      </div>

      <button
        onClick={() => onDelete(waypoint.id)}
        className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
        aria-label="Delete waypoint"
      >
        <X className="w-5 h-5" />
      </button>
    </div>
  );
}
