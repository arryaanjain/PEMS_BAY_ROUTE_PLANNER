// ItineraryView component - detailed step-by-step breakdown

import { ArrowRight, MapPin } from 'lucide-react';
import { Card } from './Card';
import type { ItineraryDay } from '../types';

interface ItineraryViewProps {
  itinerary: ItineraryDay[];
}

export function ItineraryView({ itinerary }: ItineraryViewProps) {
  const trafficColors = {
    light: 'text-green-600 bg-green-50',
    moderate: 'text-yellow-600 bg-yellow-50',
    heavy: 'text-red-600 bg-red-50',
  };

  return (
    <Card className="p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Itinerary</h2>

      <div className="space-y-6">
        {itinerary.map((day) => (
          <div key={day.day}>
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white text-sm">
                {day.day}
              </span>
              Day {day.day} - {day.date}
            </h3>

            <div className="ml-4 border-l-2 border-gray-200 pl-6 space-y-4">
              {day.stops.map((stop, idx) => (
                <div key={idx} className="relative">
                  {/* Timeline dot */}
                  <div className="absolute -left-[28px] top-1 w-4 h-4 rounded-full bg-blue-600 border-2 border-white"></div>

                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-gray-900">
                        {stop.time}
                      </span>
                      {stop.type === 'arrive' ? (
                        <ArrowRight className="w-4 h-4 text-green-600" />
                      ) : (
                        <MapPin className="w-4 h-4 text-blue-600" />
                      )}
                      <span className="text-sm font-medium text-gray-700">
                        {stop.type === 'arrive' ? 'Arrive at' : 'Depart from'}{' '}
                        <span className="font-semibold">{stop.location}</span>
                      </span>
                    </div>

                    {stop.insight && (
                      <div className="flex items-start gap-2 mt-2">
                        <div
                          className={`px-3 py-1.5 rounded-lg text-xs ${
                            stop.trafficLevel
                              ? trafficColors[stop.trafficLevel]
                              : 'bg-gray-50 text-gray-600'
                          }`}
                        >
                          <em>{stop.insight}</em>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
