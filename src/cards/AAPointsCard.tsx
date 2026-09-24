import React from 'react';
import { CardProps } from '../types/cards';

export const AAPointsCard: React.FC<CardProps> = ({ data, className = '' }) => {
  const { aggregates } = data;
  const topZones = aggregates.aaByZone.slice(0, 6);

  return (
    <div className={`bg-slate-900/50 border border-slate-700/60 rounded-lg p-4 backdrop-blur-sm ${className}`}>
      <div className="text-sm font-bold tracking-wider uppercase text-gold-soft mb-3 flex items-center justify-between">
        <span className="flex items-center gap-2">
          <span>🌟</span> AA Points by Zone
        </span>
        <span className="text-xs font-normal text-slate-400 lowercase">
          ({aggregates.totalAAs} total AAs)
        </span>
      </div>
      <ul className="divide-y divide-white/5 text-sm">
        {topZones.map((z) => (
          <li key={z.zone} className="py-1.5 flex justify-between items-center">
            <span className="text-slate-100 truncate pr-2">{z.zone}</span>
            <span className="font-bold text-gold-soft text-xs md:text-sm whitespace-nowrap">
              {z.count} AAs
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};
