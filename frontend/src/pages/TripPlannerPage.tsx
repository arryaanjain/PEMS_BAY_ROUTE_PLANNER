// Trip Planner page - create and configure a new trip

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/Header';
import { WaypointInput } from '../components/WaypointInput';
import { WaypointList } from '../components/WaypointList';
import { TimeSettings } from '../components/TimeSettings';
import { Button } from '../components/Button';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { saveTrip } from '../utils/storage';
import { optimizeRoute } from '../services/api';
import { type Waypoint } from '../types';

export function TripPlannerPage() {
  const navigate = useNavigate();
  const [waypoints, setWaypoints] = useState<Waypoint[]>([]);
  const [startTime, setStartTime] = useState(() => {
    const now = new Date();
    now.setMinutes(0);
    return now.toISOString().slice(0, 16);
  });
  const [duration, setDuration] = useState(8);
  const [durationType, setDurationType] = useState<'hours' | 'days'>('hours');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddWaypoint = (waypoint: Waypoint) => {
    setWaypoints([...waypoints, waypoint]);
  };

  const handleDeleteWaypoint = (id: string) => {
    setWaypoints(waypoints.filter((w) => w.id !== id));
  };

  const handleReorderWaypoints = (newWaypoints: Waypoint[]) => {
    setWaypoints(newWaypoints);
  };

  const handleOptimize = async () => {
    if (waypoints.length < 2) {
      alert('Please add at least 2 waypoints');
      return;
    }

    setIsOptimizing(true);
    setError(null);

    try {
      // Call real backend API
      const optimizedRoute = await optimizeRoute({
        waypoints,
        startTime,
        duration,
        durationType,
      });

      // Create trip with optimized route from API
      const tripId = crypto.randomUUID();
      const trip = {
        id: tripId,
        title: `Trip to ${waypoints[waypoints.length - 1].name}`,
        date: new Date(startTime).toLocaleDateString(),
        stops: waypoints.length,
        waypoints,
        startTime,
        duration,
        durationType,
        optimizedRoute,
      };

      saveTrip(trip);
      setIsOptimizing(false);
      navigate(`/route/${tripId}`);
    } catch (err) {
      console.error('Optimization error:', err);
      setError(err instanceof Error ? err.message : 'Failed to optimize route. Please try again.');
      setIsOptimizing(false);
    }
  };

  if (isOptimizing) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header title="New Trip" showBack />

      <main className="container mx-auto px-4 py-6 max-w-2xl">
        <div className="space-y-6">
          {/* Waypoints Section */}
          <section className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Locations</h2>
            <div className="space-y-4">
              <WaypointInput onAdd={handleAddWaypoint} />
              <WaypointList
                waypoints={waypoints}
                onReorder={handleReorderWaypoints}
                onDelete={handleDeleteWaypoint}
              />
            </div>
          </section>

          {/* Time Settings Section */}
          <section className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Trip Settings</h2>
            <TimeSettings
              startTime={startTime}
              duration={duration}
              durationType={durationType}
              onStartTimeChange={setStartTime}
              onDurationChange={setDuration}
              onDurationTypeChange={setDurationType}
            />
          </section>

          {/* Optimize Button */}
          <Button
            variant="primary"
            size="lg"
            onClick={handleOptimize}
            className="w-full"
            disabled={waypoints.length < 2}
          >
            Optimize My Route
          </Button>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              <p className="font-medium">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          )}

          {waypoints.length < 2 && (
            <p className="text-sm text-gray-500 text-center">
              Add at least 2 locations to optimize your route
            </p>
          )}
        </div>
      </main>
    </div>
  );
}
