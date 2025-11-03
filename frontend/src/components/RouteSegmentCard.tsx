import { type RouteSegment } from '../types';
import { Clock, Navigation, AlertCircle } from 'lucide-react';

interface RouteSegmentCardProps {
  segment: RouteSegment;
  index: number;
}

export function RouteSegmentCard({ segment, index }: RouteSegmentCardProps) {
  const getTrafficColor = (condition: string) => {
    switch (condition) {
      case 'light':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'moderate':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'heavy':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getCongestionWidth = (score: number) => {
    return `${Math.min(score * 100, 100)}%`;
  };

  return (
    <div className="bg-white rounded-lg border-2 border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-semibold text-sm">
            {index + 1}
          </div>
          <div>
            <div className="font-medium text-gray-900">
              {segment.fromLocation.name} → {segment.toLocation.name}
            </div>
            <div className="text-sm text-gray-500 flex items-center gap-1 mt-0.5">
              <Clock size={14} />
              {segment.predictedTravelTime} min
            </div>
          </div>
        </div>
        
        <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getTrafficColor(segment.trafficCondition)}`}>
          {segment.trafficCondition.toUpperCase()}
        </span>
      </div>

      {/* Congestion Bar */}
      <div className="mb-3">
        <div className="flex justify-between text-xs text-gray-600 mb-1">
          <span>Congestion Level</span>
          <span>{(segment.congestionScore * 100).toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              segment.congestionScore < 0.3
                ? 'bg-green-500'
                : segment.congestionScore < 0.6
                ? 'bg-yellow-500'
                : 'bg-red-500'
            }`}
            style={{ width: getCongestionWidth(segment.congestionScore) }}
          />
        </div>
      </div>

      {/* Segment Details */}
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="flex items-start gap-2">
          <Navigation size={16} className="text-blue-500 mt-0.5" />
          <div>
            <div className="text-gray-500 text-xs">From</div>
            <div className="text-gray-900 font-medium">{segment.fromLocation.name}</div>
            <div className="text-gray-400 text-xs">
              {segment.fromLocation.lat.toFixed(4)}, {segment.fromLocation.lng.toFixed(4)}
            </div>
          </div>
        </div>
        
        <div className="flex items-start gap-2">
          <Navigation size={16} className="text-green-500 mt-0.5" />
          <div>
            <div className="text-gray-500 text-xs">To</div>
            <div className="text-gray-900 font-medium">{segment.toLocation.name}</div>
            <div className="text-gray-400 text-xs">
              {segment.toLocation.lat.toFixed(4)}, {segment.toLocation.lng.toFixed(4)}
            </div>
          </div>
        </div>
      </div>

      {/* Warning for heavy traffic */}
      {segment.trafficCondition === 'heavy' && (
        <div className="mt-3 flex items-center gap-2 text-sm text-red-600 bg-red-50 p-2 rounded">
          <AlertCircle size={16} />
          <span>Heavy congestion expected on this segment</span>
        </div>
      )}
    </div>
  );
}
