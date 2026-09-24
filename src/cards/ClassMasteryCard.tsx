import React from 'react';
import { CardProps } from '../types/cards';

export const ClassMasteryCard: React.FC<CardProps> = ({ data, className = '' }) => {
  const { character, aggregates } = data;
  const cls = character.characterClass.toLowerCase();

  let headerTitle = '✨ Signature Class Abilities';
  let headerColor = 'text-cyan';

  if (cls === 'cleric') {
    headerTitle = '🕊️ Holy Liturgy & Healing';
    headerColor = 'text-emerald';
  } else if (cls === 'bard') {
    headerTitle = '🎵 Melodic Twisting & Songs';
    headerColor = 'text-purple';
  } else if (cls === 'enchanter') {
    headerTitle = '🔮 Mind Control & Mana Weaving';
    headerColor = 'text-cyan';
  } else if (cls === 'necromancer') {
    headerTitle = '💀 Dark Arts & Rotting Magic';
    headerColor = 'text-crimson';
  } else if (cls === 'wizard') {
    headerTitle = '🔥 Evocation & Pure Destruction';
    headerColor = 'text-amber-400';
  } else if (cls === 'magician') {
    headerTitle = '⚡ Conjuration & Elemental Power';
    headerColor = 'text-sky-400';
  } else if (cls === 'druid') {
    headerTitle = '🌿 Nature Magic & Restoration';
    headerColor = 'text-emerald-400';
  } else if (cls === 'shaman') {
    headerTitle = '🐺 Spirit Alchemy & Totemic Buffs';
    headerColor = 'text-teal-400';
  } else if (cls === 'paladin') {
    headerTitle = '⚔️ Holy Crusades & Divine Radiance';
    headerColor = 'text-yellow-300';
  } else if (cls === 'shadow knight' || cls === 'shadowknight') {
    headerTitle = '🗡️ Blood & Dark Tendrils';
    headerColor = 'text-rose-400';
  } else if (cls === 'ranger') {
    headerTitle = '🏹 Woodland Mastery & Bowcraft';
    headerColor = 'text-emerald-300';
  } else if (cls === 'monk') {
    headerTitle = '🥋 Martial Arts & Bare-Hand Combat';
    headerColor = 'text-orange-400';
  } else if (cls === 'rogue') {
    headerTitle = '🗡️ Backstabbing & Poison Arts';
    headerColor = 'text-red-400';
  } else if (cls === 'warrior') {
    headerTitle = '🛡️ Battle Taunts & Frontline Armor';
    headerColor = 'text-slate-300';
  } else if (cls === 'beastlord') {
    headerTitle = '🐾 Primal Bond & Savage Combat';
    headerColor = 'text-yellow-500';
  }

  const topSpells = aggregates.topSpellsCast.slice(0, 6);

  return (
    <div className={`bg-slate-900/50 border border-slate-700/60 rounded-lg p-4 backdrop-blur-sm ${className}`}>
      <div className={`text-sm font-bold tracking-wider uppercase mb-3 flex items-center gap-2 ${headerColor}`}>
        {headerTitle}
      </div>
      <ul className="divide-y divide-white/5 text-sm">
        {topSpells.length > 0 ? (
          topSpells.map((s) => (
            <li key={s.spell} className="py-1.5 flex justify-between items-center">
              <span className="text-slate-100 truncate pr-2">{s.spell}</span>
              <span className={`font-bold text-xs md:text-sm whitespace-nowrap ${headerColor}`}>
                {s.count.toLocaleString()} casts
              </span>
            </li>
          ))
        ) : (
          <li className="py-2 text-slate-400 italic text-xs">
            Physical melee combat disciplines and martial mastery.
          </li>
        )}
      </ul>
    </div>
  );
};
