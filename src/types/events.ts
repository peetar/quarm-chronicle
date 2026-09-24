export interface CharacterMetadata {
  name: string;
  lastName?: string;
  characterClass: string;
  characterRace: string;
  level: number;
  guild: string;
  dateRange: {
    start: string;
    end: string;
    startIso?: string;
    endIso?: string;
  };
  totalLogLines: number;
  lastParsedAt: string;
  logFiles?: Array<{
    fileName: string;
    sizeMb: number;
    start: string;
    end: string;
  }>;
}

export interface LevelDingEvent {
  level: number;
  type: 'level_ding' | 'ding';
  dingLevel: number;
  title: string;
  badge: string;
  zone: string;
  timestamp: string;
  date: string;
  iso?: string;
}

export interface AAGainEvent {
  level: number;
  type: 'aa_gain';
  title: string;
  banked?: number;
  zone: string;
  timestamp: string;
  date: string;
  iso?: string;
}

export interface BossKillEvent {
  level: number;
  type: 'raid_boss_kill' | 'pvp_boss_kill';
  title: string;
  boss: string;
  zone: string;
  isPinnacle: boolean;
  isPvP: boolean;
  id?: number | null;
  url?: string | null;
  timestamp: string;
  date: string;
  iso?: string;
}

export interface PinnacleFirstKillEvent {
  level: number;
  type: 'pinnacle_first';
  title: string;
  boss: string;
  zone: string;
  id?: number | null;
  url?: string | null;
  timestamp: string;
  date: string;
  iso?: string;
}

export interface DeathEvent {
  level: number;
  type: 'death';
  title: string;
  killer: string;
  zone: string;
  timestamp: string;
  date: string;
  iso?: string;
}

export interface ZoneEntryEvent {
  level: number;
  type: 'zone_first';
  title: string;
  zone: string;
  timestamp: string;
  date: string;
  iso?: string;
}

export interface GuildEvent {
  level: number;
  type: 'guild_join' | 'guild_leave';
  title: string;
  guild: string;
  action: 'joined' | 'left';
  zone: string;
  timestamp: string;
  date: string;
  iso?: string;
}

export interface EpicEvent {
  level: number;
  type: 'epic_acquired';
  title: string;
  epicClass: string;
  effect: string;
  zone: string;
  timestamp: string;
  date: string;
  iso?: string;
}

export interface SpellFirstEvent {
  level: number;
  type: 'spell_first';
  title: string;
  spell: string;
  spellClass: string;
  zone: string;
  timestamp: string;
  date: string;
  iso?: string;
}

export interface DailyZoneActivityEvent {
  level: number;
  type: 'daily_zone_activity';
  title: string;
  summary: string;
  totalTransitions: number;
  breakdown: Record<string, number>;
  date: string;
  timestamp: string;
}

export interface MonthlyBossSummary {
  type: 'monthly_boss_summary';
  monthKey: string;
  year: number;
  month: number;
  monthName: string;
  kills: BossKillEvent[];
  uniqueBossCount: number;
  sampleText: string;
  title: string;
  zoneBreakdown: string;
  timestampMs: number;
  iso: string;
}

export interface DailyBossSummary {
  type: 'daily_boss_summary';
  dateKey: string;
  dateLabel: string;
  kills: BossKillEvent[];
  uniqueBossCount: number;
  sampleText: string;
  title: string;
  zoneBreakdown: string;
  timestampMs: number;
  iso: string;
}

export interface DailyDeathSummary {
  type: 'daily_death_summary';
  dateKey: string;
  dateLabel: string;
  deaths: DeathEvent[];
  totalDeaths: number;
  topKiller: string;
  sampleText: string;
  title: string;
  zoneBreakdown: string;
  timestampMs: number;
  iso: string;
}

export interface EraMilestone {
  era: 'Classic' | 'Kunark' | 'Velious' | 'Luclin' | 'Planes of Power';
  timestamp: string;
  date: string;
  zone: string;
}

export interface CharacterAggregates {
  totalAAs: number;
  totalDeaths: number;
  totalBossKills: number;
  totalZoneTransitions: number;
  topSpellsCast: Array<{ spell: string; count: number }>;
  topTellPartners: Array<{ partner: string; sent: number; received: number; total: number }>;
  topGroupCompanions: Array<{ companion: string; count: number }>;
  topRaidCompanions: Array<{ companion: string; count: number }>;
  topSlainKillers: Array<{ killer: string; count: number }>;
  topSlainMobs: Array<{ mob: string; count: number }>;
  aaByZone: Array<{ zone: string; count: number }>;
  topRaidBossesDefeated: Array<{ boss: string; count: number; id?: number | null; url?: string | null }>;
}

export interface ParsedCharacterBundle {
  character: CharacterMetadata;
  eras: EraMilestone[];
  events: {
    level1: Array<LevelDingEvent | GuildEvent | EpicEvent | PinnacleFirstKillEvent>;
    level2: Array<AAGainEvent | ZoneEntryEvent | SpellFirstEvent>;
    level3: Array<BossKillEvent | DeathEvent | DailyZoneActivityEvent>;
  };
  aggregates: CharacterAggregates;
}
