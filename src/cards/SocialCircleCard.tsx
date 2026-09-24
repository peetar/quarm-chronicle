import React from 'react';
import { CardProps } from '../types/cards';

export const SocialCircleCard: React.FC<CardProps> = ({ data, className = '' }) => {
  const { aggregates, character, events } = data;
  const topTells = aggregates.topTellPartners.slice(0, 5);
  const topGroup = aggregates.topGroupCompanions.slice(0, 4);
  const topRaid = aggregates.topRaidCompanions.slice(0, 4);

  // Guild history
  const guildEvents = events.level1.filter((e) => e.type === 'guild_join' || e.type === 'guild_leave') as any[];
  const guildNames = guildEvents.filter((g) => g.action === 'joined').map((g) => g.guild);
  const uniqueGuilds = Array.from(new Set([...guildNames, character.guild]));

  return (
    <div className={`bg-slate-900/50 border border-slate-700/60 rounded-lg p-4 backdrop-blur-sm ${className}`}>
      <div className="text-sm font-bold tracking-wider uppercase text-cyan mb-3 flex items-center gap-2">
        <span>💬</span> Companions in Arms & Social Circle
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs md:text-sm">
        <div>
          <div className="font-semibold text-gold-soft mb-1.5">Direct Tell Partners:</div>
          <ul className="space-y-1 text-slate-300">
            {topTells.length > 0 ? (
              topTells.map((t) => (
                <li key={t.partner} className="flex justify-between items-center pr-2">
                  <span>• {t.partner}</span>
                  <span className="text-slate-400 font-mono text-xs">
                    {t.total} tells ({t.sent} sent / {t.received} recv)
                  </span>
                </li>
              ))
            ) : (
              <li className="text-slate-500 italic">No direct tell records found.</li>
            )}
          </ul>
          {topGroup.length > 0 && (
            <div className="mt-3">
              <div className="font-semibold text-gold-soft mb-1">Top Group Chat Companions:</div>
              <div className="text-slate-400 text-xs leading-relaxed">
                {topGroup.map((c) => `${c.companion} (${c.count})`).join(' • ')}
              </div>
            </div>
          )}
        </div>

        <div>
          <div className="font-semibold text-gold-soft mb-1.5">Guild Journey:</div>
          <div className="text-slate-300 text-xs mb-3">
            {uniqueGuilds.join(' → ')}
          </div>
          <div className="font-semibold text-cyan mb-1.5">Active Guild:</div>
          <div className="text-slate-200 text-xs md:text-sm flex items-center gap-1.5">
            <span>🛡️</span> &lt;{character.guild}&gt;
          </div>
          {topRaid.length > 0 && (
            <div className="mt-3">
              <div className="font-semibold text-gold-soft mb-1">Top Raid Chat Companions:</div>
              <div className="text-slate-400 text-xs leading-relaxed">
                {topRaid.map((c) => `${c.companion} (${c.count})`).join(' • ')}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
