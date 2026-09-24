import { openDB, DBSchema, IDBPDatabase } from 'idb';
import { ParsedCharacterBundle, CharacterMetadata } from '../types/events';

interface QuarmDB extends DBSchema {
  characters: {
    key: string; // character name (lowercase)
    value: ParsedCharacterBundle;
    indexes: { 'by-updated': string };
  };
  settings: {
    key: string;
    value: any;
  };
}

const DB_NAME = 'quarm_chronicle_db';
const DB_VERSION = 2;

let dbPromise: Promise<IDBPDatabase<QuarmDB>> | null = null;

function getDb(): Promise<IDBPDatabase<QuarmDB>> {
  if (!dbPromise) {
    dbPromise = openDB<QuarmDB>(DB_NAME, DB_VERSION, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('characters')) {
          const store = db.createObjectStore('characters', { keyPath: 'character.name' });
          store.createIndex('by-updated', 'character.lastParsedAt');
        }
        if (!db.objectStoreNames.contains('settings')) {
          db.createObjectStore('settings', { keyPath: 'key' });
        }
      },
    });
  }
  return dbPromise;
}

export async function saveDirectoryHandle(handle: FileSystemDirectoryHandle): Promise<void> {
  const db = await getDb();
  await db.put('settings', { key: 'takp_dir_handle', value: handle });
}

export async function getDirectoryHandle(): Promise<FileSystemDirectoryHandle | undefined> {
  try {
    const db = await getDb();
    const entry = await db.get('settings', 'takp_dir_handle');
    return entry?.value;
  } catch {
    return undefined;
  }
}

export async function clearDirectoryHandle(): Promise<void> {
  const db = await getDb();
  await db.delete('settings', 'takp_dir_handle');
}

export async function saveCharacterStitchSettings(
  characterName: string,
  selectedFileNames: string[]
): Promise<void> {
  const db = await getDb();
  await db.put('settings', {
    key: `stitch_settings_${characterName.toLowerCase()}`,
    value: selectedFileNames,
  });
}

export async function getCharacterStitchSettings(
  characterName: string
): Promise<string[] | undefined> {
  try {
    const db = await getDb();
    const entry = await db.get('settings', `stitch_settings_${characterName.toLowerCase()}`);
    return entry?.value;
  } catch {
    return undefined;
  }
}

export async function saveCharacterBundle(bundle: ParsedCharacterBundle): Promise<void> {
  const db = await getDb();
  await db.put('characters', bundle);
}

export async function getCharacterBundle(name: string): Promise<ParsedCharacterBundle | undefined> {
  const db = await getDb();
  return db.get('characters', name);
}

export async function listSavedCharacters(): Promise<CharacterMetadata[]> {
  const db = await getDb();
  const all = await db.getAll('characters');
  return all.map((b) => b.character);
}

export async function deleteCharacterBundle(name: string): Promise<void> {
  const db = await getDb();
  await db.delete('characters', name);
}

export async function loadSampleBundle(sampleName: 'steps' | 'tweedlede'): Promise<ParsedCharacterBundle> {
  const res = await fetch(`/sample_data/${sampleName}_bundle.json`);
  if (!res.ok) {
    throw new Error(`Failed to load sample data for ${sampleName}`);
  }
  const bundle: ParsedCharacterBundle = await res.json();
  // Cache to IndexedDB
  await saveCharacterBundle(bundle);
  return bundle;
}
