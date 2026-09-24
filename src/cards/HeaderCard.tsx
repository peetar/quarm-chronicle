import React from 'react';
import { CardProps } from '../types/cards';

export const HeaderCard: React.FC<CardProps> = ({ data, className = '' }) => {
  const { character } = data;
  return (
    <header className={`text-center border-b border-gold/30 pb-5 mb-6 relative ${className}`}>
      <div className="text-gold-soft text-xs md:text-sm uppercase tracking-[3px] font-bold">
        Project Quarm Chronicle
      </div>
      <h1 className="text-3xl md:text-5xl font-serif text-white font-bold my-2 tracking-wider drop-shadow-[0_0_15px_rgba(212,175,55,0.4)]">
        {character.name.toUpperCase()}{character.lastName ? ` ${character.lastName.toUpperCase()}` : ''}
      </h1>
      <div className="text-cyan text-base md:text-lg font-semibold">
        Level {character.level} {character.characterRace ? `${character.characterRace} ` : ''}{character.characterClass} • &lt;{character.guild}&gt;
      </div>
      <div className="text-slate-400 text-xs md:text-sm mt-1">
        {character.dateRange.start} — {character.dateRange.end} • Norrathian Career Chronicle ({character.totalLogLines.toLocaleString()} log lines)
      </div>
    </header>
  );
};
