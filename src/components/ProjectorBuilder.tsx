import React from 'react';
import { ParsedCharacterBundle } from '../types/events';
import { CARD_REGISTRY } from '../cards/registry';
import { ProjectorType } from '../types/projectors';

interface ProjectorBuilderProps {
  bundle: ParsedCharacterBundle;
  selectedCardIds: string[];
  onChangeSelectedCardIds: (ids: string[]) => void;
  onLaunchProjector: (type: ProjectorType) => void;
  onSwitchCharacter: () => void;
  onDeleteCharacter?: () => void;
  onRegenerateCards?: () => void;
  onReparseLog?: () => void;
}

export const ProjectorBuilder: React.FC<ProjectorBuilderProps> = ({
  bundle,
  selectedCardIds,
  onChangeSelectedCardIds,
  onLaunchProjector,
  onSwitchCharacter,
  onDeleteCharacter,
  onRegenerateCards,
  onReparseLog,
}) => {
  const { character, aggregates } = bundle;

  const toggleCard = (id: string) => {
    if (selectedCardIds.includes(id)) {
      onChangeSelectedCardIds(selectedCardIds.filter((c) => c !== id));
    } else {
      onChangeSelectedCardIds([...selectedCardIds, id]);
    }
  };

  const handleSelectAll = () => {
    onChangeSelectedCardIds(CARD_REGISTRY.map((c) => c.id));
  };

  const handleSelectDefault = () => {
    onChangeSelectedCardIds(CARD_REGISTRY.filter((c) => c.defaultSelected).map((c) => c.id));
  };

  const handleClearAll = () => {
    onChangeSelectedCardIds([]);
  };

  const handleExportJson = () => {
    const jsonStr = JSON.stringify(bundle, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${character.name.toLowerCase()}_quarm_bundle.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      {/* Character Profile Header Summary */}
      <div className="bg-[#101522]/90 border border-gold/50 rounded-xl p-6 shadow-card backdrop-blur-md flex flex-wrap justify-between items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <span className="text-3xl">⚔️</span>
            <div>
              <h2 className="text-2xl font-black text-gold tracking-wide">
                {character.name}
              </h2>
              <div className="text-xs text-slate-300 font-semibold mt-0.5">
                Level {character.level} {character.characterClass} &bull; &lt;{character.guild}&gt;
              </div>
            </div>
          </div>
          <div className="text-xs text-slate-400 mt-2 flex flex-wrap gap-x-4 gap-y-1">
            <span>📅 Career: <strong className="text-slate-200">{character.dateRange.start} &rarr; {character.dateRange.end}</strong></span>
            <span>📜 Lines: <strong className="text-cyan font-mono">{character.totalLogLines.toLocaleString()}</strong></span>
            <span>⚔️ Boss Kills: <strong className="text-gold-soft font-mono">{aggregates.totalBossKills}</strong></span>
            <span>🌟 AAs: <strong className="text-emerald-400 font-mono">{aggregates.totalAAs}</strong></span>
            <span>☠️ Deaths: <strong className="text-crimson font-mono">{aggregates.totalDeaths}</strong></span>
            {character.logFiles && character.logFiles.length > 1 && (
              <span
                className="cursor-help text-purple-300 bg-purple-950/50 border border-purple-800/60 px-2 py-0.5 rounded text-[11px]"
                title={character.logFiles.map((f) => `${f.fileName} (${f.sizeMb} MB) [${f.start} -> ${f.end}]`).join('\n')}
              >
                📚 Stitched: <strong className="text-purple-200 font-mono">{character.logFiles.length} logs</strong>
              </span>
            )}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Button 1: Regenerate all selected cards (with current data) */}
          <button
            onClick={() => {
              if (onRegenerateCards) {
                onRegenerateCards();
              } else if (selectedCardIds.length === 1 && selectedCardIds[0] === 'interactive_timeline') {
                onLaunchProjector('timeline');
              } else {
                onLaunchProjector('summary');
              }
            }}
            className="text-xs px-3.5 py-1.5 rounded-lg border border-gold bg-gold/20 text-gold-soft hover:bg-gold/30 font-bold transition-all shadow-gold-glow flex items-center gap-1.5"
            title="Regenerate all selected cards and timeline with current data"
          >
            <span>🔄</span> Regenerate Selected Cards
          </button>

          {/* Button 2: Reparse the log (and then regenerate tiles) */}
          {onReparseLog && (
            <button
              onClick={onReparseLog}
              className="text-xs px-3.5 py-1.5 rounded-lg border border-cyan/70 bg-cyan/15 text-cyan hover:bg-cyan/25 font-bold transition-all shadow-[0_0_12px_rgba(56,189,248,0.2)] flex items-center gap-1.5"
              title="Re-stream and parse the character log file from disk, then regenerate cards"
            >
              <span>⚡</span> Re-parse Log
            </button>
          )}

          <button
            onClick={handleExportJson}
            className="text-xs px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-900 text-slate-300 hover:text-white hover:border-slate-500 transition-colors flex items-center gap-1.5"
            title="Export parsed bundle JSON for offline archival"
          >
            <span>💾</span> Export JSON
          </button>
          <button
            onClick={onSwitchCharacter}
            className="text-xs px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-900 text-slate-300 hover:text-white hover:border-slate-500 transition-colors"
          >
            Switch Character
          </button>
          {onDeleteCharacter && (
            <button
              onClick={onDeleteCharacter}
              className="text-xs px-2.5 py-1.5 rounded-lg border border-red-900/60 bg-red-950/30 text-red-400 hover:bg-red-900/40 transition-colors"
              title="Delete cached character bundle"
            >
              Delete
            </button>
          )}
        </div>
      </div>

      {/* Select Projector Launcher Cards */}
      <div className="space-y-3">
        <h3 className="text-sm uppercase tracking-wider font-bold text-slate-300 flex items-center gap-2">
          <span>🚀</span> Choose Projector Presentation
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* 1. Summary Dashboard */}
          <div
            onClick={() => onLaunchProjector('summary')}
            className="group cursor-pointer bg-slate-900/70 border border-gold/40 hover:border-gold hover:bg-slate-900 rounded-xl p-5 transition-all shadow-card hover:shadow-gold-glow flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-2xl">📜</span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-gold/15 text-gold-soft border border-gold/40">
                  Classic View
                </span>
              </div>
              <h4 className="text-base font-bold text-slate-100 group-hover:text-gold-soft transition-colors">
                Chronicle Dashboard
              </h4>
              <p className="text-xs text-slate-400 mt-1.5">
                Overview summary of your character's career.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-gold-soft font-semibold">
              <span>Launch Dashboard &rarr;</span>
              <span className="text-[11px] text-slate-500">{selectedCardIds.length} cards active</span>
            </div>
          </div>

          {/* 2. Interactive Timeline */}
          <div
            onClick={() => onLaunchProjector('timeline')}
            className="group cursor-pointer bg-slate-900/70 border border-cyan/40 hover:border-cyan hover:bg-slate-900 rounded-xl p-5 transition-all shadow-card hover:shadow-[0_0_20px_rgba(56,189,248,0.2)] flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-2xl">📈</span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-cyan/15 text-cyan border border-cyan/40">
                  Interactive
                </span>
              </div>
              <h4 className="text-base font-bold text-slate-100 group-hover:text-cyan transition-colors">
                Interactive Career Timeline
              </h4>
              <p className="text-xs text-slate-400 mt-1.5">
                Interactive timeline across macro, seasonal, and deep-dive views.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-cyan font-semibold">
              <span>Launch Timeline &rarr;</span>
              <span className="text-[11px] text-slate-500">3 Zoom Tiers</span>
            </div>
          </div>

          {/* 3. Card Slideshow */}
          <div
            onClick={() => onLaunchProjector('slideshow')}
            className="group cursor-pointer bg-slate-900/70 border border-purple-500/40 hover:border-purple-400 hover:bg-slate-900 rounded-xl p-5 transition-all shadow-card hover:shadow-[0_0_20px_rgba(192,132,252,0.2)] flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-2xl">🎠</span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-purple-500/15 text-purple-300 border border-purple-400/40">
                  Presentation
                </span>
              </div>
              <h4 className="text-base font-bold text-slate-100 group-hover:text-purple-300 transition-colors">
                Card Slideshow
              </h4>
              <p className="text-xs text-slate-400 mt-1.5">
                Browse cards one at a time.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-purple-300 font-semibold">
              <span>Launch Slideshow &rarr;</span>
              <span className="text-[11px] text-slate-500">{selectedCardIds.length} slides</span>
            </div>
          </div>
        </div>
      </div>

      {/* Card Selector & Customizer */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex flex-wrap justify-between items-center gap-3 pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <span>🧩</span> Modular Chronicle Cards
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Select which cards are displayed in your chosen projector.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <button
              onClick={handleSelectDefault}
              className="px-2.5 py-1 rounded bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
            >
              Default (Recommended)
            </button>
            <button
              onClick={handleSelectAll}
              className="px-2.5 py-1 rounded bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
            >
              Select All
            </button>
            <button
              onClick={handleClearAll}
              className="px-2.5 py-1 rounded bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
            >
              Clear All
            </button>
          </div>
        </div>

        {/* Card Checklist Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {CARD_REGISTRY.map((card) => {
            const checked = selectedCardIds.includes(card.id);
            return (
              <label
                key={card.id}
                className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                  checked
                    ? 'border-gold/60 bg-gold/5 shadow-sm'
                    : 'border-slate-800 bg-slate-950/40 hover:border-slate-700 opacity-60'
                }`}
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleCard(card.id)}
                  className="mt-1 rounded border-slate-700 text-gold focus:ring-gold bg-slate-900"
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-200 truncate flex items-center gap-1.5">
                      <span>{card.icon}</span>
                      <span>{card.shortTitle}</span>
                    </span>
                    <span className="text-[10px] uppercase text-slate-500 tracking-wider">
                      {card.category}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                    {card.description}
                  </p>
                </div>
              </label>
            );
          })}
        </div>
      </div>
    </div>
  );
};
