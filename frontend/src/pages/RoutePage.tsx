// Route page - displays optimized route results

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import type { Trip } from '../types';
import { getTrip } from '../utils/storage';
import { Header } from '../components/Header';
import { MapDisplay } from '../components/MapDisplay';
import { RouteOverview } from '../components/RouteOverview';
import { RouteSegmentCard } from '../components/RouteSegmentCard';
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
      <Header title="Your Optimized Route" showBack />

      <main className="container mx-auto px-4 py-6 max-w-6xl space-y-6">
        {/* Route Overview with CNN Predictions */}
        <RouteOverview 
          optimizedRoute={trip.optimizedRoute} 
          originalWaypoints={trip.waypoints}
        />

        {/* Map */}
        <MapDisplay waypoints={trip.waypoints} />

        {/* Route Segments with Traffic Data */}
        {trip.optimizedRoute.segments && trip.optimizedRoute.segments.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-gray-900">Route Segments & Traffic</h2>
            <div className="grid gap-4 md:grid-cols-2">
              {trip.optimizedRoute.segments.map((segment, index) => (
                <RouteSegmentCard key={segment.id} segment={segment} index={index} />
              ))}
            </div>
          </div>
        )}

        {/* Detailed Itinerary */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">Detailed Itinerary</h2>
          <ItineraryView itinerary={trip.optimizedRoute.itinerary} />
        </div>
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
