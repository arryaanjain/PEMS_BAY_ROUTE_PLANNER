// WaypointInput component - add new waypoints with autocomplete

import { useState, useEffect, useRef } from 'react';
import { Plus, MapPin, AlertCircle } from 'lucide-react';
import { Button } from './Button';
import { autocompleteLocation, validateLocation } from '../services/api';
import type { Waypoint } from '../types';

interface WaypointInputProps {
  onAdd: (waypoint: Waypoint) => void;
}

export function WaypointInput({ onAdd }: WaypointInputProps) {
  const [value, setValue] = useState('');
  const [suggestions, setSuggestions] = useState<Waypoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Debounced autocomplete
  useEffect(() => {
    if (value.length < 2) {
      setSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      setError(null);
      try {
        const results = await autocompleteLocation(value);
        setSuggestions(results);
        setShowSuggestions(true);
      } catch (err) {
        console.error('Autocomplete error:', err);
        setError('Failed to load suggestions');
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [value]);

  const handleSelectSuggestion = async (suggestion: Waypoint) => {
    try {
      // Validate that location is in PEMS Bay region
      const validation = await validateLocation(suggestion.name, {
        lat: suggestion.lat,
        lng: suggestion.lng,
      });

      if (!validation.valid) {
        setError(validation.message || 'This location is not in the PEMS Bay region');
        return;
      }

      // Use the validated location data if available, otherwise use the suggestion
      const locationToAdd = validation.location || suggestion;
      onAdd(locationToAdd);
      setValue('');
      setSuggestions([]);
      setShowSuggestions(false);
      setError(null);
    } catch (err) {
      console.error('Validation error:', err);
      setError('Failed to validate location. Please try again.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!value.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      // Validate location is in PEMS Bay
      const validation = await validateLocation(value.trim());
      
      if (!validation.valid) {
        setError('⚠️ Location must be within the PEMS Bay region');
        setIsLoading(false);
        return;
      }

      if (validation.location) {
        onAdd(validation.location);
        setValue('');
        setSuggestions([]);
        setShowSuggestions(false);
      }
    } catch (err) {
      setError('Failed to add location. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (inputRef.current && !inputRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={inputRef}>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1 relative">
          <input
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
            placeholder="Add a location in PEMS Bay region..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          
          {/* Autocomplete Dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion.id}
                  type="button"
                  onClick={() => handleSelectSuggestion(suggestion)}
                  className="w-full px-4 py-2 text-left hover:bg-blue-50 flex items-start gap-2 border-b last:border-b-0"
                >
                  <MapPin className="w-4 h-4 mt-1 text-blue-600 shrink-0" />
                  <div>
                    <div className="font-medium text-gray-900">{suggestion.name}</div>
                    <div className="text-xs text-gray-500">
                      {suggestion.lat.toFixed(4)}, {suggestion.lng.toFixed(4)}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <Button type="submit" size="md" className="flex items-center gap-2" isLoading={isLoading}>
          <Plus className="w-5 h-5" />
          Add
        </Button>
      </form>

      {/* Error Message */}
      {error && (
        <div className="mt-2 flex items-start gap-2 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Info Message */}
      <div className="mt-2 text-xs text-gray-500">
        <MapPin className="w-3 h-3 inline mr-1" />
        Only locations within the PEMS Bay region can be added
      </div>
    </div>
  );
}

