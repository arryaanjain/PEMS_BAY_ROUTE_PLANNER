// WaypointList component - draggable list of waypoints

import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import type { Waypoint } from '../types';
import { WaypointItem } from './WaypointItem';

interface WaypointListProps {
  waypoints: Waypoint[];
  onReorder: (waypoints: Waypoint[]) => void;
  onDelete: (id: string) => void;
}

export function WaypointList({ waypoints, onReorder, onDelete }: WaypointListProps) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = waypoints.findIndex((w) => w.id === active.id);
      const newIndex = waypoints.findIndex((w) => w.id === over.id);
      onReorder(arrayMove(waypoints, oldIndex, newIndex));
    }
  };

  if (waypoints.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No waypoints added yet. Add your first location above.
      </div>
    );
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={waypoints.map(w => w.id)} strategy={verticalListSortingStrategy}>
        <div className="space-y-2">
          {waypoints.map((waypoint, index) => (
            <WaypointItem
              key={waypoint.id}
              waypoint={waypoint}
              index={index}
              onDelete={onDelete}
            />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  );
}
