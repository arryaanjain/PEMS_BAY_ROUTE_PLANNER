// API service functions for backend communication

import { getApiUrl } from '../utils/config';
import type { Waypoint, Trip, OptimizedRoute } from '../types';

const API_URL = getApiUrl();

// Location Services
export async function autocompleteLocation(query: string): Promise<Waypoint[]> {
  try {
    const response = await fetch(`${API_URL}/api/locations/autocomplete?query=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error('Failed to fetch location suggestions');
    }
    const data = await response.json();
    return data.map((loc: any) => ({
      id: loc.id || crypto.randomUUID(),
      name: loc.name,
      lat: loc.lat,
      lng: loc.lng,
    }));
  } catch (error) {
    console.error('Autocomplete error:', error);
    // Return empty array on error instead of throwing
    // This allows the UI to gracefully handle API failures
    return [];
  }
}

export async function validateLocation(
  name: string,
  coordinates?: { lat: number; lng: number }
): Promise<{
  valid: boolean;
  location?: Waypoint;
  message?: string;
}> {
  try {
    const response = await fetch(`${API_URL}/api/locations/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, coordinates }),
    });
    
    if (!response.ok) {
      // Handle different HTTP error codes
      if (response.status === 400) {
        return {
          valid: false,
          message: 'Invalid location data provided',
        };
      }
      if (response.status === 404) {
        return {
          valid: false,
          message: 'Location not found',
        };
      }
      throw new Error('Failed to validate location');
    }
    
    const data = await response.json();
    
    // Ensure location has an ID if it's valid
    if (data.valid && data.location && !data.location.id) {
      data.location.id = crypto.randomUUID();
    }
    
    return data;
  } catch (error) {
    console.error('Validation error:', error);
    // Return a user-friendly error response
    return {
      valid: false,
      message: 'Unable to validate location. Please check your connection and try again.',
    };
  }
}

// Route Optimization
export interface OptimizeRouteRequest {
  waypoints: Waypoint[];
  startTime: string;
  duration: number;
  durationType: 'hours' | 'days';
}

export async function optimizeRoute(request: OptimizeRouteRequest): Promise<OptimizedRoute> {
  const response = await fetch(`${API_URL}/api/routes/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to optimize route');
  }
  
  return response.json();
}

// Trip Management (optional - for server-side storage)
export async function saveTrip(trip: Trip): Promise<Trip> {
  const response = await fetch(`${API_URL}/api/trips`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(trip),
  });
  
  if (!response.ok) throw new Error('Failed to save trip');
  return response.json();
}

export async function getTrips(): Promise<Trip[]> {
  const response = await fetch(`${API_URL}/api/trips`);
  if (!response.ok) throw new Error('Failed to fetch trips');
  return response.json();
}

export async function getTrip(id: string): Promise<Trip> {
  const response = await fetch(`${API_URL}/api/trips/${id}`);
  if (!response.ok) throw new Error('Failed to fetch trip');
  return response.json();
}

export async function deleteTrip(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/trips/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete trip');
}
