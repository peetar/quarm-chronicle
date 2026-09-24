import React, { useState, useEffect, useRef, useMemo } from 'react';
import { CardProps } from '../types/cards';
import {
  BossKillEvent,
  MonthlyBossSummary,
  DailyBossSummary,
  DailyDeathSummary,
  DeathEvent,
} from '../types/events';
import html2canvas from 'html2canvas';

export interface TimelineTick {
  timeMs: number;
  label: string;
  pct: number; // 0 to 1
  isMajor?: boolean;
}

export function getEventJitter(key: string, maxOffset: number): number {
  let hash = 0;
  for (let i = 0; i < key.length; i++) {
    hash = (hash << 5) - hash + key.charCodeAt(i);
    hash |= 0;
  }
  const norm = ((Math.abs(hash) % 1000) / 500) - 1;
  return Math.round(norm * maxOffset);
}

export function generateTimelineTicks(
  windowStart: number,
  windowEnd: number,
  zoomLevel: 1 | 2 | 3
): TimelineTick[] {
  const spanMs = Math.max(1, windowEnd - windowStart);
  const ticks: TimelineTick[] = [];

  if (zoomLevel === 1) {
    // -------------------------------------------------------------
    // Zoom 1: Macro -> Months
    // -------------------------------------------------------------
    const start = new Date(windowStart);
    const end = new Date(windowEnd);

    let cur = new Date(start.getFullYear(), start.getMonth(), 1);
    const totalMonths =
      (end.getFullYear() - start.getFullYear()) * 12 +
      (end.getMonth() - start.getMonth()) + 1;

    // Adapt step if span has many months to prevent crowding
    const step = totalMonths > 32 ? 3 : totalMonths > 18 ? 2 : 1;
    let idx = 0;

    while (cur.getTime() <= windowEnd + 15 * 86400000) {
      const t = cur.getTime();
      const pct = (t - windowStart) / spanMs;

      if (pct >= -0.01 && pct <= 1.01) {
        const monthName = cur.toLocaleDateString('en-US', { month: 'short' });
        const year = cur.getFullYear();
        const isJan = cur.getMonth() === 0;

        if (idx % step === 0 || isJan) {
          const label = isJan ? `${monthName} '${String(year).slice(-2)}` : monthName;
          ticks.push({
            timeMs: t,
            label,
            pct: Math.max(0, Math.min(1, pct)),
            isMajor: isJan,
          });
        }
      }

      cur.setMonth(cur.getMonth() + 1);
      idx++;
    }
  } else if (zoomLevel === 2) {
    // -------------------------------------------------------------
    // Zoom 2: Seasonal -> Weeks
    // -------------------------------------------------------------
    // In ~30 day seasonal window, generate weekly ticks (every 7 days)
    const cur = new Date(windowStart);
    cur.setHours(0, 0, 0, 0);
    const sevenDaysMs = 7 * 86400000;

    for (let t = cur.getTime(); t <= windowEnd + 86400000; t += sevenDaysMs) {
      const pct = (t - windowStart) / spanMs;
      if (pct >= -0.01 && pct <= 1.01) {
        const d = new Date(t);
        const monthName = d.toLocaleDateString('en-US', { month: 'short' });
        const day = d.getDate();
        // Clean week format: e.g. "Sep 1", "Sep 8", "Sep 15", "Sep 22"
        const label = `${monthName} ${day}`;
        ticks.push({
          timeMs: t,
          label,
          pct: Math.max(0, Math.min(1, pct)),
          isMajor: day <= 7,
        });
      }
    }
  } else {
    // -------------------------------------------------------------
    // Zoom 3: Deep Dive -> Days
    // -------------------------------------------------------------
    // In 7 day deep dive window, generate daily ticks
    const cur = new Date(windowStart);
    cur.setHours(0, 0, 0, 0);
    const dayMs = 86400000;

    for (let t = cur.getTime(); t <= windowEnd + 43200000; t += dayMs) {
      const pct = (t - windowStart) / spanMs;
      if (pct >= -0.01 && pct <= 1.01) {
        const d = new Date(t);
        const weekday = d.toLocaleDateString('en-US', { weekday: 'short' });
        const monthName = d.toLocaleDateString('en-US', { month: 'short' });
        const day = d.getDate();
        // Clean day format: e.g. "Mon Sep 1", "Tue Sep 2"
        const label = `${weekday} ${monthName} ${day}`;
        const isWeekend = d.getDay() === 0 || d.getDay() === 6;
        ticks.push({
          timeMs: t,
          label,
          pct: Math.max(0, Math.min(1, pct)),
          isMajor: isWeekend,
        });
      }
    }
  }

  return ticks;
}

