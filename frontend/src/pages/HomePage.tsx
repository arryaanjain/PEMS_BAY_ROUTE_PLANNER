// Home page - displays list of saved trips

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Trip } from '../types';
import { getTrips } from '../utils/storage';
import { Header } from '../components/Header';
import { TripCard } from '../components/TripCard';
import { FAB } from '../components/FAB';
import { MapIcon } from 'lucide-react';

export function HomePage() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    setTrips(getTrips());
  }, []);

  const handleTripClick = (tripId: string) => {
    navigate(`/route/${tripId}`);
  };

  const handleNewTrip = () => {
    navigate('/plan');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header title="My Trips" />
      
      <main className="container mx-auto px-4 py-6">
        {trips.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="bg-blue-100 rounded-full p-6 mb-4">
              <MapIcon className="w-16 h-16 text-blue-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">No trips yet</h2>
            <p className="text-gray-600 mb-6 max-w-md">
              Start planning your first optimized route by tapping the + button below
            </p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {trips.map((trip) => (
              <TripCard
                key={trip.id}
                trip={trip}
                onClick={() => handleTripClick(trip.id)}
              />
            ))}
          </div>
        )}
      </main>

      <FAB onClick={handleNewTrip} />
    </div>
  );
}
