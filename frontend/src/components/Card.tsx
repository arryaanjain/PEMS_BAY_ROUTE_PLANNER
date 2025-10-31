// Reusable Card component

import { type ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

export function Card({ children, className = '', onClick }: CardProps) {
  const baseStyles = 'bg-white rounded-xl shadow-md';
  const interactiveStyles = onClick ? 'cursor-pointer hover:shadow-lg transition-shadow duration-200' : '';

  return (
    <div className={`${baseStyles} ${interactiveStyles} ${className}`} onClick={onClick}>
      {children}
    </div>
  );
}
