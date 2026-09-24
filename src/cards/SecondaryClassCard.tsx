import React from 'react';
import { CardProps } from '../types/cards';

export const SecondaryClassCard: React.FC<CardProps> = ({ data, className = '' }) => {
  const { character, aggregates } = data;
  const cls = character.characterClass.toLowerCase();

  let title = '🗡️ Secondary Class Utility';
  let color = 'text-cyan';

  if (cls === 'cleric') {
    title = '🗡️ Blessed Combat & Crowd Control';
  } else if (cls === 'bard') {
    title = '🛡️ Bardic Utility & Battle Control';
    color = 'text-gold-soft';
  } else if (cls === 'enchanter') {
    title = '⚡ Crowd Control & AE Stunning';
  } else if (cls === 'necromancer') {
    title = '🩸 Lifetaps & Pet Management';
    color = 'text-purple';
  } else if (cls === 'wizard') {
    title = '❄️ Cryomancy & Tactical Concussion';
    color = 'text-sky-300';
  } else if (cls === 'magician') {
    title = '🔥 Elemental Shields & Reagents';
    color = 'text-amber-300';
  } else if (cls === 'druid') {
    title = '🌪️ Portals & Environmental Rains';
    color = 'text-emerald-300';
  } else if (cls === 'shaman') {
    title = '🦎 Malo Debuffs & Celerity';
    color = 'text-teal-300';
  } else if (cls === 'paladin') {
    title = '🛡️ Holy Armor & Healing Hands';
    color = 'text-yellow-200';
  } else if (cls === 'shadow knight' || cls === 'shadowknight') {
    title = '💀 Dread Magic & Dark Armor';
    color = 'text-rose-300';
  } else if (cls === 'ranger') {
    title = '🌿 Track, Snare & Woodland Spells';
    color = 'text-emerald-200';
  } else if (cls === 'monk') {
    title = '🥋 Feign Death & Chi Discipline';
    color = 'text-orange-300';
  } else if (cls === 'rogue') {
    title = '🗡️ Stealth, Lockpicking & Poison';
    color = 'text-red-300';
  } else if (cls === 'warrior') {
    title = '⚔️ Battle Disciplines & Fortitude';
    color = 'text-slate-300';
  } else if (cls === 'beastlord') {
    title = '🐾 Spirit Ferocity & Warders';
    color = 'text-yellow-400';
  }

  // Pick spells starting after the first 6 (so no overlap with primary mastery)
  const secondarySpells = aggregates.topSpellsCast.slice(6, 12);

  return (
    <div className={`bg-slate-900/50 border border-slate-700/60 rounded-lg p-4 backdrop-blur-sm ${className}`}>
      <div className={`text-sm font-bold tracking-wider uppercase mb-3 flex items-center gap-2 ${color}`}>
        {title}
      </div>
      <ul className="divide-y divide-white/5 text-sm">
        {secondarySpells.length > 0 ? (
          secondarySpells.map((s) => (
            <li key={s.spell} className="py-1.5 flex justify-between items-center">
              <span className="text-slate-100 truncate pr-2">{s.spell}</span>
              <span className={`font-bold text-xs md:text-sm whitespace-nowrap ${color}`}>
                {s.count.toLocaleString()} {cls === 'bard' ? 'pulses' : 'casts'}
              </span>
            </li>
          ))
        ) : (
          <li className="py-2 text-slate-500 italic text-xs">Standard combat discipline and utility abilities.</li>
        )}
      </ul>
    </div>
  );
};
