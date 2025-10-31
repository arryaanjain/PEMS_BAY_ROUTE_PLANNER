// Local storage utilities for trips

import type { Trip } from '../types';

const TRIPS_KEY = 'pems_bay_trips';

export function getTrips(): Trip[] {
  const data = localStorage.getItem(TRIPS_KEY);
  return data ? JSON.parse(data) : [];
}

export function saveTrip(trip: Trip): void {
  const trips = getTrips();
  const existingIndex = trips.findIndex(t => t.id === trip.id);
  
  if (existingIndex >= 0) {
    trips[existingIndex] = trip;
  } else {
    trips.unshift(trip);
  }
  
  localStorage.setItem(TRIPS_KEY, JSON.stringify(trips));
}

export function deleteTrip(id: string): void {
  const trips = getTrips().filter(t => t.id !== id);
  localStorage.setItem(TRIPS_KEY, JSON.stringify(trips));
}

export function getTrip(id: string): Trip | undefined {
  return getTrips().find(t => t.id === id);
}

