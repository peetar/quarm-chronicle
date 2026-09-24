import React, { useState, useEffect } from 'react';
import { ProjectorProps } from '../types/projectors';
import { CARD_REGISTRY } from '../cards/registry';
import { HeaderCard } from '../cards/HeaderCard';
import { TopStatsCard } from '../cards/TopStatsCard';
import { PinnacleBossesCard } from '../cards/PinnacleBossesCard';
import { TopRaidKillsCard } from '../cards/TopRaidKillsCard';
import { ClassMasteryCard } from '../cards/ClassMasteryCard';
import { AAPointsCard } from '../cards/AAPointsCard';
import { MortalityNemesisCard } from '../cards/MortalityNemesisCard';
import { SecondaryClassCard } from '../cards/SecondaryClassCard';
import { SocialCircleCard } from '../cards/SocialCircleCard';
import { MilestonesCard } from '../cards/MilestonesCard';
import { InteractiveTimelineCard } from '../cards/InteractiveTimelineCard';

export const SlideshowProjector: React.FC<ProjectorProps> = ({
  data,
  selectedCardIds,
  onBackToSelector,
}) => {
  // Only include cards that are selected
  const activeCards = CARD_REGISTRY.filter((c) => selectedCardIds.includes(c.id));
  const [currentIndex, setCurrentIndex] = useState(0);

  const total = activeCards.length;
  const currentCard = activeCards[currentIndex] || activeCards[0];

  const goPrev = () => setCurrentIndex((prev) => (prev > 0 ? prev - 1 : total - 1));
  const goNext = () => setCurrentIndex((prev) => (prev < total - 1 ? prev + 1 : 0));

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') goPrev();
      if (e.key === 'ArrowRight') goNext();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [total]);

  const renderCardContent = (id: string) => {
    switch (id) {
      case 'header':
        return <HeaderCard data={data} />;
      case 'top_stats':
        return <TopStatsCard data={data} />;
      case 'pinnacle_bosses':
        return <PinnacleBossesCard data={data} />;
      case 'top_raid_kills':
        return <TopRaidKillsCard data={data} />;
      case 'class_mastery':
        return <ClassMasteryCard data={data} />;
      case 'aa_points':
        return <AAPointsCard data={data} />;
      case 'mortality_nemesis':
        return <MortalityNemesisCard data={data} />;
      case 'secondary_class':
        return <SecondaryClassCard data={data} />;
      case 'social_circle':
        return <SocialCircleCard data={data} />;
      case 'milestones':
        return <MilestonesCard data={data} />;
      case 'interactive_timeline':
        return <InteractiveTimelineCard data={data} />;
      default:
        return null;
    }
  };

  if (total === 0) {
    return (
      <div className="text-center p-8 text-slate-400">
        No cards selected for this slideshow projection.
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4">
      {/* Top Navigation Bar */}
      <div className="flex flex-wrap justify-between items-center gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        <div className="flex items-center gap-2">
          {onBackToSelector && (
            <button
              onClick={onBackToSelector}
              className="text-xs px-3 py-1.5 rounded border border-slate-700 text-slate-300 hover:text-white hover:border-slate-500 transition-colors"
            >
              &larr; Back
            </button>
          )}
          <span className="text-xs text-gold-soft font-semibold">
            Card {currentIndex + 1} of {total}
          </span>
        </div>

        {/* Step Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={goPrev}
            className="text-xs px-3 py-1.5 rounded border border-slate-700 text-slate-300 hover:border-gold hover:text-gold-soft transition-colors flex items-center gap-1 font-semibold"
          >
            &larr; Prev
          </button>
          <button
            onClick={goNext}
            className="text-xs px-3 py-1.5 rounded border border-gold/70 bg-gold/10 text-gold-soft hover:bg-gold/20 transition-colors flex items-center gap-1 font-semibold shadow-gold-glow"
          >
            Next &rarr;
          </button>
        </div>
      </div>

      {/* Main Slide Card Stage */}
      <div className="bg-[#101522]/95 border-2 border-double border-gold/70 rounded-xl p-6 md:p-8 shadow-[0_20px_50px_rgba(0,0,0,0.8),0_0_30px_rgba(212,175,55,0.12)] relative min-h-[420px] flex flex-col justify-between">
        {/* Card Header info */}
        <div className="border-b border-slate-800 pb-3 mb-4 flex justify-between items-center text-xs">
          <div className="text-gold-soft font-bold uppercase tracking-wider flex items-center gap-1.5">
            <span>{currentCard.icon}</span>
            <span>{currentCard.title}</span>
          </div>
          <div className="text-slate-400 font-mono">
            Slide {currentIndex + 1} / {total} (use &larr; &rarr; keys)
          </div>
        </div>

        {/* Rendered Card Content */}
        <div className="flex-1 flex flex-col justify-center">
          {renderCardContent(currentCard.id)}
        </div>

        {/* Bottom Pagination Dots */}
        <div className="flex justify-center gap-1.5 pt-4 mt-4 border-t border-slate-800">
          {activeCards.map((c, i) => (
            <button
              key={c.id}
              onClick={() => setCurrentIndex(i)}
              title={c.shortTitle}
              className={`h-2 rounded-full transition-all ${
                i === currentIndex
                  ? 'w-6 bg-gold shadow-[0_0_8px_rgba(212,175,55,0.8)]'
                  : 'w-2 bg-slate-700 hover:bg-slate-500'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
