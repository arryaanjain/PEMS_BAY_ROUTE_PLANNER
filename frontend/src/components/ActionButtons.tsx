// ActionButtons component - navigation and save actions

import { Navigation, Save } from 'lucide-react';
import { Button } from './Button';

interface ActionButtonsProps {
  firstWaypoint?: string;
  onSave: () => void;
  onNavigate: () => void;
}

export function ActionButtons({ onSave, onNavigate }: ActionButtonsProps) {
  return (
    <div className="sticky bottom-0 bg-white border-t border-gray-200 p-4 shadow-lg">
      <div className="container mx-auto max-w-2xl flex gap-3">
        <Button
          variant="primary"
          size="lg"
          onClick={onNavigate}
          className="flex-1 flex items-center justify-center gap-2"
        >
          <Navigation className="w-5 h-5" />
          Start Navigation
        </Button>
        <Button
          variant="secondary"
          size="lg"
          onClick={onSave}
          className="flex items-center justify-center gap-2"
        >
          <Save className="w-5 h-5" />
          Save Trip
        </Button>
      </div>
    </div>
  );
}