export const InteractiveTimelineCard: React.FC<CardProps> = ({ data, className = '' }) => {
  const { character, events, eras } = data;

  const [zoomLevel, setZoomLevel] = useState<1 | 2 | 3>(1);
  const [selectedEvent, setSelectedEvent] = useState<any | null>(null);

  const timelineCardRef = useRef<HTMLDivElement>(null);
  const trackWrapperRef = useRef<HTMLDivElement>(null);
  const minimapBarRef = useRef<HTMLDivElement>(null);

  const minDateMs = useMemo(() => {
    const s = character.dateRange.startIso || `${character.dateRange.start}T00:00:00`;
    return new Date(s).getTime() || new Date('2024-07-06T00:00:00').getTime();
  }, [character.dateRange]);

  const maxDateMs = useMemo(() => {
    const e = character.dateRange.endIso || `${character.dateRange.end}T23:59:59`;
    return new Date(e).getTime() || new Date('2026-09-17T23:59:59').getTime();
  }, [character.dateRange]);

  const [windowStart, setWindowStart] = useState<number>(minDateMs);
  const [windowEnd, setWindowEnd] = useState<number>(maxDateMs);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const dragStartRef = useRef<{ clientX: number; start: number; end: number }>({ clientX: 0, start: 0, end: 0 });

  useEffect(() => {
    setWindowStart(minDateMs);
    setWindowEnd(maxDateMs);
  }, [minDateMs, maxDateMs]);

  // Zoom handlers
  const handleZoom = (lvl: 1 | 2 | 3) => {
    setZoomLevel(lvl);
    if (lvl === 1) {
      setWindowStart(minDateMs);
      setWindowEnd(maxDateMs);
    } else if (lvl === 2) {
      const monthSpan = 30 * 24 * 60 * 60 * 1000;
      const center = (windowStart + windowEnd) / 2;
      let s = center - monthSpan / 2;
      let e = center + monthSpan / 2;
      if (s < minDateMs) { s = minDateMs; e = s + monthSpan; }
      if (e > maxDateMs) { e = maxDateMs; s = Math.max(minDateMs, e - monthSpan); }
      setWindowStart(s);
      setWindowEnd(e);
    } else if (lvl === 3) {
      const weekSpan = 7 * 24 * 60 * 60 * 1000;
      const center = (windowStart + windowEnd) / 2;
      let s = center - weekSpan / 2;
      let e = center + weekSpan / 2;
      if (s < minDateMs) { s = minDateMs; e = s + weekSpan; }
      if (e > maxDateMs) { e = maxDateMs; s = Math.max(minDateMs, e - weekSpan); }
      setWindowStart(s);
      setWindowEnd(e);
    }
  };

  const handleStepTime = (days: number) => {
    const span = windowEnd - windowStart;
    const delta = days * 24 * 60 * 60 * 1000;
    let s = windowStart + delta;
    let e = windowEnd + delta;
    if (s < minDateMs) { s = minDateMs; e = s + span; }
    if (e > maxDateMs) { e = maxDateMs; s = Math.max(minDateMs, e - span); }
    setWindowStart(s);
    setWindowEnd(e);
  };

  const jumpToEra = (eraName: string) => {
    const found = eras.find((e) => e.era.toLowerCase() === eraName.toLowerCase());
    if (found && found.date) {
      const target = new Date(found.date).getTime();
      const span = 30 * 24 * 60 * 60 * 1000;
      setWindowStart(Math.max(minDateMs, target));
      setWindowEnd(Math.min(maxDateMs, target + span));
      setZoomLevel(2);
    } else if (eraName.toLowerCase() === 'classic') {
      const span = 30 * 24 * 60 * 60 * 1000;
      setWindowStart(minDateMs);
      setWindowEnd(Math.min(maxDateMs, minDateMs + span));
      setZoomLevel(2);
    } else {
      alert(`No recorded entries for ${eraName} in this character's log.`);
    }
  };

  // Monthly boss summaries calculation
  const monthlyBossSummaries = useMemo<MonthlyBossSummary[]>(() => {
    const allBosses = events.level3.filter(
      (e) => e.type === 'raid_boss_kill' || e.type === 'pvp_boss_kill'
    ) as BossKillEvent[];

    const monthMap: Record<string, MonthlyBossSummary> = {};

    allBosses.forEach((k) => {
      const dt = new Date(k.iso || k.date || k.timestamp);
      const y = dt.getFullYear();
      const m = dt.getMonth() + 1;
      const key = `${y}-${String(m).padStart(2, '0')}`;

      if (!monthMap[key]) {
        monthMap[key] = {
          type: 'monthly_boss_summary',
          monthKey: key,
          year: y,
          month: m,
          monthName: dt.toLocaleString('en-US', { month: 'short' }),
          kills: [],
          uniqueBossCount: 0,
          sampleText: '',
          title: '',
          zoneBreakdown: '',
          timestampMs: 0,
          iso: '',
        };
      }
      monthMap[key].kills.push(k);
    });

    return Object.values(monthMap).map((m) => {
      m.kills.sort((a, b) => new Date(a.iso || a.date).getTime() - new Date(b.iso || b.date).getTime());
      const totalTime = m.kills.reduce((acc, k) => acc + new Date(k.iso || k.date || k.timestamp).getTime(), 0);
      const avg = Math.round(totalTime / m.kills.length);
      m.timestampMs = avg;
      m.iso = new Date(avg).toISOString();

      const unique = Array.from(new Set(m.kills.map((k) => k.boss)));
      m.uniqueBossCount = unique.length;
      const sample = unique.slice(0, 2);
      m.sampleText = sample.join(', ') + (unique.length > 2 ? ` +${unique.length - 2}` : '');
      m.title = `Boss Kills — ${m.monthName} ${m.year} (${m.kills.length} Kills)`;

      const zoneCounts: Record<string, number> = {};
      m.kills.forEach((k) => {
        zoneCounts[k.zone] = (zoneCounts[k.zone] || 0) + 1;
      });
      m.zoneBreakdown = Object.entries(zoneCounts)
        .sort((a, b) => b[1] - a[1])
        .map(([z, c]) => `${z} (${c})`)
        .join(', ');

      return m;
    }).sort((a, b) => a.timestampMs - b.timestampMs);
  }, [events.level3]);

  // Daily boss summaries calculation (for Zoom 2: Seasonal 1-Month)
  const dailyBossSummaries = useMemo<DailyBossSummary[]>(() => {
    const allBosses = events.level3.filter(
      (e) => e.type === 'raid_boss_kill' || e.type === 'pvp_boss_kill'
    ) as BossKillEvent[];

    const dayMap: Record<string, DailyBossSummary> = {};

    allBosses.forEach((k) => {
      const dateKey = k.date || (k.iso ? k.iso.substring(0, 10) : '');
      if (!dateKey) return;

      if (!dayMap[dateKey]) {
        const dt = new Date(k.iso || k.date || k.timestamp);
        const dateLabel = dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        dayMap[dateKey] = {
          type: 'daily_boss_summary',
          dateKey,
          dateLabel,
          kills: [],
          uniqueBossCount: 0,
          sampleText: '',
          title: '',
          zoneBreakdown: '',
          timestampMs: 0,
          iso: '',
        };
      }
      dayMap[dateKey].kills.push(k);
    });

    return Object.values(dayMap).map((d) => {
      d.kills.sort((a, b) => new Date(a.iso || a.date).getTime() - new Date(b.iso || b.date).getTime());
      const totalTime = d.kills.reduce((acc, k) => acc + new Date(k.iso || k.date || k.timestamp).getTime(), 0);
      const avg = Math.round(totalTime / d.kills.length);
      d.timestampMs = avg;
      d.iso = new Date(avg).toISOString();

      const unique = Array.from(new Set(d.kills.map((k) => k.boss)));
      d.uniqueBossCount = unique.length;
      if (d.kills.length === 1) {
        d.sampleText = d.kills[0].boss;
        d.title = `Raid Boss Kill — ${d.kills[0].boss} (${d.dateLabel})`;
      } else {
        const sample = unique.slice(0, 2);
        d.sampleText = sample.join(', ') + (unique.length > 2 ? ` +${unique.length - 2}` : '');
        d.title = `Boss Kills — ${d.dateLabel} (${d.kills.length} Kills)`;
      }

      const zoneCounts: Record<string, number> = {};
      d.kills.forEach((k) => {
        zoneCounts[k.zone] = (zoneCounts[k.zone] || 0) + 1;
      });
      d.zoneBreakdown = Object.entries(zoneCounts)
        .sort((a, b) => b[1] - a[1])
        .map(([z, c]) => `${z} (${c})`)
        .join(', ');

      return d;
    }).sort((a, b) => a.timestampMs - b.timestampMs);
  }, [events.level3]);

  // Daily death summaries calculation (for Zoom 2: Seasonal 1-Month, placed above timeline)
  const dailyDeathSummaries = useMemo<DailyDeathSummary[]>(() => {
    const allDeaths = events.level3.filter(
      (e) => e.type === 'death'
    ) as DeathEvent[];

    const dayMap: Record<string, DailyDeathSummary> = {};

    allDeaths.forEach((d) => {
      const dateKey = d.date || (d.iso ? d.iso.substring(0, 10) : '');
      if (!dateKey) return;

      if (!dayMap[dateKey]) {
        const dt = new Date(d.iso || d.date || d.timestamp);
        const dateLabel = dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        dayMap[dateKey] = {
          type: 'daily_death_summary',
          dateKey,
          dateLabel,
          deaths: [],
          totalDeaths: 0,
          topKiller: '',
          sampleText: '',
          title: '',
          zoneBreakdown: '',
          timestampMs: 0,
          iso: '',
        };
      }
      dayMap[dateKey].deaths.push(d);
    });

    return Object.values(dayMap).map((d) => {
      d.deaths.sort((a, b) => new Date(a.iso || a.date).getTime() - new Date(b.iso || b.date).getTime());
      const totalTime = d.deaths.reduce((acc, k) => acc + new Date(k.iso || k.date || k.timestamp).getTime(), 0);
      const avg = Math.round(totalTime / d.deaths.length);
      d.timestampMs = avg;
      d.iso = new Date(avg).toISOString();
      d.totalDeaths = d.deaths.length;

      const killerCounts: Record<string, number> = {};
      d.deaths.forEach((k) => {
        killerCounts[k.killer] = (killerCounts[k.killer] || 0) + 1;
      });
      const sortedKillers = Object.entries(killerCounts).sort((a, b) => b[1] - a[1]);
      d.topKiller = sortedKillers[0] ? sortedKillers[0][0] : 'Unknown';

      if (d.totalDeaths === 1) {
        d.sampleText = d.deaths[0].killer;
        d.title = `Death — Died to ${d.deaths[0].killer} (${d.dateLabel})`;
      } else {
        const sample = sortedKillers.slice(0, 2).map(([k, c]) => (c > 1 ? `${k} (${c})` : k));
        d.sampleText = sample.join(', ') + (sortedKillers.length > 2 ? ` +${sortedKillers.length - 2}` : '');
        d.title = `Deaths — ${d.dateLabel} (${d.totalDeaths} Deaths)`;
      }

      const zoneCounts: Record<string, number> = {};
      d.deaths.forEach((k) => {
        zoneCounts[k.zone] = (zoneCounts[k.zone] || 0) + 1;
      });
      d.zoneBreakdown = Object.entries(zoneCounts)
        .sort((a, b) => b[1] - a[1])
        .map(([z, c]) => `${z} (${c})`)
        .join(', ');

      return d;
    }).sort((a, b) => a.timestampMs - b.timestampMs);
  }, [events.level3]);

  // Mini-map drag interactions
  const handleMinimapMouseDown = (e: React.MouseEvent) => {
    if (!minimapBarRef.current) return;
    const rect = minimapBarRef.current.getBoundingClientRect();
    const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const fullMs = maxDateMs - minDateMs;
    const clicked = minDateMs + pct * fullMs;
    const span = windowEnd - windowStart;

    let s = clicked - span / 2;
    let end = clicked + span / 2;
    if (s < minDateMs) { s = minDateMs; end = s + span; }
    if (end > maxDateMs) { end = maxDateMs; s = Math.max(minDateMs, end - span); }
    setWindowStart(s);
    setWindowEnd(end);

    setIsDragging(true);
    dragStartRef.current = { clientX: e.clientX, start: s, end };
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !minimapBarRef.current) return;
      const rect = minimapBarRef.current.getBoundingClientRect();
      const deltaPx = e.clientX - dragStartRef.current.clientX;
      const fullMs = maxDateMs - minDateMs;
      const deltaMs = (deltaPx / rect.width) * fullMs;
      const span = dragStartRef.current.end - dragStartRef.current.start;

      let s = dragStartRef.current.start + deltaMs;
      let end = s + span;
      if (s < minDateMs) { s = minDateMs; end = s + span; }
      if (end > maxDateMs) { end = maxDateMs; s = Math.max(minDateMs, end - span); }
      setWindowStart(s);
      setWindowEnd(end);
    };

    const handleMouseUp = () => {
      if (isDragging) setIsDragging(false);
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, minDateMs, maxDateMs]);

  // Copy Timeline Image
  const copyTimelineImage = async () => {
    if (!timelineCardRef.current) return;
    try {
      const canvas = await html2canvas(timelineCardRef.current, {
        backgroundColor: '#080a0f',
        scale: 2,
        useCORS: true,
      });
      canvas.toBlob(async (blob) => {
        if (!blob) return;
        await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
        alert('Timeline image copied to clipboard!');
      }, 'image/png');
    } catch (err: any) {
      alert(`Clipboard copy failed: ${err.message}`);
    }
  };

  // Download Timeline PNG
  const downloadTimelineImage = async () => {
    if (!timelineCardRef.current) return;
    try {
      const canvas = await html2canvas(timelineCardRef.current, {
        backgroundColor: '#080a0f',
        scale: 2,
        useCORS: true,
      });
      const link = document.createElement('a');
      link.download = `${character.name.toLowerCase()}_timeline.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    } catch (err: any) {
      alert(`Image download failed: ${err.message}`);
    }
  };

  const totalWindowMs = Math.max(1, windowEnd - windowStart);
  const fullRangeMs = Math.max(1, maxDateMs - minDateMs);

  // Active events for current window
  const activeEvents = useMemo(() => {
    const list: any[] = [...events.level1];
    if (zoomLevel === 1) {
      list.push(...monthlyBossSummaries);
      list.push(...events.level2.filter((e) => e.type === 'aa_gain'));
    } else if (zoomLevel === 2) {
      list.push(...dailyBossSummaries);
      list.push(...dailyDeathSummaries);
      list.push(...events.level2.filter((e) => e.type === 'aa_gain'));
    } else if (zoomLevel >= 3) {
      list.push(...events.level2.filter((e) => e.type === 'aa_gain'));
      list.push(...events.level3);
    }

    return list.filter((e) => {
      const t = new Date(e.iso || e.date || e.timestamp).getTime();
      return t >= windowStart && t <= windowEnd;
    });
  }, [events, zoomLevel, windowStart, windowEnd, monthlyBossSummaries, dailyBossSummaries, dailyDeathSummaries]);

  // Formatted window label
  const windowLabel = useMemo(() => {
    const sStr = new Date(windowStart).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    const eStr = new Date(windowEnd).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    return `${sStr} — ${eStr}`;
  }, [windowStart, windowEnd]);

  // Scrubber viewport positioning
  const scrubberLeftPct = Math.max(0, Math.min(100, ((windowStart - minDateMs) / fullRangeMs) * 100));
  const scrubberWidthPct = Math.max(2, Math.min(100, (totalWindowMs / fullRangeMs) * 100));

  // Date labels for timeline axis (months for Macro, weeks for seasonal, days for deep dive)
  const interactiveTicks = useMemo(() => {
    return generateTimelineTicks(windowStart, windowEnd, zoomLevel);
  }, [windowStart, windowEnd, zoomLevel]);

  return (
    <div ref={timelineCardRef} className={`space-y-4 ${className}`}>
      {/* Top Header & Export Actions */}
      <div className="bg-slate-900/80 border border-slate-700/60 rounded-xl p-4 flex flex-wrap justify-between items-center gap-4">
        <div>
          <div className="text-gold-soft text-xs uppercase tracking-widest font-bold">
            Project Quarm
          </div>
          <h2 className="text-2xl font-serif text-white font-bold my-1 tracking-wide">
            {character.name.toUpperCase()} TIMELINE
          </h2>
          <div className="text-cyan text-xs md:text-sm">
            Level {character.level} {character.characterClass} • &lt;{character.guild}&gt; •{' '}
            <span className="text-slate-400">
              {zoomLevel === 1 ? `${character.dateRange.start} — ${character.dateRange.end}` : windowLabel}
            </span>
          </div>
        </div>

        <div className="flex gap-2" data-html2canvas-ignore="true">
          <button
            onClick={copyTimelineImage}
            className="px-3 py-1.5 rounded border border-gold text-gold-soft hover:bg-gold/10 text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            📋 Copy Image
          </button>
          <button
            onClick={downloadTimelineImage}
            className="px-3 py-1.5 rounded border border-cyan text-cyan hover:bg-cyan/10 text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            💾 Download PNG
          </button>
        </div>
      </div>

      {/* Interactive Controls */}
      <div
        data-html2canvas-ignore="true"
        className="bg-slate-900/70 border border-slate-700/60 rounded-xl p-3.5 space-y-3"
      >
        <div className="flex flex-wrap justify-between items-center gap-3 text-xs">
          <div className="flex items-center gap-2">
            <span className="text-slate-400 uppercase font-semibold">Zoom Level:</span>
            <button
              onClick={() => handleZoom(1)}
              className={`px-2.5 py-1.5 rounded border transition-colors ${
                zoomLevel === 1 ? 'border-cyan text-cyan bg-cyan/10 font-bold' : 'border-slate-700 text-slate-300 hover:border-slate-500'
              }`}
            >
              1: Macro (All-Time)
            </button>
            <button
              onClick={() => handleZoom(2)}
              className={`px-2.5 py-1.5 rounded border transition-colors ${
                zoomLevel === 2 ? 'border-cyan text-cyan bg-cyan/10 font-bold' : 'border-slate-700 text-slate-300 hover:border-slate-500'
              }`}
            >
              2: Seasonal (1 Month)
            </button>
            <button
              onClick={() => handleZoom(3)}
              className={`px-2.5 py-1.5 rounded border transition-colors ${
                zoomLevel === 3 ? 'border-cyan text-cyan bg-cyan/10 font-bold' : 'border-slate-700 text-slate-300 hover:border-slate-500'
              }`}
            >
              3: Week Deep Dive (7 Days)
            </button>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-slate-400 uppercase font-semibold">Jump to Era:</span>
            <button onClick={() => jumpToEra('Classic')} className="px-2 py-1 rounded border border-emerald/50 text-emerald hover:bg-emerald/10 text-xs">Classic</button>
            <button onClick={() => jumpToEra('Kunark')} className="px-2 py-1 rounded border border-gold/50 text-gold-soft hover:bg-gold/10 text-xs">Kunark</button>
            <button onClick={() => jumpToEra('Velious')} className="px-2 py-1 rounded border border-cyan/50 text-cyan hover:bg-cyan/10 text-xs">Velious</button>
            <button onClick={() => jumpToEra('Luclin')} className="px-2 py-1 rounded border border-purple/50 text-purple hover:bg-purple/10 text-xs">Luclin</button>
            <button onClick={() => alert('Planes of Power is coming soon!')} className="px-2 py-1 rounded border border-crimson/50 text-crimson hover:bg-crimson/10 text-xs">PoP</button>
          </div>
        </div>

        {zoomLevel > 1 && (
          <div className="flex justify-between items-center gap-2 pt-2 border-t border-slate-700/50 text-xs">
            <div className="flex gap-1.5">
              <button onClick={() => handleStepTime(-30)} className="px-2 py-1 rounded border border-slate-700 hover:border-slate-500 text-slate-300">&laquo; 1 Month</button>
              <button onClick={() => handleStepTime(-7)} className="px-2 py-1 rounded border border-slate-700 hover:border-slate-500 text-slate-300">&lsaquo; 1 Week</button>
            </div>

            <div className="font-semibold text-gold-soft px-3 py-1 bg-slate-950/70 rounded border border-gold/30">
              {windowLabel}
            </div>

            <div className="flex gap-1.5">
              <button onClick={() => handleStepTime(7)} className="px-2 py-1 rounded border border-slate-700 hover:border-slate-500 text-slate-300">1 Week &rsaquo;</button>
              <button onClick={() => handleStepTime(30)} className="px-2 py-1 rounded border border-slate-700 hover:border-slate-500 text-slate-300">1 Month &raquo;</button>
              <button
                onClick={() => {
                  const span = windowEnd - windowStart;
                  setWindowEnd(maxDateMs);
                  setWindowStart(Math.max(minDateMs, maxDateMs - span));
                }}
                className="px-2 py-1 rounded border border-gold/60 text-gold-soft hover:bg-gold/10 font-medium"
              >
                Latest &raquo;|
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Main Timeline Card Container */}
      <div className="bg-[#101522]/95 border-2 border-double border-gold/70 rounded-xl p-5 shadow-[0_0_35px_rgba(212,175,55,0.12)] relative">
        {/* Interactive Timeline Track */}
            <div
              ref={trackWrapperRef}
              className="relative w-full h-[520px] overflow-hidden bg-slate-950/60 rounded-lg border border-slate-800"
            >
              {/* Background Vertical Gridlines for Date Ticks */}
              {interactiveTicks.map((tick, i) => (
                <div
                  key={`itick-grid-${i}`}
                  style={{ left: `${tick.pct * 100}%` }}
                  className={`absolute top-0 bottom-7 w-[1px] pointer-events-none ${
                    tick.isMajor ? 'bg-slate-700/50' : 'bg-slate-800/35'
                  }`}
                />
              ))}

              {/* Central Axis Line (240px from top) */}
              <div className="absolute top-[240px] left-0 right-0 h-[2px] bg-gradient-to-r from-emerald via-gold via-cyan to-crimson shadow-[0_0_8px_rgba(212,175,55,0.6)]" />

              {/* Axis Tick Notches on Central Line */}
              {interactiveTicks.map((tick, i) => (
                <div
                  key={`itick-notch-${i}`}
                  style={{ left: `${tick.pct * 100}%`, top: '235px' }}
                  className={`absolute -translate-x-1/2 w-[2px] h-[12px] pointer-events-none z-0 ${
                    tick.isMajor ? 'bg-gold' : 'bg-gold/60'
                  }`}
                />
              ))}

              {/* Render Nodes */}
              {activeEvents.map((e, idx) => {
                const t = new Date(e.iso || e.date || e.timestamp).getTime();
                const pct = Math.max(0, Math.min(1, (t - windowStart) / totalWindowMs));
                const leftPct = pct * 100;

                if (e.type === 'level_ding') {
                  const isKey = e.dingLevel % 10 === 0 || e.dingLevel === 60;
                  return (
                    <div
                      key={`ding-${idx}`}
                      onClick={() => setSelectedEvent(e)}
                      style={{ left: `${leftPct}%`, top: '228px' }}
                      title={`Level ${e.dingLevel} reached on ${e.date}`}
                      className={`absolute -translate-x-1/2 w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] cursor-pointer z-10 hover:z-50 transition-transform hover:scale-125 ${
                        isKey
                          ? 'bg-amber-400 text-slate-950 border-2 border-white shadow-[0_0_10px_rgba(251,191,36,0.9)]'
                          : 'bg-amber-700/80 text-white border border-amber-400'
                      }`}
                    >
                      {e.badge}
                    </div>
                  );
                }

                if (e.type === 'pinnacle_first') {
                  const tiers = [160, 118, 76, 34];
                  const baseTop = tiers[idx % tiers.length];
                  const jitter = getEventJitter(e.boss + idx, 10);
                  const chosenTop = Math.max(16, Math.min(168, baseTop + jitter));
                  const stemHeight = Math.max(14, 240 - chosenTop - 26);

                  return (
                    <div
                      key={`pin-${idx}`}
                      style={{ left: `${leftPct}%`, top: `${chosenTop}px` }}
                      className="absolute -translate-x-1/2 flex flex-col items-center z-20 hover:z-50 pointer-events-none"
                    >
                      <div
                        onClick={() => setSelectedEvent(e)}
                        className="pointer-events-auto cursor-pointer bg-purple-950/95 border border-purple text-white px-2.5 py-1 rounded-full text-xs font-bold whitespace-nowrap shadow-[0_0_12px_rgba(192,132,252,0.5)] hover:scale-110 transition-transform"
                      >
                        👑 {e.boss}
                      </div>
                      <div style={{ height: `${stemHeight}px` }} className="w-[1.5px] bg-purple opacity-75 pointer-events-none" />
                    </div>
                  );
                }

                if (e.type === 'epic_acquired') {
                  const epicTop = Math.max(15, 45 + getEventJitter(e.title + idx, 15));
                  const stemHeight = Math.max(20, 240 - epicTop - 30);
                  return (
                    <div
                      key={`epic-${idx}`}
                      style={{ left: `${leftPct}%`, top: `${epicTop}px` }}
                      className="absolute -translate-x-1/2 flex flex-col items-center z-20 hover:z-50 pointer-events-none"
                    >
                      <div
                        onClick={() => setSelectedEvent(e)}
                        className="pointer-events-auto cursor-pointer bg-amber-950/95 border-2 border-gold text-gold-soft px-3 py-1.5 rounded-full text-xs font-extrabold whitespace-nowrap shadow-gold-glow hover:scale-110 transition-transform"
                      >
                        ✨ {e.title}
                      </div>
                      <div style={{ height: `${stemHeight}px` }} className="w-[2px] bg-gold opacity-80 pointer-events-none" />
                    </div>
                  );
                }

                if (e.type === 'guild_join' || e.type === 'guild_leave') {
                  const tiers = [24, 56, 88];
                  const baseStem = tiers[idx % tiers.length];
                  const jitter = getEventJitter(e.guild + idx, 8);
                  const stemHeight = Math.max(16, Math.min(105, baseStem + jitter));

                  return (
                    <div
                      key={`guild-${idx}`}
                      style={{ left: `${leftPct}%`, top: '240px' }}
                      className="absolute -translate-x-1/2 flex flex-col items-center z-10 hover:z-50 pointer-events-none"
                    >
                      <div style={{ height: `${stemHeight}px` }} className="w-[1px] bg-slate-500 opacity-60 pointer-events-none" />
                      <div
                        onClick={() => setSelectedEvent(e)}
                        className="pointer-events-auto cursor-pointer bg-slate-900 border border-slate-600 text-slate-300 px-2 py-0.5 rounded text-[11px] whitespace-nowrap hover:scale-105 transition-transform"
                      >
                        {e.type === 'guild_join' ? '🛡️' : '🚪'} &lt;{e.guild}&gt;
                      </div>
                    </div>
                  );
                }

                if (e.type === 'monthly_boss_summary') {
                  const tiers = [30, 72, 114, 156];
                  const baseStem = tiers[idx % tiers.length];
                  const jitter = getEventJitter((e.monthKey || '') + idx, 12);
                  const stemHeight = Math.max(20, Math.min(165, baseStem + jitter));

                  return (
                    <div
                      key={`m-boss-${idx}`}
                      style={{ left: `${leftPct}%`, top: '240px' }}
                      className="absolute -translate-x-1/2 flex flex-col items-center z-10 hover:z-50 pointer-events-none"
                    >
                      <div style={{ height: `${stemHeight}px` }} className="w-[1px] bg-cyan opacity-60 pointer-events-none" />
                      <div
                        onClick={() => setSelectedEvent(e)}
                        className="pointer-events-auto cursor-pointer bg-cyan-950/95 border border-cyan text-cyan-glow px-2.5 py-1 rounded text-xs whitespace-nowrap shadow-[0_0_10px_rgba(56,189,248,0.3)] hover:scale-110 transition-transform"
                      >
                        <div className="font-bold">⚔️ {e.kills.length} Boss Kills</div>
                        <div className="text-[10px] text-slate-300">{e.sampleText}</div>
                      </div>
                    </div>
                  );
                }

                if (e.type === 'daily_boss_summary') {
                  const isSingle = e.kills.length === 1;
                  const tiers = [28, 66, 104, 142];
                  const baseStem = tiers[idx % tiers.length];
                  const jitter = getEventJitter(e.dateKey + idx, 10);
                  const stemHeight = Math.max(18, Math.min(160, baseStem + jitter));

                  return (
                    <div
                      key={`d-boss-${idx}`}
                      style={{ left: `${leftPct}%`, top: '240px' }}
                      className="absolute -translate-x-1/2 flex flex-col items-center z-10 hover:z-50 pointer-events-none"
                    >
                      <div style={{ height: `${stemHeight}px` }} className="w-[1px] bg-cyan opacity-60 pointer-events-none" />
                      <div
                        onClick={() => setSelectedEvent(e)}
                        className="pointer-events-auto cursor-pointer bg-cyan-950/95 border border-cyan text-cyan-glow px-2.5 py-1 rounded text-xs whitespace-nowrap shadow-[0_0_10px_rgba(56,189,248,0.3)] hover:scale-110 transition-transform"
                      >
                        <div className="font-bold flex items-center gap-1">
                          <span>⚔️</span>
                          <span>{isSingle ? e.kills[0].boss : `${e.kills.length} Boss Kills`}</span>
                        </div>
                        {!isSingle && <div className="text-[10px] text-slate-300 max-w-[200px] truncate">{e.sampleText}</div>}
                      </div>
                    </div>
                  );
                }

                if (e.type === 'aa_gain' && zoomLevel === 1) {
                  return (
                    <div
                      key={`aa-dot-${idx}`}
                      style={{ left: `${leftPct}%`, top: '237px' }}
                      className="absolute -translate-x-1/2 w-1.5 h-1.5 rotate-45 bg-purple border border-white/80 shadow-[0_0_4px_rgba(192,132,252,0.9)] pointer-events-none"
                    />
                  );
                }

                if (e.type === 'aa_gain' && zoomLevel >= 2) {
                  return (
                    <div
                      key={`aa-${idx}`}
                      onClick={() => setSelectedEvent(e)}
                      style={{ left: `${leftPct}%`, top: '232px' }}
                      title={`+1 AA Point in ${e.zone}`}
                      className="absolute -translate-x-1/2 w-4 h-4 rotate-45 bg-purple border border-white cursor-pointer z-10 hover:z-50 hover:scale-125 transition-transform shadow-[0_0_8px_rgba(192,132,252,0.8)]"
                    />
                  );
                }

                if (e.type === 'raid_boss_kill' || e.type === 'pvp_boss_kill') {
                  const isPvP = e.isPvP || e.type === 'pvp_boss_kill';
                  const tiers = [28, 66, 104, 142];
                  const baseStem = tiers[idx % tiers.length];
                  const jitter = getEventJitter(e.boss + idx, 12);
                  const stemHeight = Math.max(18, Math.min(160, baseStem + jitter));

                  return (
                    <div
                      key={`bkill-${idx}`}
                      style={{ left: `${leftPct}%`, top: '240px' }}
                      className="absolute -translate-x-1/2 flex flex-col items-center z-10 hover:z-50 pointer-events-none"
                    >
                      <div
                        style={{ height: `${stemHeight}px` }}
                        className={`w-[1px] ${isPvP ? 'bg-purple' : 'bg-cyan'} opacity-70 pointer-events-none`}
                      />
                      <div
                        onClick={() => setSelectedEvent(e)}
                        className={`pointer-events-auto cursor-pointer px-2 py-0.5 rounded text-[11px] font-semibold whitespace-nowrap hover:scale-110 transition-transform ${
                          isPvP ? 'bg-purple-950 border border-purple text-purple-200' : 'bg-cyan-950 border border-cyan text-cyan-200'
                        }`}
                      >
                        ⚔️ {isPvP ? '[PvP] ' : ''}{e.boss}
                      </div>
                    </div>
                  );
                }

                if (e.type === 'death') {
                  const tiers = [185, 148, 110];
                  const baseTop = tiers[idx % tiers.length];
                  const jitter = getEventJitter((e.zone || '') + idx, 10);
                  const chosenTop = Math.max(65, Math.min(195, baseTop + jitter));
                  const stemHeight = Math.max(12, 240 - chosenTop - 20);

                  return (
                    <div
                      key={`death-${idx}`}
                      style={{ left: `${leftPct}%`, top: `${chosenTop}px` }}
                      className="absolute -translate-x-1/2 flex flex-col items-center z-10 hover:z-50 pointer-events-none"
                    >
                      <div
                        onClick={() => setSelectedEvent(e)}
                        className="pointer-events-auto cursor-pointer w-5 h-5 rounded-full bg-red-950 border border-crimson flex items-center justify-center text-[10px] shadow-[0_0_8px_rgba(248,113,113,0.6)] hover:scale-125 transition-transform"
                      >
                        ☠️
                      </div>
                      <div style={{ height: `${stemHeight}px` }} className="w-[1px] bg-crimson opacity-60 pointer-events-none" />
                    </div>
                  );
                }

                if (e.type === 'daily_death_summary') {
                  const isSingle = e.totalDeaths === 1;
                  const tiers = [170, 130, 90, 50];
                  const baseTop = tiers[idx % tiers.length];
                  const jitter = getEventJitter(e.dateKey + idx, 10);
                  const chosenTop = Math.max(20, Math.min(185, baseTop + jitter));
                  const stemHeight = Math.max(14, 240 - chosenTop - 24);

                  return (
                    <div
                      key={`d-death-${idx}`}
                      style={{ left: `${leftPct}%`, top: `${chosenTop}px` }}
                      className="absolute -translate-x-1/2 flex flex-col items-center z-10 hover:z-50 pointer-events-none"
                    >
                      <div
                        onClick={() => setSelectedEvent(e)}
                        className="pointer-events-auto cursor-pointer bg-red-950/95 border border-crimson text-red-200 px-2.5 py-1 rounded text-xs whitespace-nowrap shadow-[0_0_10px_rgba(248,113,113,0.4)] hover:scale-110 transition-transform"
                      >
                        <div className="font-bold flex items-center gap-1 text-crimson">
                          <span>☠️</span>
                          <span>{isSingle ? `Died: ${e.deaths[0].killer}` : `${e.totalDeaths} Deaths`}</span>
                        </div>
                        {!isSingle && <div className="text-[10px] text-red-300 max-w-[200px] truncate">{e.sampleText}</div>}
                      </div>
                      <div style={{ height: `${stemHeight}px` }} className="w-[1px] bg-crimson opacity-60 pointer-events-none" />
                    </div>
                  );
                }

                return null;
              })}

              {/* Bottom Date Axis Strip */}
              <div className="absolute bottom-0 left-0 right-0 h-7 bg-slate-950/95 border-t border-slate-800/90 flex items-center select-none z-20">
                <div className="relative w-full h-full">
                  {interactiveTicks.map((tick, i) => {
                    const alignClass =
                      tick.pct < 0.03
                        ? 'translate-x-1'
                        : tick.pct > 0.97
                        ? '-translate-x-[calc(100%-4px)]'
                        : '-translate-x-1/2';
                    return (
                      <div
                        key={`itick-label-${i}`}
                        style={{ left: `${tick.pct * 100}%` }}
                        className={`absolute top-0 bottom-0 ${alignClass} flex flex-col items-center justify-center pointer-events-none`}
                      >
                        <div className={`w-[1px] h-1.5 mb-0.5 ${tick.isMajor ? 'bg-gold' : 'bg-slate-600'}`} />
                        <span
                          className={`text-[10px] font-mono whitespace-nowrap px-1 ${
                            tick.isMajor ? 'text-gold-soft font-bold' : 'text-slate-400 font-medium'
                          }`}
                        >
                          {tick.label}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Draggable Mini-Map Scrubber */}
            <div data-html2canvas-ignore="true" className="mt-4 pt-3 border-t border-slate-700/60">
              <div className="flex justify-between items-center text-xs text-slate-400 mb-1.5">
                <span>Timeline Scrubber (Drag or Click to Navigate)</span>
                <span>{character.dateRange.start} — {character.dateRange.end}</span>
              </div>
              <div
                ref={minimapBarRef}
                onMouseDown={handleMinimapMouseDown}
                className="h-8 bg-slate-950/80 rounded border border-slate-700 relative cursor-pointer overflow-hidden select-none"
              >
                <div
                  style={{
                    left: `${scrubberLeftPct}%`,
                    width: `${scrubberWidthPct}%`,
                  }}
                  className="absolute top-0 bottom-0 bg-gold/20 border-2 border-gold rounded cursor-grab active:cursor-grabbing transition-none backdrop-blur-sm"
                />
              </div>
            </div>

            {/* Legend Footer */}
            <div className="mt-4 pt-3 border-t border-gold/20 flex flex-wrap justify-center gap-6 text-xs text-slate-400 select-none">
              <span><strong className="text-gold-soft">👑</strong> Pinnacle First Kills</span>
              <span><strong className="text-gold">✨</strong> Epic 1.0 Weapon</span>
              <span><strong className="text-amber-400">●</strong> Milestone Dings (1–60)</span>
              <span><strong className="text-purple">◆</strong> Alternate Advancements ({data.aggregates.totalAAs} AAs)</span>
              <span><strong className="text-cyan">⚔️</strong> {data.aggregates.totalBossKills} Raid & PvP Boss Kills</span>
            </div>
      </div>

      {/* Event Detail Modal */}
      {selectedEvent && (
        <div
          onClick={() => setSelectedEvent(null)}
          className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-[100] backdrop-blur-sm"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="bg-slate-900 border-2 border-gold rounded-xl p-5 max-w-lg w-full shadow-2xl relative"
          >
            <button
              onClick={() => setSelectedEvent(null)}
              className="absolute top-3 right-4 text-slate-400 hover:text-white text-xl font-bold"
            >
              &times;
            </button>
            <h3 className="text-xl font-serif text-gold-soft font-bold mb-3 border-b border-slate-700 pb-2">
              {selectedEvent.title}
            </h3>
            <div className="space-y-2 text-sm text-slate-300">
              {selectedEvent.dateLabel && (
                <div className="flex justify-between border-b border-white/5 py-1">
                  <span className="text-slate-400">Date:</span>
                  <span className="text-slate-200 font-medium">{selectedEvent.dateLabel}</span>
                </div>
              )}
              {selectedEvent.zone && (
                <div className="flex justify-between border-b border-white/5 py-1">
                  <span className="text-slate-400">Zone:</span>
                  <span className="text-cyan font-medium">{selectedEvent.zone}</span>
                </div>
              )}
              {selectedEvent.zoneBreakdown && (
                <div className="flex justify-between border-b border-white/5 py-1">
                  <span className="text-slate-400">Zones:</span>
                  <span className="text-slate-300 text-xs text-right max-w-xs">{selectedEvent.zoneBreakdown}</span>
                </div>
              )}
              {selectedEvent.timestamp && (
                <div className="flex justify-between border-b border-white/5 py-1">
                  <span className="text-slate-400">Exact Timestamp:</span>
                  <span>{selectedEvent.timestamp}</span>
                </div>
              )}
              {selectedEvent.killer && (
                <div className="flex justify-between border-b border-white/5 py-1">
                  <span className="text-slate-400">Killer:</span>
                  <span className="text-crimson font-medium">{selectedEvent.killer}</span>
                </div>
              )}
              {selectedEvent.url && (
                <div className="flex justify-between border-b border-white/5 py-1">
                  <span className="text-slate-400">Database Entry:</span>
                  <a
                    href={selectedEvent.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-cyan hover:underline"
                  >
                    View on pqdi.cc &rarr;
                  </a>
                </div>
              )}
              {selectedEvent.kills && (
                <div className="mt-3">
                  <div className="text-gold-soft font-semibold mb-1">
                    {selectedEvent.type === 'monthly_boss_summary' ? 'Monthly Breakdown' : 'Raid Kills Breakdown'} ({selectedEvent.kills.length} kills{selectedEvent.uniqueBossCount ? ` across ${selectedEvent.uniqueBossCount} unique bosses` : ''}):
                  </div>
                  <div className="max-h-48 overflow-y-auto divide-y divide-white/5 text-xs">
                    {selectedEvent.kills.map((k: any, i: number) => (
                      <div key={i} className="py-1 flex justify-between">
                        <span className="truncate pr-2">⚔️ {k.boss}</span>
                        <span className="text-slate-400 whitespace-nowrap">{k.zone}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {selectedEvent.deaths && (
                <div className="mt-3">
                  <div className="text-crimson font-semibold mb-1">
                    Deaths Breakdown ({selectedEvent.deaths.length} deaths):
                  </div>
                  <div className="max-h-48 overflow-y-auto divide-y divide-white/5 text-xs">
                    {selectedEvent.deaths.map((d: any, i: number) => (
                      <div key={i} className="py-1 flex justify-between">
                        <span className="truncate pr-2 text-red-300">☠️ {d.killer}</span>
                        <span className="text-slate-400 whitespace-nowrap">{d.zone}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
