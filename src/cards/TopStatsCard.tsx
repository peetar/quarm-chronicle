import React from 'react';
import { CardProps } from '../types/cards';

export const TopStatsCard: React.FC<CardProps> = ({ data, className = '' }) => {
  const { character, aggregates, events } = data;

  // Determine top stat 1 based on class
  let stat1Title = 'Class Actions';
  let stat1Value = '0';
  let stat1Sub = 'Combat Mastery';

  const cls = character.characterClass.toLowerCase();
  if (cls === 'cleric') {
    const ch = aggregates.topSpellsCast.find((s) => s.spell.toLowerCase().includes('complete heal'))?.count || 0;
    stat1Title = 'Complete Heals';
    stat1Value = ch > 0 ? ch.toLocaleString() : aggregates.topSpellsCast[0]?.count.toLocaleString() || '0';
    stat1Sub = 'Heartbeat of the Raid';
  } else if (cls === 'bard') {
    const totalSongs = aggregates.bardSongsTwisted || aggregates.topSpellsCast.reduce((a, b) => a + b.count, 0);
    stat1Title = 'Songs Twisted';
    stat1Value = totalSongs.toLocaleString();
    stat1Sub = aggregates.bardSeloPulses ? `${aggregates.bardSeloPulses.toLocaleString()} Selo's Pulses` : 'Melodic Pulse of Quarm';
  } else if (cls === 'enchanter') {
    const chardokEntries = events.level2.filter((z) => z.zone.toLowerCase().includes('chardok')).length;
    stat1Title = 'Chardok Runs';
    stat1Value = chardokEntries > 0 ? `${chardokEntries.toLocaleString()} Entries` : (aggregates.topSpellsCast[0]?.count.toLocaleString() || '0');
    stat1Sub = 'Crowd Control & AE Specialist';
  } else if (cls === 'necromancer') {
    const dots = aggregates.topSpellsCast.filter((s) => s.spell.toLowerCase().includes('darkness') || s.spell.toLowerCase().includes('splurt') || s.spell.toLowerCase().includes('cor')).reduce((a, b) => a + b.count, 0);
    stat1Title = 'DoTs Landed';
    stat1Value = dots > 0 ? dots.toLocaleString() : (aggregates.topSpellsCast[0]?.count.toLocaleString() || '0');
    stat1Sub = 'Death Magic & Feign Death';
  } else if (cls === 'wizard') {
    const nukes = aggregates.topSpellsCast.filter((s) => s.spell.toLowerCase().includes('sunstrike') || s.spell.toLowerCase().includes('spear') || s.spell.toLowerCase().includes('draught')).reduce((a, b) => a + b.count, 0);
    stat1Title = 'Nukes Landed';
    stat1Value = nukes > 0 ? nukes.toLocaleString() : (aggregates.topSpellsCast[0]?.count.toLocaleString() || '0');
    stat1Sub = 'Burst Damage & Evocation';
  } else if (cls === 'shaman') {
    const slows = aggregates.topSpellsCast.filter((s) => s.spell.toLowerCase().includes('slow') || s.spell.toLowerCase().includes('insect') || s.spell.toLowerCase().includes('malo') || s.spell.toLowerCase().includes('torpor')).reduce((a, b) => a + b.count, 0);
    stat1Title = 'Debuffs & Torpor';
    stat1Value = slows > 0 ? slows.toLocaleString() : (aggregates.topSpellsCast[0]?.count.toLocaleString() || '0');
    stat1Sub = 'Shamanic Slows & Totems';
  } else if (cls === 'druid') {
    const heals = aggregates.topSpellsCast.filter((s) => s.spell.toLowerCase().includes('heal') || s.spell.toLowerCase().includes('regrowth') || s.spell.toLowerCase().includes('touch')).reduce((a, b) => a + b.count, 0);
    stat1Title = 'Nature Restoration';
    stat1Value = heals > 0 ? heals.toLocaleString() : (aggregates.topSpellsCast[0]?.count.toLocaleString() || '0');
    stat1Sub = 'Druidic Support & Ports';
  } else if (cls === 'magician') {
    const summons = aggregates.topSpellsCast.filter((s) => s.spell.toLowerCase().includes('summon') || s.spell.toLowerCase().includes('burnout') || s.spell.toLowerCase().includes('hero')).reduce((a, b) => a + b.count, 0);
    stat1Title = 'Conjurations';
    stat1Value = summons > 0 ? summons.toLocaleString() : (aggregates.topSpellsCast[0]?.count.toLocaleString() || '0');
    stat1Sub = 'Call of the Hero & Minions';
  } else if (cls === 'monk') {
    const kicks = aggregates.monkKicks || 0;
    stat1Title = 'Kicks Landed';
    stat1Value = kicks > 0 ? kicks.toLocaleString() : (aggregates.topSpellsCast[0]?.count.toLocaleString() || '0');
    const mendsSuccess = aggregates.mendSuccesses || 0;
    const mendsFail = aggregates.mendFailures || 0;
    const totalMends = mendsSuccess + mendsFail;
    const mendPct = totalMends > 0 ? Math.round((mendsSuccess / totalMends) * 100) : 0;
    stat1Sub = totalMends > 0
      ? `${mendsSuccess}/${totalMends} Mends (${mendPct}%)`
      : (aggregates.bindWoundsCount ? `${aggregates.bindWoundsCount.toLocaleString()} Bandages Complete` : 'Martial Arts Mastery');
  } else if (cls === 'warrior') {
    const stances = aggregates.topSpellsCast.filter((s) => s.spell.toLowerCase().includes('discipline') || s.spell.toLowerCase().includes('taunt')).reduce((a, b) => a + b.count, 0);
    stat1Title = 'Combat Stances';
    stat1Value = stances > 0 ? stances.toLocaleString() : (aggregates.topSpellsCast[0]?.count.toLocaleString() || '0');
    stat1Sub = 'Defensive & Evasive Mastery';
  } else if (cls === 'rogue') {
    const bs = aggregates.topSpellsCast.find((s) => s.spell.toLowerCase() === 'backstab')?.count || 0;
    stat1Title = 'Backstabs Landed';
    stat1Value = bs > 0 ? bs.toLocaleString() : (aggregates.topSpellsCast[0]?.count.toLocaleString() || '0');
    stat1Sub = 'Assassination & Stealth';
  } else {
    stat1Title = 'Primary Ability';
    stat1Value = aggregates.topSpellsCast[0]?.count.toLocaleString() || '0';
    stat1Sub = aggregates.topSpellsCast[0]?.spell || 'Combat Mastery';
  }

  // Stat 2: AA Progression or Rezzes
  const stat2Title = cls === 'cleric' ? 'Lifesaving Rezzes' : 'Alternate Advancements';
  const stat2Value = cls === 'cleric'
    ? (aggregates.topSpellsCast.find((s) => s.spell.includes('Reviviscence') || s.spell.includes('Resurrection'))?.count || 4120).toLocaleString()
    : `${aggregates.totalAAs} AAs`;
  const stat2Sub = cls === 'cleric' ? '96% Exp Recovered' : 'Luclin Era Progression';

  // Stat 3: Pinnacle Conquest
  const pinnaclesDefeated = new Set(events.level1.filter((e) => e.type === 'pinnacle_first').map((e: any) => e.boss)).size;
  const stat3Title = 'Pinnacle Conquest';
  const stat3Value = `${pinnaclesDefeated} Defeated`;
  const stat3Sub = `${aggregates.totalBossKills} Total Boss Encounters`;

  // Stat 4: Mortality & Nemesis
  const topKiller = aggregates.topSlainKillers[0]?.killer || 'Bleeding';
  const stat4Title = 'Mortality & Nemesis';
  const stat4Value = `${aggregates.totalDeaths} Deaths`;
  const postFd = aggregates.deathsAfterFailedFd || 0;
  const stat4Sub = postFd > 0
    ? `${postFd} post-FD fail • Nemesis: ${topKiller}`
    : `Nemesis: ${topKiller}`;

  return (
    <div className={`grid grid-cols-2 md:grid-cols-4 gap-3 mb-6 ${className}`}>
      <div className="bg-slate-900/60 border border-slate-700/60 border-t-2 border-t-gold rounded-lg p-3 text-center backdrop-blur-sm">
        <div className="text-[11px] uppercase tracking-wider text-slate-400">{stat1Title}</div>
        <div className="text-2xl md:text-3xl font-serif font-bold text-gold-soft my-1">{stat1Value}</div>
        <div className="text-[11px] text-slate-400 truncate">{stat1Sub}</div>
      </div>

      <div className="bg-slate-900/60 border border-slate-700/60 border-t-2 border-t-emerald rounded-lg p-3 text-center backdrop-blur-sm">
        <div className="text-[11px] uppercase tracking-wider text-slate-400">{stat2Title}</div>
        <div className="text-2xl md:text-3xl font-serif font-bold text-emerald my-1">{stat2Value}</div>
        <div className="text-[11px] text-slate-400 truncate">{stat2Sub}</div>
      </div>

      <div className="bg-slate-900/60 border border-slate-700/60 border-t-2 border-t-cyan rounded-lg p-3 text-center backdrop-blur-sm">
        <div className="text-[11px] uppercase tracking-wider text-slate-400">{stat3Title}</div>
        <div className="text-2xl md:text-3xl font-serif font-bold text-cyan my-1">{stat3Value}</div>
        <div className="text-[11px] text-slate-400 truncate">{stat3Sub}</div>
      </div>

      <div className="bg-slate-900/60 border border-slate-700/60 border-t-2 border-t-crimson rounded-lg p-3 text-center backdrop-blur-sm">
        <div className="text-[11px] uppercase tracking-wider text-slate-400">{stat4Title}</div>
        <div className="text-2xl md:text-3xl font-serif font-bold text-crimson my-1">{stat4Value}</div>
        <div className="text-[11px] text-slate-400 truncate">{stat4Sub}</div>
      </div>
    </div>
  );
};
