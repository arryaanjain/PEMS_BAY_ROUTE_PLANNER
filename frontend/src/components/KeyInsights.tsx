// KeyInsights component - summary of route optimization results

import { Clock, CalendarClock, TrendingUp } from 'lucide-react';
import { Card } from './Card';
import type { OptimizedRoute } from '../types';

interface KeyInsightsProps {
  route: OptimizedRoute;
}

export function KeyInsights({ route }: KeyInsightsProps) {
  return (
    <Card className="p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Key Insights</h2>
      
      <div className="grid gap-4 md:grid-cols-3">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <CalendarClock className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <p className="text-sm text-gray-600">Recommended Start</p>
            <p className="text-lg font-semibold text-gray-900">{route.recommendedStart}</p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="p-2 bg-green-100 rounded-lg">
            <Clock className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <p className="text-sm text-gray-600">Predicted Travel Time</p>
            <p className="text-lg font-semibold text-gray-900">{route.totalTime}</p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="p-2 bg-purple-100 rounded-lg">
            <TrendingUp className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <p className="text-sm text-gray-600">Route Status</p>
            <p className="text-lg font-semibold text-gray-900">Optimized</p>
          </div>
        </div>
      </div>
    </Card>
  );
}
