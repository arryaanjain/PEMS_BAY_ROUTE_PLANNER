// MapDisplay component - shows route overview map

import { MapPin } from 'lucide-react';

interface MapDisplayProps {
  waypoints: Array<{ name: string }>;
}

export function MapDisplay({ waypoints }: MapDisplayProps) {
  // This is a placeholder map. In production, integrate Google Maps or Mapbox
  return (
    <div className="relative w-full h-64 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl overflow-hidden shadow-md">
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <MapPin className="w-12 h-12 text-blue-600 mx-auto mb-2" />
          <p className="text-blue-800 font-medium">Route Map</p>
          <p className="text-sm text-blue-600 mt-1">
            {waypoints.length} stops planned
          </p>
        </div>
      </div>
      
      {/* Decorative route line */}
      <svg className="absolute inset-0 w-full h-full opacity-30" viewBox="0 0 100 100" preserveAspectRatio="none">
        <path
          d="M 10,50 Q 30,20 50,50 T 90,50"
          stroke="#2563eb"
          strokeWidth="2"
          fill="none"
          strokeDasharray="5,5"
        />
      </svg>
    </div>
  );
}
