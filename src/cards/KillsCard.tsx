import React from 'react';
import { CardProps } from '../types/cards';

export const KillsCard: React.FC<CardProps> = ({ data, className = '' }) => {
  const { aggregates } = data;
  const totalKills = aggregates.totalKills ?? 0;
  const bossKillShots = aggregates.bossKillShots || [];
  const topSlainMobs = (aggregates.topSlainMobs || []).slice(0, 10);
  const totalKillShots = bossKillShots.reduce((acc, b) => acc + b.count, 0);

  return (
    <div className={`bg-slate-900/50 border border-slate-700/60 rounded-lg p-4 backdrop-blur-sm ${className}`}>
      {/* Header with Title & Stats Badges */}
      <div className="flex flex-wrap justify-between items-center gap-2 mb-3 border-b border-white/5 pb-2">
        <div className="text-sm font-bold tracking-wider uppercase text-gold-soft flex items-center gap-2">
          <span>🎯</span> Personal Kills & Boss Kill Shots
        </div>
        <div className="flex items-center gap-2">
          {totalKills > 0 && (
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              {totalKills.toLocaleString()} Total Kills
            </span>
          )}
          {totalKillShots > 0 && (
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-gold/20 text-gold-soft border border-gold/30">
              {totalKillShots} Boss Kill {totalKillShots === 1 ? 'Shot' : 'Shots'}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Personal Boss Kill Shots */}
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-cyan mb-2 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <span>👑</span> Boss Killing Blows ({bossKillShots.length})
            </span>
            <span className="text-[10px] text-slate-400 font-normal lowercase">final blows landed</span>
          </div>

          {bossKillShots.length > 0 ? (
            <div className="space-y-1.5 max-h-[360px] overflow-y-auto pr-1 text-sm custom-scrollbar">
              {bossKillShots.map((b) => {
                const url = b.url || (b.id ? `https://www.pqdi.cc/npc/${b.id}` : null);
                return (
                  <div
                    key={`${b.boss}-${b.lastTimestamp || ''}`}
                    className="p-2 rounded bg-slate-800/40 hover:bg-slate-800/70 border border-slate-700/40 flex justify-between items-center transition-colors"
                  >
                    <div className="min-w-0 pr-2">
                      <div className="text-slate-100 flex items-center gap-1.5 font-medium truncate">
                        {b.isPinnacle && (
                          <span className="text-gold text-xs" title="Pinnacle Encounter">
                            ★
                          </span>
                        )}
                        {url ? (
                          <a
                            href={url}
                            target="_blank"
                            rel="noreferrer"
                            className="hover:text-cyan border-b border-dashed border-gold/40 hover:border-cyan transition-colors truncate"
                          >
                            {b.boss}
                          </a>
                        ) : (
                          <span className="truncate">{b.boss}</span>
                        )}
                      </div>
                      <div className="text-[11px] text-slate-400 flex items-center gap-1.5 mt-0.5">
                        {b.zone && <span>{b.zone}</span>}
                        {b.zone && b.lastDate && <span>•</span>}
                        {b.lastDate && <span>{b.lastDate}</span>}
                        {b.hp && b.hp > 0 && (
                          <>
                            <span>•</span>
                            <span className="text-slate-500">{Math.round(b.hp / 1000)}k HP</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="shrink-0">
                      <span className="px-2 py-0.5 text-xs font-bold rounded bg-cyan/15 text-cyan border border-cyan/30 whitespace-nowrap">
                        {b.count} {b.count === 1 ? 'Kill Shot' : 'Kill Shots'}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-xs text-slate-500 italic py-6 text-center border border-dashed border-slate-800 rounded">
              No raid boss killing blows recorded.
            </div>
          )}
        </div>

        {/* Right Column: Top Slain Foes */}
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-2 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <span>🗡️</span> Top Slain Foes & Monsters
            </span>
            <span className="text-[10px] text-slate-400 font-normal lowercase">most frequent conquests</span>
          </div>

          {topSlainMobs.length > 0 ? (
            <ul className="divide-y divide-white/5 text-sm">
              {topSlainMobs.map((m, idx) => {
                const url = m.url || (m.id ? `https://www.pqdi.cc/npc/${m.id}` : null);
                return (
                  <li key={`${m.mob}-${idx}`} className="py-1.5 flex justify-between items-center">
                    <span className="text-slate-100 flex items-center gap-2 truncate pr-2">
                      <span className="text-xs font-semibold text-slate-500 w-5">#{idx + 1}</span>
                      {url ? (
                        <a
                          href={url}
                          target="_blank"
                          rel="noreferrer"
                          className="hover:text-emerald-300 border-b border-dashed border-emerald-500/40 hover:border-emerald-300 transition-colors truncate"
                        >
                          {m.mob}
                        </a>
                      ) : (
                        <span className="truncate">{m.mob}</span>
                      )}
                      {m.level && m.level > 0 && (
                        <span className="text-[10px] text-slate-400 bg-slate-800/80 px-1.5 py-0.2 rounded border border-slate-700/50">
                          lvl {m.level}
                        </span>
                      )}
                    </span>
                    <span className="font-bold text-emerald-400 text-xs md:text-sm whitespace-nowrap">
                      {m.count.toLocaleString()} {m.count === 1 ? 'kill' : 'kills'}
                    </span>
                  </li>
                );
              })}
            </ul>
          ) : (
            <div className="text-xs text-slate-500 italic py-6 text-center border border-dashed border-slate-800 rounded">
              No slain foes recorded.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
