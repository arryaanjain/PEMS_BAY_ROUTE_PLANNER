// TripCard component - displays a single trip in the list

import type { Trip } from '../types';
import { Card } from './Card';
import { MapPin, Calendar } from 'lucide-react';

interface TripCardProps {
  trip: Trip;
  onClick: () => void;
}

export function TripCard({ trip, onClick }: TripCardProps) {
  return (
    <Card onClick={onClick} className="p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{trip.title}</h3>
          <div className="flex flex-wrap gap-3 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              <span>{trip.date}</span>
            </div>
            <div className="flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              <span>{trip.stops} {trip.stops === 1 ? 'Stop' : 'Stops'}</span>
            </div>
          </div>
        </div>
        <div className="text-gray-400">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </Card>
  );
}
