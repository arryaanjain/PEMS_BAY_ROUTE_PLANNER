import { type OptimizedRoute, type Waypoint } from '../types';
import { Clock, Calendar, TrendingUp, MapPin, AlertTriangle } from 'lucide-react';

interface RouteOverviewProps {
  optimizedRoute: OptimizedRoute;
  originalWaypoints: Waypoint[];
}

export function RouteOverview({ optimizedRoute, originalWaypoints }: RouteOverviewProps) {
  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const formatDateTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const getOptimizedWaypoints = () => {
    return optimizedRoute.optimizedOrder.map(index => originalWaypoints[index]);
  };

  const orderedWaypoints = getOptimizedWaypoints();

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-200">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Optimized Route</h2>
          <p className="text-gray-600">CNN-powered traffic prediction with {optimizedRoute.segments.length} segments</p>
        </div>
        
        <div className="bg-white rounded-lg px-4 py-2 border-2 border-green-300">
          <div className="text-xs text-gray-500 mb-1">Total Travel Time</div>
          <div className="text-2xl font-bold text-green-600">
            {formatTime(optimizedRoute.totalTravelTime)}
          </div>
        </div>
      </div>

      {/* Key Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2 text-gray-600 mb-2">
            <Calendar size={18} />
            <span className="text-sm font-medium">Start Time</span>
          </div>
          <div className="text-gray-900 font-semibold">
            {formatDateTime(optimizedRoute.recommendedStart)}
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2 text-gray-600 mb-2">
            <MapPin size={18} />
            <span className="text-sm font-medium">Total Stops</span>
          </div>
          <div className="text-gray-900 font-semibold text-2xl">
            {orderedWaypoints.length}
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2 text-gray-600 mb-2">
            <TrendingUp size={18} />
            <span className="text-sm font-medium">Route Days</span>
          </div>
          <div className="text-gray-900 font-semibold text-2xl">
            {optimizedRoute.itinerary.length}
          </div>
        </div>
      </div>

      {/* Optimized Order */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <TrendingUp size={18} className="text-blue-500" />
          Recommended Visit Order
        </h3>
        <div className="flex items-center gap-2 flex-wrap">
          {orderedWaypoints.map((waypoint, index) => (
            <div key={waypoint.id} className="flex items-center gap-2">
              <div className="flex items-center gap-2 bg-blue-50 border-2 border-blue-200 rounded-lg px-3 py-2">
                <span className="w-6 h-6 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </span>
                <span className="font-medium text-gray-900">{waypoint.name}</span>
              </div>
              {index < orderedWaypoints.length - 1 && (
                <span className="text-gray-400">→</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Warnings */}
      {optimizedRoute.insights.warnings.length > 0 && (
        <div className="mt-4 space-y-2">
          {optimizedRoute.insights.warnings.map((warning, index) => (
            <div
              key={index}
              className={`flex items-start gap-3 p-3 rounded-lg border-l-4 ${
                warning.severity === 'high'
                  ? 'bg-red-50 border-red-500'
                  : warning.severity === 'medium'
                  ? 'bg-yellow-50 border-yellow-500'
                  : 'bg-blue-50 border-blue-500'
              }`}
            >
              <AlertTriangle
                size={20}
                className={
                  warning.severity === 'high'
                    ? 'text-red-500'
                    : warning.severity === 'medium'
                    ? 'text-yellow-500'
                    : 'text-blue-500'
                }
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{warning.message}</p>
                {warning.location && (
                  <p className="text-xs text-gray-600 mt-1">Location: {warning.location}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Recommendations */}
      {optimizedRoute.insights.recommendations.length > 0 && (
        <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="font-semibold text-green-900 mb-2">💡 Recommendations</h4>
          <ul className="space-y-1">
            {optimizedRoute.insights.recommendations.map((rec: any, index: number) => (
              <li key={index} className="text-sm text-green-800">
                • {rec.message || JSON.stringify(rec)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
