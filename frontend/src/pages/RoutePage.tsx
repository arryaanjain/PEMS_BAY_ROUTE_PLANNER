// Route page - displays optimized route results

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import type { Trip } from '../types';
import { getTrip } from '../utils/storage';
import { Header } from '../components/Header';
import { MapDisplay } from '../components/MapDisplay';
import { KeyInsights } from '../components/KeyInsights';
import { TrafficWarning } from '../components/TrafficWarning';
import { ItineraryView } from '../components/ItineraryView';
import { ActionButtons } from '../components/ActionButtons';

export function RoutePage() {
  const { tripId } = useParams<{ tripId: string }>();
  const navigate = useNavigate();
  const [trip, setTrip] = useState<Trip | null>(null);

  useEffect(() => {
    if (tripId) {
      const foundTrip = getTrip(tripId);
      if (foundTrip) {
        setTrip(foundTrip);
      } else {
        navigate('/');
      }
    }
  }, [tripId, navigate]);

  if (!trip || !trip.optimizedRoute) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading route...</p>
      </div>
    );
  }

  const handleSave = () => {
    alert('Trip already saved!');
  };

  const handleNavigate = () => {
    const firstWaypoint = trip.waypoints[0];
    if (firstWaypoint) {
      // Open Google Maps with the first waypoint
      const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
        firstWaypoint.name
      )}`;
      window.open(mapsUrl, '_blank');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      <Header title="Your Optimized Plan" showBack />

      <main className="container mx-auto px-4 py-6 max-w-4xl space-y-6">
        {/* Map */}
        <MapDisplay waypoints={trip.waypoints} />

        {/* Key Insights */}
        <KeyInsights route={trip.optimizedRoute} />

        {/* Traffic Warnings */}
        {trip.optimizedRoute.warnings.length > 0 && (
          <div className="space-y-3">
            {trip.optimizedRoute.warnings.map((warning, idx) => (
              <TrafficWarning key={idx} warning={warning} />
            ))}
          </div>
        )}

        {/* Itinerary */}
        <ItineraryView itinerary={trip.optimizedRoute.itinerary} />
      </main>

      {/* Action Buttons */}
      <ActionButtons
        firstWaypoint={trip.waypoints[0]?.name}
        onSave={handleSave}
        onNavigate={handleNavigate}
      />
    </div>
  );
}
