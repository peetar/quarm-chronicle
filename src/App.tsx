import React, { useState, useEffect, useRef } from 'react';
import { ParsedCharacterBundle, CharacterMetadata } from './types/events';
import { ProjectorType } from './types/projectors';
import { CARD_REGISTRY } from './cards/registry';
import {
  saveCharacterBundle,
  getCharacterBundle,
  listSavedCharacters,
  deleteCharacterBundle,
  getDirectoryHandle,
  getCharacterStitchSettings,
} from './storage/characterStore';
import { DirectoryConnect } from './components/DirectoryConnect';
import { FileDropZone } from './components/FileDropZone';
import { ParsingProgressBar, ParsingProgress } from './components/ParsingProgressBar';
import { ProjectorBuilder } from './components/ProjectorBuilder';
import { SummaryProjector } from './projectors/SummaryProjector';
import { SlideshowProjector } from './projectors/SlideshowProjector';
import { TimelineProjector } from './projectors/TimelineProjector';
import { SecurityModal } from './components/SecurityModal';

export const App: React.FC = () => {
  const [savedCharacters, setSavedCharacters] = useState<CharacterMetadata[]>([]);
  const [selectedBundle, setSelectedBundle] = useState<ParsedCharacterBundle | null>(null);
  const [activeProjector, setActiveProjector] = useState<ProjectorType | null>(null);
  const [selectedCardIds, setSelectedCardIds] = useState<string[]>(
    CARD_REGISTRY.filter((c) => c.defaultSelected).map((c) => c.id)
  );

  const [isParsing, setIsParsing] = useState(false);
  const [parsingName, setParsingName] = useState('');
  const [parseProgress, setParseProgress] = useState<ParsingProgress | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showSecurityModal, setShowSecurityModal] = useState(false);

  const workerRef = useRef<Worker | null>(null);
  const npcDbRef = useRef<any>(null);

  // Load saved characters and NPC DB on mount
  useEffect(() => {
    refreshSavedCharacters();

    // Prefetch NPC Database for boss resolution
    fetch('/data/npc_database.json')
      .then((res) => {
        if (res.ok) return res.json();
        return null;
      })
      .then((data) => {
        if (data) npcDbRef.current = data;
      })
      .catch((err) => console.warn('Could not load NPC database:', err));
  }, []);

  const refreshSavedCharacters = async () => {
    try {
      const list = await listSavedCharacters();
      setSavedCharacters(list);
    } catch (e) {
      console.error('Failed to list characters from IndexedDB:', e);
    }
  };

  const handleSelectSavedCharacter = async (name: string) => {
    try {
      const bundle = await getCharacterBundle(name);
      if (bundle) {
        setSelectedBundle(bundle);
        setActiveProjector(null);
      }
    } catch (e: any) {
      setErrorMessage(`Failed to load ${name}: ${e.message}`);
    }
  };

  const handleDeleteSavedCharacter = async (name: string) => {
    if (confirm(`Remove cached chronicle for ${name}?`)) {
      await deleteCharacterBundle(name);
      if (selectedBundle?.character.name === name) {
        setSelectedBundle(null);
        setActiveProjector(null);
      }
      refreshSavedCharacters();
    }
  };

  const handleStartParsing = (
    fileOrFiles: File[] | File,
    characterName: string,
    autoLaunch: ProjectorType | null = null
  ) => {
    const files = Array.isArray(fileOrFiles) ? fileOrFiles : [fileOrFiles];
    if (files.length === 0) return;

    setErrorMessage(null);
    setIsParsing(true);
    setParsingName(characterName);
    const totalBytes = files.reduce((acc, f) => acc + f.size, 0) || 1;
    setParseProgress({
      linesProcessed: 0,
      bytesRead: 0,
      totalBytes,
      percent: 0,
      linesPerSec: 0,
    });

    if (workerRef.current) {
      workerRef.current.terminate();
    }

    const worker = new Worker(new URL('./workers/logParser.worker.ts', import.meta.url), {
      type: 'module',
    });
    workerRef.current = worker;

    worker.onmessage = async (e: MessageEvent) => {
      const { type, linesProcessed, bytesRead, totalBytes, percent, linesPerSec, bundle, error } = e.data;

      if (type === 'PROGRESS') {
        setParseProgress({
          linesProcessed,
          bytesRead,
          totalBytes,
          percent,
          linesPerSec,
        });
      } else if (type === 'DONE') {
        setIsParsing(false);
        setParseProgress(null);
        worker.terminate();
        workerRef.current = null;

        if (bundle) {
          await saveCharacterBundle(bundle);
          await refreshSavedCharacters();
          setSelectedBundle(bundle);
          setActiveProjector(autoLaunch);
        }
      } else if (type === 'ERROR') {
        setIsParsing(false);
        setParseProgress(null);
        setErrorMessage(error || 'Unknown parsing failure');
        worker.terminate();
        workerRef.current = null;
      }
    };

    worker.onerror = (err) => {
      setIsParsing(false);
      setParseProgress(null);
      setErrorMessage(`Worker error: ${err.message}`);
      worker.terminate();
      workerRef.current = null;
    };

    worker.postMessage({
      files,
      characterNameHint: characterName,
      npcDatabase: npcDbRef.current,
    });
  };

  const handleReparseCharacter = async () => {
    if (!selectedBundle) return;
    const charName = selectedBundle.character.name;

    try {
      const dirHandle = await getDirectoryHandle();
      if (dirHandle) {
        // @ts-ignore
        const perm = await dirHandle.requestPermission({ mode: 'read' });
        if (perm === 'granted') {
          const savedSettings = await getCharacterStitchSettings(charName);
          const charRegex = new RegExp(`^eqlog_${charName}_`, 'i');

          const matchedHandles: FileSystemFileHandle[] = [];
          // @ts-ignore
          for await (const entry of dirHandle.values()) {
            if (entry.kind === 'file' && charRegex.test(entry.name) && entry.name.endsWith('.txt')) {
              if (savedSettings && savedSettings.length > 0) {
                if (savedSettings.includes(entry.name)) {
                  matchedHandles.push(entry as FileSystemFileHandle);
                }
              } else {
                if (!entry.name.includes(' - Copy')) {
                  matchedHandles.push(entry as FileSystemFileHandle);
                }
              }
            }
          }

          if (matchedHandles.length > 0) {
            const files = await Promise.all(matchedHandles.map((h) => h.getFile()));
            handleStartParsing(files, charName, 'summary');
            return;
          }
        }
      }
    } catch (err) {
      console.warn('Auto-reparse directory check failed:', err);
    }

    // Fallback: trigger multi-file open dialog directly
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '.txt';
    input.onchange = (e: any) => {
      const files = Array.from(e.target?.files || []) as File[];
      if (files.length > 0) {
        handleStartParsing(files, charName, 'summary');
      }
    };
    input.click();
  };

  const handleRegenerateCards = () => {
    if (selectedCardIds.length === 1 && selectedCardIds[0] === 'interactive_timeline') {
      setActiveProjector('timeline');
    } else {
      setActiveProjector('summary');
    }
  };

  const handleCancelParsing = () => {
    if (workerRef.current) {
      workerRef.current.terminate();
      workerRef.current = null;
    }
    setIsParsing(false);
    setParseProgress(null);
  };

  return (
    <div className="min-h-screen bg-[#080a0f] text-slate-100 flex flex-col font-sans">
      {/* Top Application Navbar */}
      <header className="border-b border-slate-800 bg-[#0c101a]/90 backdrop-blur-md sticky top-0 z-50 px-4 py-3">
        <div className="max-w-7xl mx-auto flex flex-wrap justify-between items-center gap-4">
          <div
            className="flex items-center gap-3 cursor-pointer"
            onClick={() => {
              if (!isParsing) {
                setActiveProjector(null);
              }
            }}
          >
            <span className="text-2xl">⚔️</span>
            <div>
              <h1 className="text-base font-black text-gold tracking-wide">
                QUARM CHRONICLE
              </h1>
            </div>
          </div>

          {/* Quick Nav & Character Selection */}
          <div className="flex items-center gap-3">
            {selectedBundle && (
              <div className="flex items-center gap-2 bg-slate-900 border border-slate-700/80 px-3 py-1.5 rounded-lg text-xs">
                <span className="text-slate-400">Viewing:</span>
                <span className="text-gold-soft font-bold">{selectedBundle.character.name}</span>
                <span className="text-slate-500">({selectedBundle.character.characterClass})</span>
                <button
                  onClick={() => setActiveProjector(null)}
                  className="ml-2 text-cyan hover:underline text-[11px]"
                >
                  Configure
                </button>
              </div>
            )}

            <button
              onClick={() => {
                setSelectedBundle(null);
                setActiveProjector(null);
              }}
              className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
            >
              + Parse New Log
            </button>
          </div>
        </div>
      </header>

      {/* Main Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 space-y-6">
        {errorMessage && (
          <div className="bg-red-950/50 border border-red-800 text-red-300 p-4 rounded-xl text-sm flex justify-between items-center">
            <span>⚠️ {errorMessage}</span>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-red-400 hover:text-red-200 font-bold ml-4"
            >
              &times;
            </button>
          </div>
        )}

        {/* 1. Actively Parsing */}
        {isParsing && parseProgress && (
          <div className="max-w-3xl mx-auto py-8">
            <ParsingProgressBar
              characterName={parsingName}
              progress={parseProgress}
              onCancel={handleCancelParsing}
            />
          </div>
        )}

        {/* 2. Render Chosen Projector */}
        {!isParsing && selectedBundle && activeProjector === 'summary' && (
          <SummaryProjector
            data={selectedBundle}
            selectedCardIds={selectedCardIds}
            onBackToSelector={() => setActiveProjector(null)}
          />
        )}

        {!isParsing && selectedBundle && activeProjector === 'slideshow' && (
          <SlideshowProjector
            data={selectedBundle}
            selectedCardIds={selectedCardIds}
            onBackToSelector={() => setActiveProjector(null)}
          />
        )}

        {!isParsing && selectedBundle && activeProjector === 'timeline' && (
          <TimelineProjector
            data={selectedBundle}
            selectedCardIds={selectedCardIds}
            onBackToSelector={() => setActiveProjector(null)}
          />
        )}

        {/* 3. Render Projector Builder (when character selected, but no projector launched) */}
        {!isParsing && selectedBundle && !activeProjector && (
          <ProjectorBuilder
            bundle={selectedBundle}
            selectedCardIds={selectedCardIds}
            onChangeSelectedCardIds={setSelectedCardIds}
            onLaunchProjector={(type) => setActiveProjector(type)}
            onSwitchCharacter={() => setSelectedBundle(null)}
            onDeleteCharacter={() => handleDeleteSavedCharacter(selectedBundle.character.name)}
            onRegenerateCards={handleRegenerateCards}
            onReparseLog={handleReparseCharacter}
          />
        )}

        {/* 4. Render Log Ingestion & Demo Hub (when no character selected) */}
        {!isParsing && !selectedBundle && (
          <div className="space-y-8 max-w-5xl mx-auto py-4">
            {/* Hero Banner */}
            <div className="text-center space-y-2 py-4">
              <h2 className="text-3xl md:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-gold via-yellow-200 to-cyan">
                Project Quarm Chronicle
              </h2>
              <p className="text-sm md:text-base text-slate-300 max-w-2xl mx-auto">
                Visualize your Project Quarm logs.
              </p>
            </div>

            {/* Saved Characters in IndexedDB */}
            {savedCharacters.length > 0 && (
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3">
                <div className="flex justify-between items-center">
                  <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                    <span>💾</span> Saved Characters ({savedCharacters.length})
                  </h3>
                  <span className="text-xs text-slate-500">Stored in your browser's IndexedDB</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {savedCharacters.map((char) => (
                    <div
                      key={char.name}
                      onClick={() => handleSelectSavedCharacter(char.name)}
                      className="p-3.5 rounded-lg border border-slate-700 bg-slate-950/60 hover:border-gold hover:bg-slate-900 cursor-pointer transition-all flex flex-col justify-between group"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-bold text-sm text-slate-200 group-hover:text-gold-soft transition-colors">
                            {char.name}
                          </div>
                          <div className="text-xs text-slate-400">
                            Level {char.level} {char.characterClass}
                          </div>
                        </div>
                        <span className="text-[10px] text-cyan font-mono bg-cyan/10 border border-cyan/30 px-1.5 py-0.5 rounded">
                          {char.totalLogLines.toLocaleString()} lines
                        </span>
                      </div>
                      <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-500 flex justify-between items-center">
                        <span>Guild: &lt;{char.guild}&gt;</span>
                        <span className="text-gold-soft font-semibold group-hover:translate-x-0.5 transition-transform">
                          Open &rarr;
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Directory Connect (Primary) */}
            <DirectoryConnect
              onSelectFiles={handleStartParsing}
              disabled={isParsing}
              onOpenSecurityModal={() => setShowSecurityModal(true)}
            />

            {/* Single/Multi File Drop (Fallback) */}
            <FileDropZone
              onSelectFiles={handleStartParsing}
              disabled={isParsing}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-[#0c101a] py-4 text-center text-xs text-slate-500">
        Project Quarm Chronicle created by Peetar &bull; EverQuest is a registered trademark of Daybreak Game Company LLC. &bull;{' '}
        <button
          type="button"
          onClick={() => setShowSecurityModal(true)}
          className="hover:text-cyan underline ml-1 cursor-pointer transition-colors"
        >
          Privacy &amp; Security
        </button>
      </footer>

      {/* Privacy & Security Modal */}
      <SecurityModal
        isOpen={showSecurityModal}
        onClose={() => setShowSecurityModal(false)}
      />
    </div>
  );
};
