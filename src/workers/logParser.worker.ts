import { streamLines } from './lineSplitter';
import {
  ParsedCharacterBundle,
  LevelDingEvent,
  AAGainEvent,
  BossKillEvent,
  PinnacleFirstKillEvent,
  DeathEvent,
  ZoneEntryEvent,
  GuildEvent,
  EpicEvent,
  SpellFirstEvent,
  DailyZoneActivityEvent,
  EraMilestone,
  ClassAALearnEvent,
} from '../types/events';
import CLASS_AAS from '../data/class_aas.json';

const TS_PATTERN = /^\[([A-Za-z]{3}\s+[A-Za-z]{3}\s+[\s\d]?\d\s+\d{2}:\d{2}:\d{2}\s+\d{4})\]\s*(.*)\r?$/;
const ZONE_PATTERN = /^You have entered ([^\.]+)\./i;
const DING_PATTERN = /Welcome to level (\d+)!/i;
const AA_PATTERN = /You have gained an ability point!\s*You now have (\d+) ability point(?:\(s\)|s)?\./i;
const AA_GAIN_PATTERN = /^You have gained the ability \"(?<name>[^\"]+)\" at a cost of (?<cost>\d+) ability points?\./i;
const AA_IMPROVE_PATTERN = /^You have improved (?<name>.+?)(?:\s+(?<rank>\d+))? at a cost of (?<cost>\d+) ability points?\./i;
const DEATH_SLAIN = /^You have been slain by ([^!]+)!/i;
const CAST_PATTERN = /^You begin (?:casting|singing) (.*?)\./i;
const GUILD_JOIN = /^You have joined (?!the group|the raid)(.+?)\.?$/i;
const GUILD_LEAVE = /^You are no longer a member of (.+?)\.?$/i;
const GUILD_KILL = /^Druzzil Ro tells the guild, '(?<player>.+?) of (?<guild>.+?)> has killed (?<boss>.+?) in (?<zone>.+?)!'/i;
const LOCKOUT_PATTERN = /^You have incurred a lockout for (?<boss>.+?) that expires in/i;
const LOCAL_SLAY = /^(?<target>.*?) has been slain by (?<killer>.*?)!/i;
const PVP_KILL = /^\[PVP\]\s*(?<player>.+?)\s*of\s*<(?<guild>.+?)>\s*has killed\s*(?<boss>.+?)\s*in\s*(?<zone>.+?)!/i;
const TELL_SENT = /^You told ([A-Za-z]+),\s*'(.*)'/i;
const TELL_RECV = /^([A-Za-z\s]+) tells you,\s*'(.*)'/i;
const GROUP_CHAT = /^\[Group\]\s*([A-Za-z]+):\s*(.*)/i;
const RAID_CHAT = /^\[Raid\]\s*([A-Za-z]+):\s*(.*)/i;
const BARD_SONG_DAMAGE = /has taken \d+ (?:non-melee )?damage from your (.*?)\./i;
const MEM_PATTERN = /^You have finished memorizing (.*?)\./i;

