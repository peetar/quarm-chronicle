import React from 'react';
import { CardProps } from '../types/cards';

export const TopRaidKillsCard: React.FC<CardProps> = ({ data, className = '' }) => {
  const { aggregates } = data;
  const topBosses = aggregates.topRaidBossesDefeated.slice(0, 7);

  return (
    <div className={`bg-slate-900/50 border border-slate-700/60 rounded-lg p-4 backdrop-blur-sm ${className}`}>
      <div className="text-sm font-bold tracking-wider uppercase text-cyan mb-3 flex items-center gap-2">
        <span>⚔️</span> Top Raid Boss Total Kills
      </div>
      <ul className="divide-y divide-white/5 text-sm">
        {topBosses.map((b) => {
          const url = b.id ? `https://www.pqdi.cc/npc/${b.id}` : null;
          return (
            <li key={b.boss} className="py-1.5 flex justify-between items-center">
              <span className="text-slate-100 truncate pr-2">
                {url ? (
                  <a
                    href={url}
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-cyan border-b border-dashed border-cyan/40 hover:border-cyan transition-colors"
                  >
                    {b.boss}
                  </a>
                ) : (
                  <span>{b.boss}</span>
                )}
              </span>
              <span className="font-bold text-cyan text-xs md:text-sm whitespace-nowrap">
                {b.count} {b.count === 1 ? 'kill' : 'kills'}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
};
