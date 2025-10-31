// TimeSettings component - start time and duration picker

import { Calendar, Clock } from 'lucide-react';

interface TimeSettingsProps {
  startTime: string;
  duration: number;
  durationType: 'hours' | 'days';
  onStartTimeChange: (value: string) => void;
  onDurationChange: (value: number) => void;
  onDurationTypeChange: (type: 'hours' | 'days') => void;
}

export function TimeSettings({
  startTime,
  duration,
  durationType,
  onStartTimeChange,
  onDurationChange,
  onDurationTypeChange,
}: TimeSettingsProps) {
  return (
    <div className="space-y-4">
      <div>
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
          <Calendar className="w-4 h-4" />
          Start Time
        </label>
        <input
          type="datetime-local"
          value={startTime}
          onChange={(e) => onStartTimeChange(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div>
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
          <Clock className="w-4 h-4" />
          Trip Duration
        </label>
        <div className="flex gap-2">
          <input
            type="number"
            min="1"
            value={duration}
            onChange={(e) => onDurationChange(Number(e.target.value))}
            className="w-24 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <div className="flex rounded-lg border border-gray-300 overflow-hidden">
            <button
              type="button"
              onClick={() => onDurationTypeChange('hours')}
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                durationType === 'hours'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Hours
            </button>
            <button
              type="button"
              onClick={() => onDurationTypeChange('days')}
              className={`px-4 py-2 text-sm font-medium transition-colors border-l border-gray-300 ${
                durationType === 'days'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Days
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
