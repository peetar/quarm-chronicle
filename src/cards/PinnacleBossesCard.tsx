import React from 'react';
import { CardProps } from '../types/cards';
import { BossKillEvent } from '../types/events';

const PINNACLE_DEFS = [
  { name: 'Lord Nagafen', era: 'Classic', id: 32040 },
  { name: 'Lady Vox', era: 'Classic', id: 73057 },
  { name: 'Phara Dar', era: 'Kunark', id: 108510 },
  { name: 'The Avatar of War', era: 'Velious', id: 113244 },
  { name: 'Tunare', era: 'Velious', id: 127002 },
  { name: 'Vulak`Aerr', era: 'Velious', id: 124128 },
  { name: 'Aten Ha Ra', era: 'Luclin', id: 158436 },
];

export const PinnacleBossesCard: React.FC<CardProps> = ({ data, className = '' }) => {
  const { events } = data;
  const l1Pinnacles = events.level1.filter((e) => e.type === 'pinnacle_first') as any[];
  const allBossKills = events.level3.filter((e): e is BossKillEvent => e.type === 'raid_boss_kill' || e.type === 'pvp_boss_kill');

  const killsByBoss: Record<string, number> = {};
  allBossKills.forEach((k) => {
    killsByBoss[k.boss.toLowerCase()] = (killsByBoss[k.boss.toLowerCase()] || 0) + 1;
  });

  return (
    <div className={`bg-slate-900/50 border border-slate-700/60 rounded-lg p-4 backdrop-blur-sm ${className}`}>
      <div className="text-sm font-bold tracking-wider uppercase text-gold-soft mb-3 flex items-center gap-2">
        <span>👑</span> Pinnacle Raid Bosses (First Kills)
      </div>
      <ul className="divide-y divide-white/5 text-sm">
        {PINNACLE_DEFS.map((p) => {
          const first = l1Pinnacles.find((f) => f.boss.toLowerCase() === p.name.toLowerCase() || f.boss.toLowerCase().includes(p.name.toLowerCase()));
          const count = killsByBoss[p.name.toLowerCase()] || (first ? 1 : 0);
          const url = first?.url || (p.id ? `https://www.pqdi.cc/npc/${p.id}` : null);

          return (
            <li key={p.name} className="py-1.5 flex justify-between items-center">
              <span className="text-slate-100 flex items-center gap-1.5">
                <span className={first ? 'text-gold' : 'text-slate-600'}>★</span>
                {url ? (
                  <a
                    href={url}
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-cyan border-b border-dashed border-gold/40 hover:border-cyan transition-colors"
                  >
                    {p.name} ({p.era})
                  </a>
                ) : (
                  <span>{p.name} ({p.era})</span>
                )}
              </span>
              <span className="font-semibold text-xs md:text-sm">
                {first ? (
                  <span className="text-gold-soft">
                    {first.date} {count > 1 ? `(${count} Kills)` : '(1 Kill)'}
                  </span>
                ) : (
                  <span className="text-slate-500 font-normal italic">Undefeated</span>
                )}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
};
