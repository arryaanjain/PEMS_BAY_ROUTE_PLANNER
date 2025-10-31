// TrafficWarning component - displays traffic alerts

import { AlertTriangle, AlertCircle, Info } from 'lucide-react';
import type { TrafficWarning as TrafficWarningType } from '../types';

interface TrafficWarningProps {
  warning: TrafficWarningType;
}

export function TrafficWarning({ warning }: TrafficWarningProps) {
  const severityConfig = {
    low: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-800',
      icon: Info,
    },
    medium: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      text: 'text-yellow-800',
      icon: AlertCircle,
    },
    high: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-800',
      icon: AlertTriangle,
    },
  };

  const config = severityConfig[warning.severity];
  const Icon = config.icon;

  return (
    <div className={`${config.bg} ${config.border} border-l-4 p-4 rounded-r-lg`}>
      <div className="flex gap-3">
        <Icon className={`w-5 h-5 ${config.text} flex-shrink-0 mt-0.5`} />
        <div className="flex-1">
          <p className={`font-semibold ${config.text}`}>
            {warning.severity === 'high' && '⚠️ '}
            {warning.severity === 'medium' && '⚡ '}
            {warning.message}
          </p>
        </div>
      </div>
    </div>
  );
}
