// Type definitions for the trip planner app

export interface Waypoint {
  id: string;
  name: string;
  address?: string;
  lat?: number;
  lng?: number;
}

export interface Trip {
  id: string;
  title: string;
  date: string;
  stops: number;
  waypoints: Waypoint[];
  startTime?: string;
  duration?: number;
  durationType?: 'hours' | 'days';
  optimizedRoute?: OptimizedRoute;
}

export interface OptimizedRoute {
  recommendedStart: string;
  totalTime: string;
  warnings: TrafficWarning[];
  itinerary: ItineraryDay[];
  mapData?: {
    center: { lat: number; lng: number };
    zoom: number;
    waypoints: Array<{ lat: number; lng: number; name: string }>;
  };
}

export interface TrafficWarning {
  severity: 'low' | 'medium' | 'high';
  message: string;
  segment?: string;
}

export interface ItineraryDay {
  day: number;
  date: string;
  stops: ItineraryStop[];
}

export interface ItineraryStop {
  time: string;
  type: 'depart' | 'arrive';
  location: string;
  insight?: string;
  trafficLevel?: 'light' | 'moderate' | 'heavy';
}
