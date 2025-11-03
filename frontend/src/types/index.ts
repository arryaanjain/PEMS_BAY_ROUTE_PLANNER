// Type definitions for the trip planner app

export interface Waypoint {
  id: string;
  name: string;
  address?: string;
  lat: number;
  lng: number;
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

// Route segment with traffic predictions
export interface RouteSegment {
  id: string;
  fromLocation: {
    name: string;
    lat: number;
    lng: number;
  };
  toLocation: {
    name: string;
    lat: number;
    lng: number;
  };
  predictedTravelTime: number; // minutes
  trafficCondition: 'light' | 'moderate' | 'heavy';
  congestionScore: number; // 0-1
  timeWindow: {
    start: string;
    end: string;
  };
}

// Optimized route from backend
export interface OptimizedRoute {
  optimizedOrder: number[]; // Indices of waypoints in optimal order
  recommendedStart: string; // ISO datetime
  totalTravelTime: number; // minutes
  insights: {
    warnings: TrafficWarning[];
    recommendations: any[];
  };
  itinerary: ItineraryDay[];
  segments: RouteSegment[];
}

export interface TrafficWarning {
  severity: 'low' | 'medium' | 'high';
  message: string;
  location?: string;
  timeWindow?: {
    start: string;
    end: string;
  };
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
  segmentId?: string | null;
  travelTime?: number | null; // minutes
  insight?: string | null;
  trafficLevel?: 'light' | 'moderate' | 'heavy' | null;
}

