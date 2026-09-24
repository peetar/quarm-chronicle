import React, { useRef } from 'react';
import { ProjectorProps } from '../types/projectors';
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
import html2canvas from 'html2canvas';

export const SummaryProjector: React.FC<ProjectorProps> = ({
  data,
  selectedCardIds,
  onBackToSelector,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  const isSelected = (id: string) => selectedCardIds.includes(id);

  const copyAsImage = async () => {
    if (!containerRef.current) return;
    try {
      const canvas = await html2canvas(containerRef.current, {
        backgroundColor: '#080a0f',
        scale: 2,
        useCORS: true,
      });
      canvas.toBlob(async (blob) => {
        if (!blob) return;
        await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
        alert('Summary Card copied to clipboard!');
      }, 'image/png');
    } catch (err: any) {
      alert(`Clipboard copy failed: ${err.message}`);
    }
  };

  const downloadStandaloneHtml = () => {
    if (!containerRef.current) return;
    const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Project Quarm Chronicle - ${data.character.name}</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
  :root {
    --gold: #d4af37;
    --gold-soft: #f3df8a;
    --cyan: #38bdf8;
    --crimson: #f87171;
    --emerald: #4ade80;
    --purple: #c084fc;
  }
</style>
</head>
<body class="bg-[#080a0f] text-slate-100 min-h-screen p-4 md:p-8 flex justify-center items-center">
  <div class="w-full max-w-[980px]">
    ${containerRef.current.outerHTML}
  </div>
</body>
</html>`;

    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${data.character.name.toLowerCase()}_chronicle_summary.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-4">
      {/* Top Action Bar */}
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
            Chronicle Dashboard
          </span>
        </div>

        <div className="flex gap-2">
          <button
            onClick={copyAsImage}
            className="text-xs px-3 py-1.5 rounded border border-gold text-gold-soft hover:bg-gold/10 font-semibold transition-colors"
          >
            📋 Copy Image
          </button>
          <button
            onClick={downloadStandaloneHtml}
            className="text-xs px-3 py-1.5 rounded border border-cyan text-cyan hover:bg-cyan/10 font-semibold transition-colors"
          >
            💾 Download HTML
          </button>
        </div>
      </div>

      {/* Main Chronicle Card Surface (Matches the original thebrain_card.html layout) */}
      <div
        ref={containerRef}
        className="w-full bg-[#101522]/95 border-[3px] border-double border-gold rounded-xl p-6 md:p-9 shadow-[0_20px_50px_rgba(0,0,0,0.8),0_0_35px_rgba(212,175,55,0.15)] relative backdrop-blur-md"
      >
        {/* Corner Ornaments */}
        <div className="absolute top-2 left-2 w-4 h-4 border-t-2 border-l-2 border-gold pointer-events-none" />
        <div className="absolute top-2 right-2 w-4 h-4 border-t-2 border-r-2 border-gold pointer-events-none" />
        <div className="absolute bottom-2 left-2 w-4 h-4 border-b-2 border-l-2 border-gold pointer-events-none" />
        <div className="absolute bottom-2 right-2 w-4 h-4 border-b-2 border-r-2 border-gold pointer-events-none" />

        {/* 1. Header Card */}
        {isSelected('header') && <HeaderCard data={data} />}

        {/* 2. Top Stats Card */}
        {isSelected('top_stats') && <TopStatsCard data={data} />}

        {/* 3. Split Grid: Section 1 (Pinnacles & Top Raid Kills) */}
        {(isSelected('pinnacle_bosses') || isSelected('top_raid_kills')) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {isSelected('pinnacle_bosses') && <PinnacleBossesCard data={data} />}
            {isSelected('top_raid_kills') && <TopRaidKillsCard data={data} />}
          </div>
        )}

        {/* 4. Split Grid: Section 2 (Class Mastery & AA Points) */}
        {(isSelected('class_mastery') || isSelected('aa_points')) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {isSelected('class_mastery') && <ClassMasteryCard data={data} />}
            {isSelected('aa_points') && <AAPointsCard data={data} />}
          </div>
        )}

        {/* 5. Split Grid: Section 3 (Mortality/Nemesis & Secondary Utility) */}
        {(isSelected('mortality_nemesis') || isSelected('secondary_class')) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {isSelected('mortality_nemesis') && <MortalityNemesisCard data={data} />}
            {isSelected('secondary_class') && <SecondaryClassCard data={data} />}
          </div>
        )}

        {/* 6. Wide Card: Social & Companions */}
        {isSelected('social_circle') && <SocialCircleCard data={data} className="mb-4" />}

        {/* 7. Wide Card: Milestones & Expansion Firsts */}
        {isSelected('milestones') && <MilestonesCard data={data} className="mb-4" />}

        {/* 8. Interactive Timeline Card (if selected) */}
        {isSelected('interactive_timeline') && <InteractiveTimelineCard data={data} className="mt-6" />}

        <footer className="text-center mt-6 pt-4 border-t border-slate-700/40 text-xs text-slate-500 tracking-wider">
          Project Quarm Chronicle • Client Logs from TAKP • Generated with Web App
        </footer>
      </div>
    </div>
  );
};
