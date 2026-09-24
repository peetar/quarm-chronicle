import React from 'react';
import { CardProps } from '../types/cards';

export const MortalityNemesisCard: React.FC<CardProps> = ({ data, className = '' }) => {
  const { aggregates } = data;
  const topKillers = aggregates.topSlainKillers.slice(0, 5);

  return (
    <div className={`bg-slate-900/50 border border-slate-700/60 rounded-lg p-4 backdrop-blur-sm ${className}`}>
      <div className="text-sm font-bold tracking-wider uppercase text-crimson mb-3 flex items-center justify-between">
        <span className="flex items-center gap-2">
          <span>☠️</span> Mortality & Nemesis
        </span>
        <span className="text-xs font-normal text-slate-400 lowercase">
          ({aggregates.totalDeaths} total deaths)
        </span>
      </div>
      <ul className="divide-y divide-white/5 text-sm">
        {topKillers.map((k, idx) => (
          <li key={k.killer} className="py-1.5 flex justify-between items-center">
            <span className="text-slate-100 truncate pr-2 flex items-center gap-1.5">
              {idx === 0 && <span className="text-crimson font-bold text-xs">👑 Nemesis:</span>}
              <span>{k.killer}</span>
            </span>
            <span className="font-bold text-crimson text-xs md:text-sm whitespace-nowrap">
              {k.count} {k.count === 1 ? 'death' : 'deaths'}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};
