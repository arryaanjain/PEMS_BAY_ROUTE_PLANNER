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
import { type Waypoint, type ItineraryStop } from '../types';

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

  const handleAddWaypoint = (name: string) => {
    const newWaypoint: Waypoint = {
      id: crypto.randomUUID(),
      name,
    };
    setWaypoints([...waypoints, newWaypoint]);
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

    // Simulate API call for demo
    // TODO: Replace with actual API call to backend
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Create mock optimized route
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
      optimizedRoute: {
        recommendedStart: new Date(startTime).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        }),
        totalTime: '4h 12m',
        warnings: [
          {
            severity: 'high' as const,
            message: `High Congestion: Avoid the area near ${waypoints[1]?.name || 'stop 2'} after 5 PM.`,
          },
        ],
        itinerary: [
          {
            day: 1,
            date: new Date(startTime).toLocaleDateString(),
            stops: waypoints.flatMap((wp, idx): ItineraryStop[] => {
              const baseTime = new Date(startTime);
              const offset = idx * 90; // 1.5 hours between stops
              
              const departTime = new Date(baseTime.getTime() + offset * 60000);
              const arriveTime = new Date(baseTime.getTime() + (offset + 30) * 60000);

              if (idx === 0) {
                return [
                  {
                    time: departTime.toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    }),
                    type: 'depart' as const,
                    location: wp.name,
                    insight: 'Starting your journey',
                  },
                ];
              }
              
              return [
                {
                  time: arriveTime.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  }),
                  type: 'arrive' as const,
                  location: wp.name,
                  insight:
                    idx === 1
                      ? 'This route has light traffic.'
                      : 'Busiest part of your trip. Expect 20 min of slow traffic.',
                  trafficLevel: idx === 1 ? ('light' as const) : ('heavy' as const),
                },
                {
                  time: departTime.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  }),
                  type: 'depart' as const,
                  location: wp.name,
                },
              ];
            }),
          },
        ],
      },
    };

    saveTrip(trip);
    setIsOptimizing(false);
    navigate(`/route/${tripId}`);
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
