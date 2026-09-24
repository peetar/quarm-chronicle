import React from 'react';
import { CardProps } from '../types/cards';

export const MilestonesCard: React.FC<CardProps> = ({ data, className = '' }) => {
  const { eras, events } = data;

  const epicEvent = events.level1.find((e) => e.type === 'epic_acquired') as any;
  const ding60 = events.level1.find((e) => e.type === 'level_ding' && (e as any).dingLevel === 60) as any;

  return (
    <div className={`bg-slate-900/50 border border-slate-700/60 rounded-lg p-4 backdrop-blur-sm ${className}`}>
      <div className="text-sm font-bold tracking-wider uppercase text-gold-soft mb-3 flex items-center gap-2">
        <span>🏆</span> Milestones & Expansion Firsts
      </div>
      <div className="divide-y divide-white/5 text-xs md:text-sm">
        {epicEvent && (
          <div className="py-2 flex justify-between items-center">
            <span className="text-gold-soft font-semibold flex items-center gap-1.5">
              <span>✨</span> {epicEvent.title} (Epic 1.0)
            </span>
            <span className="text-slate-400">{epicEvent.date}</span>
            <span className="text-cyan font-medium">{epicEvent.zone}</span>
          </div>
        )}

        {ding60 && (
          <div className="py-2 flex justify-between items-center">
            <span className="text-gold-soft font-semibold flex items-center gap-1.5">
              <span>★</span> Ding 60 (Max Level Milestone)
            </span>
            <span className="text-slate-400">{ding60.date}</span>
            <span className="text-cyan font-medium">{ding60.zone}</span>
          </div>
        )}

        {events.level1
          .filter((e) => e.type === 'class_aa_learn')
          .map((aa: any, i: number) => (
            <div key={`maa-${i}`} className="py-2 flex justify-between items-center">
              <span className="text-indigo-300 font-semibold flex items-center gap-1.5 truncate pr-2">
                <span>🔮</span> {aa.title}
              </span>
              <span className="text-slate-400 whitespace-nowrap">{aa.date}</span>
              <span className="text-cyan font-medium whitespace-nowrap pl-2">{aa.zone}</span>
            </div>
          ))}

        {eras.map((era) => (
          <div key={era.era} className="py-2 flex justify-between items-center">
            <span className="text-slate-200 flex items-center gap-1.5">
              <span className="text-gold">★</span> First {era.era} Footstep
            </span>
            <span className="text-slate-400">{era.date}</span>
            <span className="text-cyan font-medium">{era.zone}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