const NPC_TELL_PATTERNS = [
  // Pets (summoned & charmed)
  /\bMaster[\.!]?$/i,
  /^Attacking .* Master/i,
  /^Following you, Master/i,
  /^Guarding .* Master/i,
  /^At your service, Master/i,
  /^As you command, Master/i,
  /^I am unable to obey, Master/i,
  /^Sorry, Master/i,
  // Merchants
  /^That(?:'ll| will) be \d+/i,
  /^I(?:'ll| will) give you \d+/i,
  /^I(?:'ll| will) buy that /i,
  /^I don'?t buy /i,
  /^I don'?t want that/i,
  /^You(?:'ll| will) have to pay /i,
  /^I have nothing to give you for that/i,
  /^I cannot buy that from you/i,
  /^You cannot afford that/i,
  /^You do not have enough/i,
  /per (?:ticket|bottle|ration|flask|arrow|pattern|clay|sketches|sketch|meat)/i,
  // Bankers
  /^Welcome to my bank!/i,
  /^Come back soon!/i,
  /^You don'?t have that much money in the bank!/i,
  /^You have deposited /i,
  /^You have withdrawn /i,
  // Trainers / Guildmasters / Soulbinders
  /^You have increased your skill in /i,
  /^You have no more training points/i,
  /^You will have to achieve level /i,
  /^Welcome to the Guild of /i,
  /^Binding your soul/i,
  /^You are now bound to this location/i,
];

function isNpcTell(sender: string, text: string): boolean {
  const s = sender.trim();
  if (s.includes(' ')) return true;
  if (s && s[0] === s[0].toLowerCase()) return true;
  for (const pattern of NPC_TELL_PATTERNS) {
    if (pattern.test(text)) return true;
  }
  return false;
}

const DISC_ACTIVATIONS: Record<string, { disc: string; cls: string }> = {
  // Monk
  'You assume a stone stance.': { disc: 'Stonestance Discipline', cls: 'Monk' },
  'You assume a void stance.': { disc: 'Voiddance Discipline', cls: 'Monk' },
  'You begin to whirl.': { disc: 'Whirlwind Discipline', cls: 'Monk' },
  'You summon your inner strength.': { disc: 'Inner Flame Discipline', cls: 'Monk' },
  'You prepare to strike with furious speed.': { disc: 'Hundred Fists Discipline', cls: 'Monk' },
  'You prepare for thunderous strikes.': { disc: 'Thunderkick Discipline', cls: 'Monk' },
  // Warrior
  'You assume a defensive fighting style.': { disc: 'Defensive Discipline', cls: 'Warrior' },
  'You assume an evasive fighting style.': { disc: 'Evasive Discipline', cls: 'Warrior' },
  'You assume an aggressive fighting style.': { disc: 'Aggressive Discipline', cls: 'Warrior' },
  'You begin to throw frantic strikes.': { disc: 'Furious Discipline', cls: 'Warrior' },
  'You ready yourself to deflect incoming blows.': { disc: 'Fortitude Discipline', cls: 'Warrior' },
  'You prepare to attack with precision.': { disc: 'Precision Discipline', cls: 'Warrior' },
  'You prepare to land a fell strike.': { disc: 'Fellstrike Discipline', cls: 'Warrior' },
  'You prepare to land mighty strikes.': { disc: 'Mighty Strike Discipline', cls: 'Warrior' },
  'You begin to charge your weapons.': { disc: 'Charge Discipline', cls: 'Warrior' },
  // Ranger
  'You become hyper-focused on your archery.': { disc: 'Trueshot Discipline', cls: 'Ranger' },
  'You prepare for weapon strikes.': { disc: 'Weapon Shield Discipline', cls: 'Ranger' },
  // Rogue
  'You prepare to duel.': { disc: 'Duelist Discipline', cls: 'Rogue' },
  'You focus on your kinesthetic movements.': { disc: 'Kinesthetics Discipline', cls: 'Rogue' },
  'You become more nimble.': { disc: 'Nimble Discipline', cls: 'Rogue' },
  'You focus your aim.': { disc: 'Deadeye Discipline', cls: 'Rogue' },
  'You prepare to counterattack.': { disc: 'Counterattack Discipline', cls: 'Rogue' },
  // General / Defensive Melee
  'You prepare to resist magical attacks.': { disc: 'Resistant Discipline', cls: 'Warrior' },
  'You become fearless.': { disc: 'Fearless Discipline', cls: 'Warrior' },
  'You steel your nerves.': { disc: 'Fearless Discipline', cls: 'Warrior' },
};

const KICK_HIT_PATTERN = /^You (?:flying kick|round kick|kick) .* for \d+ points? of damage\./i;
const MARTIAL_HIT_PATTERN = /^You (?:dragon punch|tail rake|tiger claw|eagle strike) .* for \d+ points? of damage\./i;
const BACKSTAB_HIT_PATTERN = /^You backstab .* for \d+ points? of damage\./i;
const FD_FALL_PATTERN = /^([A-Za-z]+) has fallen to the ground\./i;

const WHO_ENTRY_PATTERN = /^\[(?<lvl>\d+)\s+(?<cls>[A-Za-z\s]+)\]\s+(?:(?<title>[A-Za-z]+)\s+)?(?<first>[A-Za-z0-9]+)(?:\s+(?<surname>[A-Za-z0-9]+))?(?:\s+\((?<race>[A-Za-z\s]+)\))?(?:\s+<(?<guild>[^>]+)>)?/i;
const WHO_ANON_PATTERN = /^\[(?:ANONYMOUS|ROLEPLAYING)\]\s+(?:(?<title>[A-Za-z]+)\s+)?(?<first>[A-Za-z0-9]+)(?:\s+(?<surname>[A-Za-z0-9]+))?(?:\s+\((?<race>[A-Za-z\s]+)\))?(?:\s+<(?<guild>[^>]+)>)?/i;

const VALID_EQ_CLASSES = new Set([
  'Bard', 'Cleric', 'Druid', 'Enchanter', 'Magician', 'Monk',
  'Necromancer', 'Paladin', 'Ranger', 'Rogue', 'Shadow Knight',
  'Shaman', 'Warrior', 'Wizard', 'Beastlord'
]);

function normalizeClassName(cls?: string): string | null {
  if (!cls) return null;
  const c = cls.trim().toLowerCase();
  if (c === 'shadowknight' || c === 'shadow knight') return 'Shadow Knight';
  for (const valid of VALID_EQ_CLASSES) {
    if (valid.toLowerCase() === c) return valid;
  }
  return null;
}

const KUNARK_ZONES = new Set([
  'the overthere', 'field of bone', "kurn's tower", 'lake of ill omen',
  'firiona vie', 'timorous deep', 'the burning wood', 'skyfire mountains',
  'chardok', 'ruins of sebilis', "karnor's castle", 'the emerald jungle', "trakanon's teeth"
]);

const VELIOUS_ZONES = new Set([
  'iceclad ocean', 'eastern wastes', 'the great divide', 'kael drakkel',
  'thurgadin', 'crystal caverns', 'western wastes', 'temple of veeshan',
  "siren's grotto", 'cobalt scar', 'plane of mischief'
]);

const LUCLIN_ZONES = new Set([
  'the nexus', 'nexus', 'the bazaar', 'shadow haven', "the maiden's eye",
  'the umbral plains', 'ssraeshza temple', 'vex thal', 'the fungus grove',
  'the twilight sea', 'sanctus seru', 'the dawnshroud peaks', 'akheva ruins'
]);

const POP_ZONES = new Set([
  'plane of knowledge', 'plane of tranquility', 'plane of innovation',
  'plane of disease', 'plane of nightmare', 'plane of justice', 'plane of storms',
  'plane of valor', 'plane of torment', 'plane of tactics', 'plane of air',
  'plane of fire', 'plane of water', 'plane of earth', 'plane of time'
]);

const NORM_PINNACLES: Record<string, string> = {
  'lord nagafen': 'Lord Nagafen',
  'lady vox': 'Lady Vox',
  'phara dar': 'Phara Dar',
  'tunare': 'Tunare',
  "vulak'aerr": "Vulak`Aerr",
  'vulak`aerr': "Vulak`Aerr",
  "the herald of vulak'aerr": "Vulak`Aerr",
  'the avatar of war': 'The Avatar of War',
  'avatar of war': 'The Avatar of War',
  'aten ha ra': 'Aten Ha Ra',
  'quarm': 'Quarm',
};

const SIGNATURE_SPELLS_BY_CLASS: Record<string, string[]> = {
  Enchanter: [
    'Clarity II', "Koadic's Endless Intellect", 'Boon of the Clear Mind', 'Color Slant',
    'Color Skew', 'Color Flux', 'Rapture', 'Dementia', 'Allure', 'Tashani', 'Tashania',
    'Wind of Tishani', "Boltran's Agacerie", 'Dictate', 'Mesmerize', 'Glamour of Kintaz'
  ],
  Cleric: [
    'Complete Healing', 'Greater Healing', 'Reviviscence', 'Resurrection', 'Heroic Bond',
    'Aegolism', 'Divine Intervention', 'Celestial Elixir', 'Yaulp V', 'Word of Redemption',
    'Supernal Remedy', 'Supernal Elixir', "Kazad's Mark", 'Mark of Karn'
  ],
  Bard: [
    "Selo's Accelerating Chorus", "Selo's Accelerando", "Chords of Dissonance",
    "Denon's Disruptive Discord", "Denon's Bereavement", "Selo's Chords of Cessation",
    "Cantata of Replenishment", "Cassindra's Chorus of Clarity", "Largo's Absonant Binding",
    "Fufil's Curtailing Chant", "Cantata of Soothing", "Solon's Bewitching Bravura",
    "Occlusion of Sound", "Tuyen's Chant of Flame", "Tuyen's Chant of Frost",
    "McVaxius' Berserker Crescendo", "Niv's Harmonic Melody", "Composition of Ervaj",
    "Verses of Victory", "Psalm of Veeshan", "Shauri's Sonorous Clouding", "Angstlich's Assonance"
  ],
  Necromancer: [
    'Dooming Darkness', 'Cascading Darkness', 'Cessation of Cor', 'Splurt', 'Ancient: Lifebane',
    'Funeral Pyre of Kelador', 'Vexing Mordinia', 'Mana Conversion', 'Sedulous Subversion',
    'Feign Death', 'Death Peace', 'Emissary of Thule', 'Torment of Shadows', 'Mind Wrack',
    'Levant', 'Ignite Blood', 'Defoliation', 'Bond of Death', 'Pyrocruor'
  ],
  Wizard: [
    'Sunstrike', 'Ice Spear of Solist', "Garrison's Superior Sundering", 'Draught of Fire',
    'Draught of Jiva', 'Draught of Ice', 'Rend', 'Tears of Prexus', 'Pillar of Fire', 'Pillar of Frost'
  ],
  Magician: [
    'Call of the Hero', 'Monster Summoning', 'Burnout IV', 'Muzzle of Mardu', 'Blade of the Kedge',
    'Band of Rods', 'Summon: Modulating Rod', 'Summon: Molten Orb', 'Shock of Steel'
  ],
  Druid: [
    'Protection of the Glades', 'Mask of the Stalker', 'Natureskin', "Nature's Touch",
    'Wrath of the Elements', 'Call of the Predator', 'Form of the Great Wolf', 'Succor', 'Winged Death'
  ],
  Shaman: [
    'Torpor', 'Focus of Soul', 'Avatar', 'Cannibalize IV', 'Cannibalize III', 'Cannibalize II',
    'Malo', 'Malosini', "Turgur's Insects", "Tigir's Insects", 'Pox of Bertoxxulous', 'Bane of Nife'
  ],
  Paladin: [
    'Wave of Healing', 'Divine Glory', 'Act of Valor', 'Spiritual Cleansing', "Quellious' Word of Tranquility"
  ],
  'Shadow Knight': [
    'Voice of Death', 'Voice of Darkness', 'Shroud of Death', 'Terror of Darkness',
    'Cloak of the Akheva', 'Spear of Decay'
  ],
  Ranger: [
    'Call of the Sky', 'Call of the Predator', 'Strength of Nature', 'Trueshot Discipline'
  ],
  Beastlord: [
    'Spirit of Sharik', 'Spirit of Allizewsaur', 'Spiritual Dominion', "Sha's Advantage"
  ],
  Monk: [
    'Flying Kick', 'Dragon Punch', 'Tail Rake', 'Stonestance Discipline',
    'Voiddance Discipline', 'Inner Flame Discipline', 'Whirlwind Discipline',
    'Hundred Fists Discipline', 'Thunderkick Discipline', 'Mend'
  ],
  Rogue: [
    'Backstab', 'Duelist Discipline', 'Kinesthetics Discipline', 'Nimble Discipline',
    'Deadeye Discipline', 'Counterattack Discipline'
  ],
  Warrior: [
    'Defensive Discipline', 'Evasive Discipline', 'Fortitude Discipline', 'Furious Discipline',
    'Aggressive Discipline', 'Precision Discipline', 'Fellstrike Discipline', 'Mighty Strike Discipline'
  ],
};

const SPELL_TO_CLASS: Record<string, string> = {};
for (const [cls, spells] of Object.entries(SIGNATURE_SPELLS_BY_CLASS)) {
  for (const sp of spells) {
    SPELL_TO_CLASS[sp.toLowerCase()] = cls;
  }
}

const EPICS_REF: Record<string, { weapons: string[]; effect: string }> = {
  Bard: { weapons: ['Singing Short Sword'], effect: 'Dance of the Blade' },
  Cleric: { weapons: ["Water Sprinkler of Nem'Ankh", 'Water Sprinkler of Nem`Ankh', 'Water Sprinkler of Nem Ankh'], effect: 'Reviviscence' },
  Druid: { weapons: ["Nature Walker's Scimitar", "Nature Walker`s Scimitar", "Nature Walkers Scimitar"], effect: 'Wrath of Nature' },
  Enchanter: { weapons: ['Staff of the Serpent'], effect: 'Speed of the Shissar' },
  Magician: { weapons: ['Orb of Mastery'], effect: 'Manifest Elements' },
  Monk: { weapons: ['Celestial Fists'], effect: 'Celestial Tranquility' },
  Necromancer: { weapons: ['Scythe of the Shadowed Soul'], effect: 'Tormenting Darkness' },
  Paladin: { weapons: ['Fiery Defender'], effect: 'Holy Order' },
  Ranger: { weapons: ['Swiftwind', 'Earthcaller'], effect: 'Swift Spirit & Earthcall' },
  Rogue: { weapons: ['Ragebringer'], effect: 'Seething Fury' },
  'Shadow Knight': { weapons: ["Innoruuk's Curse", "Innoruuk`s Curse", "Innoruuks Curse"], effect: 'Soul Well' },
  Shaman: { weapons: ['Spear of Fate'], effect: 'True Spirit' },
  Warrior: { weapons: ['Jagged Blade of War', 'Blade of Tactics', 'Blade of Strategy', 'Red Scabbard'], effect: 'Fury of Zek' },
  Wizard: { weapons: ['Staff of the Four'], effect: 'Barrier of Force' },
  Beastlord: { weapons: ['Claw of the Savage Spirit'], effect: 'Fury of the Beast' },
};

function normalizeBossName(name: string): string {
  let n = name.trim().replace(/`/g, "'");
  let nl = n.toLowerCase();
  if (nl.startsWith('the ')) nl = nl.slice(4).trim();
  for (const [normK, canon] of Object.entries(NORM_PINNACLES)) {
    let k = normK.replace(/`/g, "'");
    if (k.startsWith('the ')) k = k.slice(4).trim();
    if (nl === k) return canon;
  }
  return name.trim();
}

function parseEqDate(tsStr: string): { dt: Date | null; iso: string | null; dateStr: string | null } {
  try {
    const normalized = tsStr.replace(/\s+/g, ' ');
    const dt = new Date(normalized);
    if (isNaN(dt.getTime())) return { dt: null, iso: null, dateStr: null };
    const dateStr = dt.toISOString().split('T')[0];
    return { dt, iso: dt.toISOString(), dateStr };
  } catch {
    return { dt: null, iso: null, dateStr: null };
  }
}

interface RawBossSignal {
  dt: Date;
  boss: string;
  type: string;
  ts: string;
  zone: string;
  isPvP: boolean;
}

async function inspectFileBounds(file: File): Promise<{
  file: File;
  firstDt: Date | null;
  lastDt: Date | null;
  firstTs: string | null;
  lastTs: string | null;
}> {
  let firstDt: Date | null = null;
  let lastDt: Date | null = null;
  let firstTs: string | null = null;
  let lastTs: string | null = null;

  if (file.size > 0) {
    try {
      // First 64 KB
      const headSlice = file.slice(0, Math.min(file.size, 65536));
      const headText = await headSlice.text();
      for (const rawLine of headText.split('\n')) {
        const line = rawLine.replace(/\r$/, '');
        const m = TS_PATTERN.exec(line);
        if (m) {
          const d = new Date(m[1].replace(/\s+/g, ' '));
          if (!isNaN(d.getTime())) {
            firstDt = d;
            firstTs = m[1];
            break;
          }
        }
      }

      // Last 64 KB
      const tailStart = Math.max(0, file.size - 65536);
      const tailSlice = file.slice(tailStart, file.size);
      const tailText = await tailSlice.text();
      const tailLines = tailText.split('\n');
      for (let i = tailLines.length - 1; i >= 0; i--) {
        const line = tailLines[i].replace(/\r$/, '');
        const m = TS_PATTERN.exec(line);
        if (m) {
          const d = new Date(m[1].replace(/\s+/g, ' '));
          if (!isNaN(d.getTime())) {
            lastDt = d;
            lastTs = m[1];
            break;
          }
        }
      }
    } catch {
      // Ignore slice errors
    }
  }

  return { file, firstDt, lastDt, firstTs, lastTs };
}

self.onmessage = async (event: MessageEvent) => {
  const { files: inputFiles, file, characterNameHint, npcDatabase } = event.data;
  const rawFiles: File[] = inputFiles && inputFiles.length > 0 ? inputFiles : (file ? [file] : []);

  if (rawFiles.length === 0) {
    self.postMessage({ type: 'ERROR', error: 'No files provided' });
    return;
  }

  try {
    let characterName = characterNameHint;
    if (!characterName) {
      const match = rawFiles[0].name.match(/^eqlog_([A-Za-z0-9]+)_/i);
      characterName = match ? match[1] : 'Unknown';
    }

    // Inspect date bounds for each file to order them chronologically
    const inspected = await Promise.all(rawFiles.map(inspectFileBounds));
    inspected.sort((a, b) => {
      const tA = a.firstDt ? a.firstDt.getTime() : Infinity;
      const tB = b.firstDt ? b.firstDt.getTime() : Infinity;
      if (tA !== tB) return tA - tB;
      const endA = a.lastDt ? a.lastDt.getTime() : 0;
      const endB = b.lastDt ? b.lastDt.getTime() : 0;
      return endB - endA; // Longest file first if same start date
    });

    let lineCount = 0;
    let bytesRead = 0;
    const totalBytes = inspected.reduce((acc, f) => acc + f.file.size, 0) || 1;
    let lastProgressTime = performance.now();
    const startTime = performance.now();

    // Trackers
    let firstTs: string | null = null;
    let lastTs: string | null = null;
    let firstIso: string | null = null;
    let lastIso: string | null = null;
    let firstDate: string | null = null;
    let lastDate: string | null = null;

    let currentZone = 'Unknown';
    const seenLevels = new Set<number>();
    const seenZones = new Set<string>();
    const candidateEpics: Record<string, EpicEvent> = {};
    let bardSongsEnded = 0;
    let bardSeloPulses = 0;
    const bardSongsMemorized: Record<string, number> = {};
    const knownGuilds = new Set<string>();

    // Martial abilities & Feign Death state
    let monkKicks = 0;
    let mendSuccesses = 0;
    let mendFailures = 0;
    let bindWoundsCount = 0;
    let fdFailedOrBroken = 0;
    let deathsAfterFailedFd = 0;
    let lastFailedFdMs = 0;

    // /who command tracking (Tier 1)
    const whoClassVotes: Record<string, number> = {};
    const whoRaceVotes: Record<string, number> = {};
    let whoMaxLevel = 0;
    let whoLatestGuild: string | null = null;

    // Ability & spell scoring (Tier 3)
    const classAbilityScores: Record<string, number> = {};
    for (const cls of VALID_EQ_CLASSES) {
      classAbilityScores[cls] = 0;
    }

    // First spell seen tracker (buffered until class is known)
    const firstSpellSeen = new Map<string, { spell: string; timestamp: string; date: string; iso?: string; zone: string }>();

    // Event collections
    const level1Events: Array<LevelDingEvent | GuildEvent | EpicEvent | PinnacleFirstKillEvent> = [];
    const level2Events: Array<AAGainEvent | ZoneEntryEvent | SpellFirstEvent | ClassAALearnEvent> = [];
    const level3Events: Array<BossKillEvent | DeathEvent | DailyZoneActivityEvent> = [];

    // Aggregates buffers
    const dailyZoneEntries: Record<string, Record<string, number>> = {};
    const rawBossEvents: RawBossSignal[] = [];
    const spellCounts: Record<string, number> = {};
    const tellCounts: Record<string, { sent: number; received: number; total: number }> = {};
    const knownNpcSenders = new Set<string>();
    const groupCompanions: Record<string, number> = {};
    const raidCompanions: Record<string, number> = {};
    const deathKillers: Record<string, number> = {};

    const eraFirsts: Record<string, { timestamp: string; date: string; zone: string } | null> = {
      Classic: null,
      Kunark: null,
      Velious: null,
      Luclin: null,
      'Planes of Power': null,
    };

    // Multi-file boundary stitching & de-duplication state
    let maxSeenTimestampMs = 0;
    const boundaryLines = new Set<string>();

    for (const info of inspected) {
      const stream = info.file.stream();

      for await (const line of streamLines(stream)) {
        bytesRead += line.length + 1;

        // Throttle progress updates to ~10 times per second
        const now = performance.now();
        if (now - lastProgressTime > 100) {
          const elapsedSec = (now - startTime) / 1000;
          const linesPerSec = elapsedSec > 0 ? Math.round(lineCount / elapsedSec) : 0;
          self.postMessage({
            type: 'PROGRESS',
            linesProcessed: lineCount,
            bytesRead,
            totalBytes,
            percent: Math.min(100, Math.round((bytesRead / totalBytes) * 100)),
            linesPerSec,
          });
          lastProgressTime = now;
        }

        if (line.charCodeAt(0) !== 91) continue; // Must start with '['

        const match = TS_PATTERN.exec(line);
        if (!match) continue;
        const ts = match[1];
        const msg = match[2];
        const lineDt = new Date(ts.replace(/\s+/g, ' '));
        const lineMs = lineDt.getTime();
        if (isNaN(lineMs)) continue;

        // Boundary de-duplication across files
        if (maxSeenTimestampMs > 0) {
          if (lineMs < maxSeenTimestampMs) {
            continue; // Duplicate from an earlier file
          }
          if (lineMs === maxSeenTimestampMs) {
            if (boundaryLines.has(line)) {
              continue; // Duplicate exact line at seam
            }
          }
        }

        if (lineMs > maxSeenTimestampMs) {
          maxSeenTimestampMs = lineMs;
          boundaryLines.clear();
          boundaryLines.add(line);
        } else if (lineMs === maxSeenTimestampMs) {
          boundaryLines.add(line);
        }

        lineCount++;
        lastTs = ts;
        const { dt, iso, dateStr } = parseEqDate(ts);
        if (!firstTs) {
          firstTs = ts;
          firstIso = iso;
          firstDate = dateStr;
        }
        if (iso) lastIso = iso;
        if (dateStr) lastDate = dateStr;

      // ------------------------------------------------------------------
      // /who command lines & Anonymous/Roleplaying inspections (Tier 1)
      // ------------------------------------------------------------------
      if (msg.charCodeAt(0) === 91) {
        if (
          !msg.startsWith('[Group]') &&
          !msg.startsWith('[Raid]') &&
          !msg.startsWith('[Guild]') &&
          !msg.startsWith('[Tell]') &&
          !msg.startsWith('[PVP]')
        ) {
          const wm = WHO_ENTRY_PATTERN.exec(msg);
          if (wm && wm.groups) {
            const first = wm.groups.first.toLowerCase();
            const title = (wm.groups.title || '').toLowerCase();
            const charLower = characterName.toLowerCase();
            if (first === charLower || title === charLower) {
              const normCls = normalizeClassName(wm.groups.cls);
              if (normCls) {
                whoClassVotes[normCls] = (whoClassVotes[normCls] || 0) + 1;
              }
              const lvl = parseInt(wm.groups.lvl, 10);
              if (!isNaN(lvl)) {
                whoMaxLevel = Math.max(whoMaxLevel, lvl);
              }
              const race = wm.groups.race?.trim();
              if (race && race.toLowerCase() !== 'unknown') {
                whoRaceVotes[race] = (whoRaceVotes[race] || 0) + 1;
              }
              const g = wm.groups.guild?.trim();
              if (g) {
                whoLatestGuild = g;
                knownGuilds.add(g.toLowerCase());
              }
            }
          } else {
            const am = WHO_ANON_PATTERN.exec(msg);
            if (am && am.groups) {
              const first = am.groups.first.toLowerCase();
              const title = (am.groups.title || '').toLowerCase();
              const charLower = characterName.toLowerCase();
              if (first === charLower || title === charLower) {
                const race = am.groups.race?.trim();
                if (race && race.toLowerCase() !== 'unknown') {
                  whoRaceVotes[race] = (whoRaceVotes[race] || 0) + 1;
                }
                const g = am.groups.guild?.trim();
                if (g) {
                  whoLatestGuild = g;
                  knownGuilds.add(g.toLowerCase());
                }
              }
            }
          }
        }
      }

      // ------------------------------------------------------------------
      // Zone Transitions
      // ------------------------------------------------------------------
      if (msg.startsWith('You have entered ')) {
        const zm = ZONE_PATTERN.exec(msg);
        if (zm) {
          const zname = zm[1].trim();
          if (zname.toLowerCase().includes('arena (pvp) area')) continue;
          currentZone = zname;

          if (!eraFirsts.Classic) {
            eraFirsts.Classic = { timestamp: ts, date: dateStr || '', zone: currentZone };
          }

          if (!seenZones.has(currentZone)) {
            seenZones.add(currentZone);
            level2Events.push({
              level: 2,
              type: 'zone_first',
              title: `Discovered ${currentZone}`,
              zone: currentZone,
              timestamp: ts,
              date: dateStr || '',
              iso: iso || undefined,
            });
          }

          const zl = currentZone.toLowerCase();
          if (!eraFirsts.Kunark && [...KUNARK_ZONES].some((kz) => zl.includes(kz))) {
            eraFirsts.Kunark = { timestamp: ts, date: dateStr || '', zone: currentZone };
          }
          if (!eraFirsts.Velious && [...VELIOUS_ZONES].some((vz) => zl.includes(vz))) {
            eraFirsts.Velious = { timestamp: ts, date: dateStr || '', zone: currentZone };
          }
          if (!eraFirsts.Luclin && [...LUCLIN_ZONES].some((lz) => zl.includes(lz))) {
            eraFirsts.Luclin = { timestamp: ts, date: dateStr || '', zone: currentZone };
          }
          if (!eraFirsts['Planes of Power'] && [...POP_ZONES].some((pz) => zl.includes(pz))) {
            eraFirsts['Planes of Power'] = { timestamp: ts, date: dateStr || '', zone: currentZone };
          }

          if (dateStr) {
            if (!dailyZoneEntries[dateStr]) dailyZoneEntries[dateStr] = {};
            dailyZoneEntries[dateStr][currentZone] = (dailyZoneEntries[dateStr][currentZone] || 0) + 1;
          }
        }
        continue;
      }

      // ------------------------------------------------------------------
      // Level Dings (Level 1)
      // ------------------------------------------------------------------
      if (msg.includes('Welcome to level ')) {
        const dm = DING_PATTERN.exec(msg);
        if (dm) {
          const lvl = parseInt(dm[1], 10);
          if (!seenLevels.has(lvl)) {
            seenLevels.add(lvl);
            const { iso, dateStr } = parseEqDate(ts);
            level1Events.push({
              level: 1,
              type: 'level_ding',
              dingLevel: lvl,
              title: `Level ${lvl}`,
              badge: String(lvl),
              zone: currentZone,
              timestamp: ts,
              date: dateStr || '',
              iso: iso || undefined,
            });
          }
        }
        continue;
      }

      // ------------------------------------------------------------------
      // Guild Joins / Departures (Level 1)
      // ------------------------------------------------------------------
      if (msg.startsWith('You have joined ')) {
        const gjm = GUILD_JOIN.exec(msg);
        if (gjm) {
          const gName = gjm[1].trim();
          knownGuilds.add(gName.toLowerCase());
          const { iso, dateStr } = parseEqDate(ts);
          level1Events.push({
            level: 1,
            type: 'guild_join',
            title: `Joined <${gName}>`,
            guild: gName,
            action: 'joined',
            zone: currentZone,
            timestamp: ts,
            date: dateStr || '',
            iso: iso || undefined,
          });
        }
        continue;
      } else if (msg.startsWith('You are no longer a member of ')) {
        const glm = GUILD_LEAVE.exec(msg);
        if (glm) {
          const gName = glm[1].trim();
          const { iso, dateStr } = parseEqDate(ts);
          level1Events.push({
            level: 1,
            type: 'guild_leave',
            title: `Left <${gName}>`,
            guild: gName,
            action: 'left',
            zone: currentZone,
            timestamp: ts,
            date: dateStr || '',
            iso: iso || undefined,
          });
        }
        continue;
      }

      // ------------------------------------------------------------------
      // Epic Acquisition (Level 1)
      // ------------------------------------------------------------------
      const ml = msg.toLowerCase();
      for (const [clsName, edata] of Object.entries(EPICS_REF)) {
        if (!candidateEpics[clsName]) {
          const matchedWeapon = edata.weapons.find((w) => ml.includes(w.toLowerCase()));
          if (matchedWeapon) {
            if (
              ml.includes('you say to your guild') ||
              ml.includes('you have looted') ||
              ml.includes('worthy') ||
              ml.includes('primary:')
            ) {
              const { iso, dateStr } = parseEqDate(ts);
              candidateEpics[clsName] = {
                level: 1,
                type: 'epic_acquired',
                title: matchedWeapon,
                epicClass: `${clsName} Epic 1.0`,
                effect: edata.effect,
                zone: currentZone,
                timestamp: ts,
                date: dateStr || '',
                iso: iso || undefined,
              };
            }
          }
        }
      }

      // ------------------------------------------------------------------
      // AA Gains (Level 2)
      // ------------------------------------------------------------------
      if (msg.includes('You have gained an ability point!')) {
        const am = AA_PATTERN.exec(msg);
        const banked = am ? parseInt(am[1], 10) : undefined;
        const { iso, dateStr } = parseEqDate(ts);
        level2Events.push({
          level: 2,
          type: 'aa_gain',
          title: banked !== undefined ? `+1 AA Point (${banked} banked)` : '+1 AA Point',
          banked,
          zone: currentZone,
          timestamp: ts,
          date: dateStr || '',
          iso: iso || undefined,
        });
        continue;
      }

      // ------------------------------------------------------------------
      // Class-based AA Learning & Improvements (Level 1 Milestone)
      // ------------------------------------------------------------------
      if (msg.startsWith('You have gained the ability "') || msg.startsWith('You have improved ')) {
        let rawName = '';
        let rank = 1;
        let cost = 0;

        if (msg.startsWith('You have gained the ability "')) {
          const gm = AA_GAIN_PATTERN.exec(msg);
          if (gm && gm.groups) {
            rawName = gm.groups.name.trim();
            cost = parseInt(gm.groups.cost, 10);
            rank = 1;
          }
        } else {
          const im = AA_IMPROVE_PATTERN.exec(msg);
          if (im && im.groups) {
            rawName = im.groups.name.trim();
            cost = parseInt(im.groups.cost, 10);
            rank = im.groups.rank ? parseInt(im.groups.rank, 10) : 2;
          }
        }

        if (rawName) {
          const aaInfo = (CLASS_AAS as Record<string, any>)[rawName.toLowerCase()];
          if (aaInfo) {
            const { iso, dateStr } = parseEqDate(ts);
            const rankLabel = rank > 1 ? ` Rank ${rank}` : '';
            const title = `${aaInfo.name}${rankLabel} (${cost} AA${cost === 1 ? '' : 's'})`;

            level2Events.push({
              level: 2,
              type: 'class_aa_learn',
              title,
              abilityName: aaInfo.name,
              rank,
              cost,
              category: aaInfo.category,
              classes: aaInfo.classes,
              description: aaInfo.description,
              zone: currentZone,
              timestamp: ts,
              date: dateStr || '',
              iso: iso || undefined,
            });

            // Class inference scoring
            const classTokens = aaInfo.classes.split(/[,/\s+]+/).map((c: string) => c.trim().toUpperCase());
            const classMap: Record<string, string> = {
              WAR: 'Warrior', CLR: 'Cleric', PAL: 'Paladin', RNG: 'Ranger',
              SHD: 'Shadow Knight', DRU: 'Druid', MNK: 'Monk', BRD: 'Bard',
              ROG: 'Rogue', SHM: 'Shaman', NEC: 'Necromancer', WIZ: 'Wizard',
              MAG: 'Magician', ENC: 'Enchanter', BST: 'Beastlord'
            };
            for (const tok of classTokens) {
              const fullCls = classMap[tok];
              if (fullCls) {
                classAbilityScores[fullCls] = (classAbilityScores[fullCls] || 0) + (classTokens.length === 1 ? 25 : 10);
              }
            }
          }
        }
        continue;
      }

      // ------------------------------------------------------------------
      // Spells, Songs & Melodies
      // ------------------------------------------------------------------
      if (msg === 'Your song ends.') {
        bardSongsEnded++;
        classAbilityScores['Bard'] = (classAbilityScores['Bard'] || 0) + 2;
        continue;
      }

      if (msg === 'Your feet move faster.') {
        bardSeloPulses++;
        const sName = "Selo's Accelerating Chorus";
        spellCounts[sName] = (spellCounts[sName] || 0) + 1;
        classAbilityScores['Bard'] = (classAbilityScores['Bard'] || 0) + 2;
        if (!firstSpellSeen.has(sName)) {
          const { iso, dateStr } = parseEqDate(ts);
          firstSpellSeen.set(sName, {
            spell: sName,
            timestamp: ts,
            date: dateStr || '',
            iso: iso || undefined,
            zone: currentZone,
          });
        }
        continue;
      }

      if (msg.includes('damage from your ')) {
        const bdm = BARD_SONG_DAMAGE.exec(msg);
        if (bdm) {
          const sName = bdm[1].replace(/`/g, "'").trim();
          spellCounts[sName] = (spellCounts[sName] || 0) + 1;
          classAbilityScores['Bard'] = (classAbilityScores['Bard'] || 0) + 2;
          if (!firstSpellSeen.has(sName)) {
            const { iso, dateStr } = parseEqDate(ts);
            firstSpellSeen.set(sName, {
              spell: sName,
              timestamp: ts,
              date: dateStr || '',
              iso: iso || undefined,
              zone: currentZone,
            });
          }
          continue;
        }
      }

      if (msg.startsWith('You have finished memorizing ')) {
        const mm = MEM_PATTERN.exec(msg);
        if (mm) {
          const sName = mm[1].replace(/`/g, "'").trim();
          bardSongsMemorized[sName] = (bardSongsMemorized[sName] || 0) + 1;
          if (!firstSpellSeen.has(sName)) {
            const { iso, dateStr } = parseEqDate(ts);
            firstSpellSeen.set(sName, {
              spell: sName,
              timestamp: ts,
              date: dateStr || '',
              iso: iso || undefined,
              zone: currentZone,
            });
          }
        }
        continue;
      }

      if (msg.startsWith('You begin ')) {
        if (msg.startsWith('You begin playing a melody.')) {
          classAbilityScores['Bard'] = (classAbilityScores['Bard'] || 0) + 10;
        } else if (msg.startsWith('You begin singing ')) {
          classAbilityScores['Bard'] = (classAbilityScores['Bard'] || 0) + 10;
          const cm = CAST_PATTERN.exec(msg);
          if (cm) {
            const sName = cm[1].replace(/`/g, "'").trim();
            spellCounts[sName] = (spellCounts[sName] || 0) + 1;
            if (!firstSpellSeen.has(sName)) {
              const { iso, dateStr } = parseEqDate(ts);
              firstSpellSeen.set(sName, {
                spell: sName,
                timestamp: ts,
                date: dateStr || '',
                iso: iso || undefined,
                zone: currentZone,
              });
            }
          }
        } else {
          const cm = CAST_PATTERN.exec(msg);
          if (cm) {
            const sName = cm[1].replace(/`/g, "'").trim();
            spellCounts[sName] = (spellCounts[sName] || 0) + 1;
            const spCls = SPELL_TO_CLASS[sName.toLowerCase()];
            if (spCls) {
              classAbilityScores[spCls] = (classAbilityScores[spCls] || 0) + 5;
            }
            if (!firstSpellSeen.has(sName)) {
              const { iso, dateStr } = parseEqDate(ts);
              firstSpellSeen.set(sName, {
                spell: sName,
                timestamp: ts,
                date: dateStr || '',
                iso: iso || undefined,
                zone: currentZone,
              });
            }
          }
        }
        continue;
      }

      // ------------------------------------------------------------------
      // Disciplines & Combat Abilities (Melee & Hybrid)
      // ------------------------------------------------------------------
      const discInfo = DISC_ACTIVATIONS[msg];
      if (discInfo) {
        spellCounts[discInfo.disc] = (spellCounts[discInfo.disc] || 0) + 1;
        classAbilityScores[discInfo.cls] = (classAbilityScores[discInfo.cls] || 0) + 10;
        if (!firstSpellSeen.has(discInfo.disc)) {
          const { iso, dateStr } = parseEqDate(ts);
          firstSpellSeen.set(discInfo.disc, {
            spell: discInfo.disc,
            timestamp: ts,
            date: dateStr || '',
            iso: iso || undefined,
            zone: currentZone,
          });
        }
        continue;
      }

      // Bandaging
      if (msg === 'The bandaging is complete.') {
        bindWoundsCount++;
        spellCounts['Bind Wound'] = (spellCounts['Bind Wound'] || 0) + 1;
        if (!firstSpellSeen.has('Bind Wound')) {
          const { iso, dateStr } = parseEqDate(ts);
          firstSpellSeen.set('Bind Wound', {
            spell: 'Bind Wound',
            timestamp: ts,
            date: dateStr || '',
            iso: iso || undefined,
            zone: currentZone,
          });
        }
        continue;
      }

      // Mend (Monk)
      if (msg.includes('You mend your wounds and heal some damage')) {
        mendSuccesses++;
        spellCounts['Mend'] = (spellCounts['Mend'] || 0) + 1;
        classAbilityScores['Monk'] = (classAbilityScores['Monk'] || 0) + 10;
        if (!firstSpellSeen.has('Mend')) {
          const { iso, dateStr } = parseEqDate(ts);
          firstSpellSeen.set('Mend', {
            spell: 'Mend',
            timestamp: ts,
            date: dateStr || '',
            iso: iso || undefined,
            zone: currentZone,
          });
        }
        continue;
      } else if (msg.includes('You have worsened your wounds!') || msg.includes('You have failed to mend your wounds')) {
        mendFailures++;
        classAbilityScores['Monk'] = (classAbilityScores['Monk'] || 0) + 10;
        continue;
      }

      // Feign Death Fail / Spell Broken (Monk, Necromancer, Shadow Knight)
      if (msg === 'You are no longer feigning death, because a spell hit you.') {
        fdFailedOrBroken++;
        lastFailedFdMs = lineMs;
        classAbilityScores['Monk'] = (classAbilityScores['Monk'] || 0) + 5;
        classAbilityScores['Necromancer'] = (classAbilityScores['Necromancer'] || 0) + 5;
        classAbilityScores['Shadow Knight'] = (classAbilityScores['Shadow Knight'] || 0) + 5;
        continue;
      }
      const fdm = FD_FALL_PATTERN.exec(msg);
      if (fdm && fdm[1].toLowerCase() === characterName.toLowerCase()) {
        fdFailedOrBroken++;
        lastFailedFdMs = lineMs;
        classAbilityScores['Monk'] = (classAbilityScores['Monk'] || 0) + 10;
        classAbilityScores['Necromancer'] = (classAbilityScores['Necromancer'] || 0) + 10;
        classAbilityScores['Shadow Knight'] = (classAbilityScores['Shadow Knight'] || 0) + 10;
        continue;
      }

      // Kicks & Martial Arts
      if (KICK_HIT_PATTERN.test(msg)) {
        monkKicks++;
        classAbilityScores['Monk'] = (classAbilityScores['Monk'] || 0) + 2;
        const skillName = msg.startsWith('You flying kick')
          ? 'Flying Kick'
          : msg.startsWith('You round kick')
          ? 'Round Kick'
          : 'Kick';
        spellCounts[skillName] = (spellCounts[skillName] || 0) + 1;
        if (!firstSpellSeen.has(skillName)) {
          const { iso, dateStr } = parseEqDate(ts);
          firstSpellSeen.set(skillName, {
            spell: skillName,
            timestamp: ts,
            date: dateStr || '',
            iso: iso || undefined,
            zone: currentZone,
          });
        }
      } else if (MARTIAL_HIT_PATTERN.test(msg)) {
        classAbilityScores['Monk'] = (classAbilityScores['Monk'] || 0) + 2;
        const skillName = msg.startsWith('You dragon punch')
          ? 'Dragon Punch'
          : msg.startsWith('You tail rake')
          ? 'Tail Rake'
          : msg.startsWith('You tiger claw')
          ? 'Tiger Claw'
          : 'Eagle Strike';
        spellCounts[skillName] = (spellCounts[skillName] || 0) + 1;
        if (!firstSpellSeen.has(skillName)) {
          const { iso, dateStr } = parseEqDate(ts);
          firstSpellSeen.set(skillName, {
            spell: skillName,
            timestamp: ts,
            date: dateStr || '',
            iso: iso || undefined,
            zone: currentZone,
          });
        }
      } else if (BACKSTAB_HIT_PATTERN.test(msg)) {
        classAbilityScores['Rogue'] = (classAbilityScores['Rogue'] || 0) + 10;
        spellCounts['Backstab'] = (spellCounts['Backstab'] || 0) + 1;
        if (!firstSpellSeen.has('Backstab')) {
          const { iso, dateStr } = parseEqDate(ts);
          firstSpellSeen.set('Backstab', {
            spell: 'Backstab',
            timestamp: ts,
            date: dateStr || '',
            iso: iso || undefined,
            zone: currentZone,
          });
        }
      } else if (msg.startsWith('You backstab ') || msg.startsWith('You try to backstab ')) {
        classAbilityScores['Rogue'] = (classAbilityScores['Rogue'] || 0) + 5;
      } else if (msg.startsWith('You taunt ') || msg.startsWith('You have failed to taunt ')) {
        classAbilityScores['Warrior'] = (classAbilityScores['Warrior'] || 0) + 5;
        spellCounts['Taunt'] = (spellCounts['Taunt'] || 0) + 1;
      } else if (msg.includes('Harm Touch')) {
        classAbilityScores['Shadow Knight'] = (classAbilityScores['Shadow Knight'] || 0) + 10;
      } else if (msg.includes('Lay on Hands')) {
        classAbilityScores['Paladin'] = (classAbilityScores['Paladin'] || 0) + 10;
      }

      // ------------------------------------------------------------------
      // Deaths (Level 3)
      // ------------------------------------------------------------------
      if (msg.startsWith('You have been slain by ') || msg === 'You died.') {
        if (lastFailedFdMs > 0 && lineMs >= lastFailedFdMs && lineMs - lastFailedFdMs <= 30000) {
          deathsAfterFailedFd++;
          lastFailedFdMs = 0;
        }
        let killer = 'Bleeding / Environmental / Gravity';
        if (msg.startsWith('You have been slain by ')) {
          const dsm = DEATH_SLAIN.exec(msg);
          if (dsm) killer = dsm[1].trim();
        }
        deathKillers[killer] = (deathKillers[killer] || 0) + 1;
        const { iso, dateStr } = parseEqDate(ts);
        level3Events.push({
          level: 3,
          type: 'death',
          title: `Died to ${killer}`,
          killer,
          zone: currentZone,
          timestamp: ts,
          date: dateStr || '',
          iso: iso || undefined,
        });
        continue;
      }

      // ------------------------------------------------------------------
      // Tells & Social
      // ------------------------------------------------------------------
      if (msg.startsWith('You told ')) {
        const tm = TELL_SENT.exec(msg);
        if (tm) {
          const p = tm[1].trim();
          if (!tellCounts[p]) tellCounts[p] = { sent: 0, received: 0, total: 0 };
          tellCounts[p].sent++;
          tellCounts[p].total++;
        }
        continue;
      } else if (msg.includes(' tells you, ')) {
        const tm = TELL_RECV.exec(msg);
        if (tm) {
          const p = tm[1].trim();
          const text = tm[2].trim();
          if (isNpcTell(p, text)) {
            knownNpcSenders.add(p.toLowerCase());
          } else {
            if (!tellCounts[p]) tellCounts[p] = { sent: 0, received: 0, total: 0 };
            tellCounts[p].received++;
            tellCounts[p].total++;
          }
        }
        continue;
      } else if (msg.startsWith('[Group] ')) {
        const gm = GROUP_CHAT.exec(msg);
        if (gm) {
          const comp = gm[1];
          if (comp.toLowerCase() !== characterName.toLowerCase()) {
            groupCompanions[comp] = (groupCompanions[comp] || 0) + 1;
          }
        }
        continue;
      } else if (msg.startsWith('[Raid] ')) {
        const rm = RAID_CHAT.exec(msg);
        if (rm) {
          const comp = rm[1];
          if (comp.toLowerCase() !== characterName.toLowerCase()) {
            raidCompanions[comp] = (raidCompanions[comp] || 0) + 1;
          }
        }
        continue;
      }

      // ------------------------------------------------------------------
      // Boss Signals
      // ------------------------------------------------------------------
      if (msg.startsWith('You have incurred a lockout for ')) {
        const lm = LOCKOUT_PATTERN.exec(msg);
        if (lm && lm.groups) {
          const bname = lm.groups.boss.trim();
          const { dt } = parseEqDate(ts);
          if (dt) rawBossEvents.push({ dt, boss: bname, type: 'lockout', ts, zone: currentZone, isPvP: false });
        }
        continue;
      }

      if (msg.startsWith("Druzzil Ro tells the guild, '")) {
        const gkm = GUILD_KILL.exec(msg);
        if (gkm && gkm.groups) {
          const bname = gkm.groups.boss.trim();
          const bzone = gkm.groups.zone.trim();
          const inZone = bzone.toLowerCase().includes(currentZone.toLowerCase()) || currentZone.toLowerCase().includes(bzone.toLowerCase());
          const { dt } = parseEqDate(ts);
          if (inZone && dt) rawBossEvents.push({ dt, boss: bname, type: 'guild_kill', ts, zone: bzone, isPvP: false });
        }
        continue;
      }

      if (msg.startsWith('[PVP] ') && msg.includes('has killed ')) {
        const pm = PVP_KILL.exec(msg);
        if (pm && pm.groups) {
          const player = pm.groups.player.trim();
          const guild = pm.groups.guild.trim();
          const bname = pm.groups.boss.trim();
          const bzone = pm.groups.zone.trim();
          const isMe = player.toLowerCase() === characterName.toLowerCase();
          const inZone = bzone.toLowerCase().includes(currentZone.toLowerCase()) || currentZone.toLowerCase().includes(bzone.toLowerCase());
          const isGuildInZone = inZone && knownGuilds.has(guild.toLowerCase());
          const { dt } = parseEqDate(ts);
          if ((isMe || isGuildInZone) && dt) {
            rawBossEvents.push({ dt, boss: bname, type: 'pvp_kill', ts, zone: bzone, isPvP: true });
          }
        }
        continue;
      }

      if (msg.includes('has been slain by')) {
        const sm = LOCAL_SLAY.exec(msg);
        if (sm && sm.groups) {
          const target = sm.groups.target.trim();
          const normTgt = normalizeBossName(target);
          if (Object.values(NORM_PINNACLES).includes(normTgt) || target.toLowerCase().includes('vulak')) {
            const { dt } = parseEqDate(ts);
            if (dt) rawBossEvents.push({ dt, boss: normTgt, type: 'local_slay', ts, zone: currentZone, isPvP: false });
          }
        }
        continue;
      }
    }
  }

    // ------------------------------------------------------------------
    // Cluster Boss Events (10-minute sliding window)
    // ------------------------------------------------------------------
    rawBossEvents.sort((a, b) => a.dt.getTime() - b.dt.getTime());
    const clusteredBossKills: Array<{
      boss: string;
      dt: Date;
      ts: string;
      date: string;
      iso: string;
      zone: string;
      isPinnacle: boolean;
      isPvP: boolean;
      id: number | null;
      url: string | null;
    }> = [];
    const pinnacleFirstKills = new Set<string>();

    for (const bSig of rawBossEvents) {
      const canonName = normalizeBossName(bSig.boss);
      const isMatched = clusteredBossKills.some(
        (c) => c.boss === canonName && Math.abs(bSig.dt.getTime() - c.dt.getTime()) <= 600000
      );

      if (!isMatched) {
        let npcId: number | null = null;
        let npcUrl: string | null = null;

        if (npcDatabase) {
          const cleaned = canonName.toLowerCase().replace(/`/g, "'");
          const override = npcDatabase.custom_overrides?.[cleaned];
          if (override) {
            npcId = override.id;
            npcUrl = `https://www.pqdi.cc/npc/${npcId}`;
          } else {
            const matches = npcDatabase.npcs_by_name?.[cleaned];
            if (matches && matches.length > 0) {
              npcId = matches[0].id;
              npcUrl = `https://www.pqdi.cc/npc/${npcId}`;
            }
          }
        }

        const isPinnacle = Object.values(NORM_PINNACLES).includes(canonName);
        const iso = bSig.dt.toISOString();
        const date = iso.split('T')[0];

        const killObj = {
          boss: canonName,
          dt: bSig.dt,
          ts: bSig.ts,
          date,
          iso,
          zone: bSig.zone,
          isPinnacle,
          isPvP: bSig.isPvP,
          id: npcId,
          url: npcUrl,
        };
        clusteredBossKills.push(killObj);

        // Pinnacle First Kills -> Level 1
        if (isPinnacle && !pinnacleFirstKills.has(canonName)) {
          pinnacleFirstKills.add(canonName);
          level1Events.push({
            level: 1,
            type: 'pinnacle_first',
            title: `First Kill: ${canonName}`,
            boss: canonName,
            zone: bSig.zone,
            id: npcId,
            url: npcUrl,
            timestamp: bSig.ts,
            date,
            iso,
          });
        }

        // Level 3 Boss Kill
        level3Events.push({
          level: 3,
          type: bSig.isPvP ? 'pvp_boss_kill' : 'raid_boss_kill',
          title: `Defeated ${canonName}${bSig.isPvP ? ' (PvP)' : ''}`,
          boss: canonName,
          isPinnacle,
          isPvP: bSig.isPvP,
          zone: bSig.zone,
          id: npcId,
          url: npcUrl,
          timestamp: bSig.ts,
          date,
          iso,
        });
      }
    }

    // ------------------------------------------------------------------
    // Daily Zone Activity Summaries (Level 3)
    // ------------------------------------------------------------------
    for (const [dateStr, zMap] of Object.entries(dailyZoneEntries)) {
      const entries = Object.entries(zMap).sort((a, b) => b[1] - a[1]);
      const totalTransitions = entries.reduce((acc, curr) => acc + curr[1], 0);
      const topStr = entries.slice(0, 3).map(([z, c]) => `${z} (x${c})`).join(', ');

      level3Events.push({
        level: 3,
        type: 'daily_zone_activity',
        title: `${totalTransitions} Zone Transitions`,
        summary: topStr,
        totalTransitions,
        breakdown: zMap,
        date: dateStr,
        timestamp: `${dateStr} 12:00:00`,
      });
    }

    // ------------------------------------------------------------------
    // Class & Identity Resolution (3-Tier Hierarchy)
    // ------------------------------------------------------------------
    let detectedClass = 'Adventurer';

    // Tier 1: Direct /who logs for this character (Highest Authority)
    const whoClassEntries = Object.entries(whoClassVotes).sort((a, b) => b[1] - a[1]);
    if (whoClassEntries.length > 0 && whoClassEntries[0][1] > 0) {
      detectedClass = whoClassEntries[0][0];
    }

    // Tier 2: Epic 1.0 Weapon / Quest Acquisition (if class unknown and unambiguous)
    if (detectedClass === 'Adventurer') {
      const candidateClasses = Object.keys(candidateEpics);
      if (candidateClasses.length === 1) {
        detectedClass = candidateClasses[0];
      }
    }

    // Tier 3: Signature Ability & Spell Scoring
    if (detectedClass === 'Adventurer') {
      const scoreEntries = Object.entries(classAbilityScores).sort((a, b) => b[1] - a[1]);
      if (scoreEntries.length > 0 && scoreEntries[0][1] > 0) {
        detectedClass = scoreEntries[0][0];
      }
    }

    // Attach Epic Milestone for the DETECTED class only (prevents cross-class loot triggers)
    if (candidateEpics[detectedClass]) {
      level1Events.push(candidateEpics[detectedClass]);
    }

    // Race resolution from /who logs
    const whoRaceEntries = Object.entries(whoRaceVotes).sort((a, b) => b[1] - a[1]);
    const detectedRace = whoRaceEntries.length > 0 ? whoRaceEntries[0][0] : '';

    // Max level resolution (highest between ding milestones and /who logs)
    const dingMaxLvl = seenLevels.size > 0 ? Math.max(...seenLevels) : 0;
    const maxLvl = Math.max(dingMaxLvl, whoMaxLevel) || 60;

    // Guild resolution (latest /who guild or latest guild join event)
    const guildEvents = level1Events.filter((e) => e.type === 'guild_join') as GuildEvent[];
    const currentGuild = guildEvents.length > 0
      ? guildEvents[guildEvents.length - 1].guild
      : (whoLatestGuild || 'None');

    // Add first-cast milestones for signature spells of the DETECTED class ONLY
    const classSigs = SIGNATURE_SPELLS_BY_CLASS[detectedClass] || [];
    for (const sig of classSigs) {
      const record = firstSpellSeen.get(sig);
      if (record) {
        const isMeleeClass = ['Monk', 'Warrior', 'Rogue'].includes(detectedClass);
        const prefix = isMeleeClass ? 'First Use' : detectedClass === 'Bard' ? 'First Performance' : 'First Cast';
        level2Events.push({
          level: 2,
          type: 'spell_first',
          title: `${prefix}: ${sig}`,
          spell: sig,
          spellClass: detectedClass,
          zone: record.zone,
          timestamp: record.timestamp,
          date: record.date,
          iso: record.iso,
        });
      }
    }

    // Sort all events chronologically (after adding class signature spells)
    const sortFn = (a: any, b: any) => (a.iso || a.date || '9999').localeCompare(b.iso || b.date || '9999');
    level1Events.sort(sortFn);
    level2Events.sort(sortFn);
    level3Events.sort(sortFn);

    // Eras
    const eras: EraMilestone[] = [];
    for (const [eraName, edata] of Object.entries(eraFirsts)) {
      if (edata) {
        eras.push({
          era: eraName as any,
          timestamp: edata.timestamp,
          date: edata.date,
          zone: edata.zone,
        });
      }
    }

    // For bards, incorporate utility songs memorized that aren't already represented in spellCounts
    if (detectedClass === 'Bard') {
      for (const [song, memCount] of Object.entries(bardSongsMemorized)) {
        if (!spellCounts[song]) {
          spellCounts[song] = memCount;
        }
      }
    }

    // Top aggregates
    const topSpells = Object.entries(spellCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 20)
      .map(([spell, count]) => ({ spell, count }));

    const topTells = Object.entries(tellCounts)
      .filter(([partner]) => {
        const p = partner.trim();
        return !knownNpcSenders.has(p.toLowerCase()) && !p.includes(' ') && p[0] === p[0].toUpperCase();
      })
      .map(([partner, c]) => ({ partner, sent: c.sent, received: c.received, total: c.total }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 6);

    const topGroup = Object.entries(groupCompanions)
      .map(([companion, count]) => ({ companion, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 6);

    const topRaid = Object.entries(raidCompanions)
      .map(([companion, count]) => ({ companion, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 6);

    const topKillers = Object.entries(deathKillers)
      .map(([killer, count]) => ({ killer, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    const aaZoneCounts: Record<string, number> = {};
    for (const aa of level2Events) {
      if (aa.type === 'aa_gain') {
        aaZoneCounts[aa.zone] = (aaZoneCounts[aa.zone] || 0) + 1;
      }
    }
    const topAAZones = Object.entries(aaZoneCounts)
      .map(([zone, count]) => ({ zone, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8);

    const bossKillCounts: Record<string, number> = {};
    for (const bk of level3Events) {
      if (bk.type === 'raid_boss_kill' || bk.type === 'pvp_boss_kill') {
        bossKillCounts[bk.boss] = (bossKillCounts[bk.boss] || 0) + 1;
      }
    }
    const topBosses = Object.entries(bossKillCounts)
      .map(([boss, count]) => ({ boss, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    const totalAAs = level2Events.filter((e) => e.type === 'aa_gain').length;
    const totalDeaths = level3Events.filter((e) => e.type === 'death').length;
    const totalBossKills = level3Events.filter((e) => e.type === 'raid_boss_kill' || e.type === 'pvp_boss_kill').length;
    const totalZoneTransitions = Object.values(dailyZoneEntries).reduce(
      (acc, zMap) => acc + Object.values(zMap).reduce((a, c) => a + c, 0),
      0
    );

    const bundle: ParsedCharacterBundle = {
      character: {
        name: characterName,
        characterClass: detectedClass,
        characterRace: detectedRace,
        level: maxLvl,
        guild: currentGuild,
        dateRange: {
          start: firstDate || 'Unknown',
          end: lastDate || 'Unknown',
          startIso: firstIso || undefined,
          endIso: lastIso || undefined,
        },
        totalLogLines: lineCount,
        lastParsedAt: new Date().toISOString(),
        logFiles: inspected.map((i) => ({
          fileName: i.file.name,
          sizeMb: Math.round((i.file.size / (1024 * 1024)) * 10) / 10,
          start: i.firstTs || 'Unknown',
          end: i.lastTs || 'Unknown',
        })),
      },
      eras,
      events: {
        level1: level1Events,
        level2: level2Events,
        level3: level3Events,
      },
      aggregates: {
        totalAAs,
        totalDeaths,
        totalBossKills,
        totalZoneTransitions,
        bardSongsTwisted: bardSongsEnded > 0 ? bardSongsEnded : undefined,
        bardSeloPulses: bardSeloPulses > 0 ? bardSeloPulses : undefined,
        monkKicks: monkKicks > 0 ? monkKicks : undefined,
        mendSuccesses: mendSuccesses > 0 ? mendSuccesses : undefined,
        mendFailures: mendFailures > 0 ? mendFailures : undefined,
        bindWoundsCount: bindWoundsCount > 0 ? bindWoundsCount : undefined,
        fdFailedOrBroken: fdFailedOrBroken > 0 ? fdFailedOrBroken : undefined,
        deathsAfterFailedFd: deathsAfterFailedFd > 0 ? deathsAfterFailedFd : undefined,
        topSpellsCast: topSpells,
        topTellPartners: topTells,
        topGroupCompanions: topGroup,
        topRaidCompanions: topRaid,
        topSlainKillers: topKillers,
        topSlainMobs: [],
        aaByZone: topAAZones,
        topRaidBossesDefeated: topBosses,
      },
    };

    self.postMessage({ type: 'DONE', bundle });
  } catch (err: any) {
    self.postMessage({ type: 'ERROR', error: err?.message || String(err) });
  }
};
