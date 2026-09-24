import React, { useState, useEffect, useRef } from 'react';
import {
  saveDirectoryHandle,
  getDirectoryHandle,
  clearDirectoryHandle,
  getCharacterStitchSettings,
  saveCharacterStitchSettings,
} from '../storage/characterStore';

export interface DiscoveredLogFile {
  name: string;
  characterName: string;
  sizeMb: number;
  lastModified: Date;
  file?: File;
  fileHandle?: FileSystemFileHandle;
  type: 'active' | 'archive' | 'copy';
}

export interface CharacterLogGroup {
  characterName: string;
  totalSizeMb: number;
  lastModified: Date;
  files: DiscoveredLogFile[];
}

interface DirectoryConnectProps {
  onSelectFiles: (files: File[], characterName: string) => void;
  disabled?: boolean;
  onOpenSecurityModal?: () => void;
}

function extractCharacterName(fileName: string): string {
  // Regex strictly enforces underscore right after character name: eqlog_Character_...
  const match = fileName.match(/^eqlog_([A-Za-z0-9]+)_/i);
  if (match) return match[1];
  const simpleMatch = fileName.match(/^eqlog_([A-Za-z0-9]+)\.txt$/i);
  if (simpleMatch) return simpleMatch[1];
  return fileName.replace(/^eqlog_/i, '').replace(/\.txt$/i, '');
}

function classifyLogFile(fileName: string, characterName: string): 'active' | 'archive' | 'copy' {
  if (fileName.includes(' - Copy')) {
    return 'copy';
  }
  const cleanActive = `eqlog_${characterName.toLowerCase()}_pq.proj.txt`;
  if (fileName.toLowerCase() === cleanActive) {
    return 'active';
  }
  return 'archive';
}

export const DirectoryConnect: React.FC<DirectoryConnectProps> = ({
  onSelectFiles,
  disabled = false,
  onOpenSecurityModal,
}) => {
  const [characterGroups, setCharacterGroups] = useState<CharacterLogGroup[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [hasSavedFolder, setHasSavedFolder] = useState(false);
  const [savedHandle, setSavedHandle] = useState<FileSystemDirectoryHandle | null>(null);

  // Stitch Modal state
  const [stitchModalGroup, setStitchModalGroup] = useState<CharacterLogGroup | null>(null);
  const [selectedFileNames, setSelectedFileNames] = useState<Set<string>>(new Set());
  const [rememberSettings, setRememberSettings] = useState(true);
  const [isPreparingFiles, setIsPreparingFiles] = useState(false);
  const [stitchError, setStitchError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const supportsDirectoryPicker = typeof window !== 'undefined' && 'showDirectoryPicker' in window;

  useEffect(() => {
    checkSavedDirectory();
  }, []);

  const checkSavedDirectory = async () => {
    try {
      const handle = await getDirectoryHandle();
      if (handle) {
        setSavedHandle(handle);
        setHasSavedFolder(true);
        // @ts-ignore
        const permission = await handle.queryPermission({ mode: 'read' });
        if (permission === 'granted') {
          await scanDirectoryHandle(handle);
        }
      }
    } catch (err) {
      console.warn('Error reading saved directory handle:', err);
    }
  };

  const groupDiscoveredFiles = (files: DiscoveredLogFile[]): CharacterLogGroup[] => {
    const groupMap = new Map<string, CharacterLogGroup>();
    for (const f of files) {
      const key = f.characterName.toLowerCase();
      let grp = groupMap.get(key);
      if (!grp) {
        grp = {
          characterName: f.characterName,
          totalSizeMb: 0,
          lastModified: new Date(0),
          files: [],
        };
        groupMap.set(key, grp);
      }
      grp.files.push(f);
      grp.totalSizeMb = Math.round((grp.totalSizeMb + f.sizeMb) * 10) / 10;
      if (f.lastModified.getTime() > grp.lastModified.getTime()) {
        grp.lastModified = f.lastModified;
      }
    }

    const typeOrder = { active: 0, archive: 1, copy: 2 };
    const groups = Array.from(groupMap.values()).map((g) => ({
      ...g,
      files: g.files.sort((a, b) => {
        if (typeOrder[a.type] !== typeOrder[b.type]) {
          return typeOrder[a.type] - typeOrder[b.type];
        }
        return b.lastModified.getTime() - a.lastModified.getTime();
      }),
    }));

    groups.sort((a, b) => b.lastModified.getTime() - a.lastModified.getTime());
    return groups;
  };

  const scanDirectoryHandle = async (dirHandle: FileSystemDirectoryHandle) => {
    setError(null);
    setIsScanning(true);
    try {
      const candidateHandles: FileSystemFileHandle[] = [];
      // @ts-ignore
      for await (const entry of dirHandle.values()) {
        if (entry.kind === 'file' && entry.name.startsWith('eqlog_') && entry.name.endsWith('.txt')) {
          candidateHandles.push(entry as FileSystemFileHandle);
        }
      }

      const files: DiscoveredLogFile[] = [];
      const batchSize = 6;

      for (let i = 0; i < candidateHandles.length; i += batchSize) {
        const batch = candidateHandles.slice(i, i + batchSize);
        const results = await Promise.all(
          batch.map(async (handle) => {
            try {
              const file = await handle.getFile();
              if (file.size === 0) return null;

              const characterName = extractCharacterName(handle.name);
              const type = classifyLogFile(handle.name, characterName);

              return {
                name: handle.name,
                characterName,
                sizeMb: Math.round((file.size / (1024 * 1024)) * 10) / 10,
                lastModified: new Date(file.lastModified),
                fileHandle: handle,
                type,
              } as DiscoveredLogFile;
            } catch {
              return null;
            }
          })
        );

        for (const r of results) {
          if (r) files.push(r);
        }

        await new Promise((resolve) => setTimeout(resolve, 0));
      }

      const groups = groupDiscoveredFiles(files);
      setCharacterGroups(groups);

      if (groups.length === 0) {
        setError('No active EverQuest log files (eqlog_*.txt) found in the selected folder.');
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setError(`Failed to read folder contents: ${err.message}`);
      }
    } finally {
      setIsScanning(false);
    }
  };

  const handleConnectDirectory = async () => {
    setError(null);
    try {
      // @ts-ignore
      const dirHandle: FileSystemDirectoryHandle = await window.showDirectoryPicker({
        id: 'quarm_takp_folder',
        mode: 'read',
      });

      await saveDirectoryHandle(dirHandle);
      setSavedHandle(dirHandle);
      setHasSavedFolder(true);
      await scanDirectoryHandle(dirHandle);
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setError(err.message || 'Failed to open directory picker.');
      }
    }
  };

  const handleReconnectSaved = async () => {
    if (!savedHandle) return;
    setError(null);
    try {
      // @ts-ignore
      const perm = await savedHandle.requestPermission({ mode: 'read' });
      if (perm === 'granted') {
        await scanDirectoryHandle(savedHandle);
      } else {
        setError('Permission to access saved TAKPv22 folder was denied.');
      }
    } catch (err: any) {
      setError(`Failed to reconnect folder: ${err.message}`);
    }
  };

  const handleForgetSavedFolder = async () => {
    await clearDirectoryHandle();
    setSavedHandle(null);
    setHasSavedFolder(false);
    setCharacterGroups([]);
  };

  const handleDirectFilesChosen = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const rawFiles = Array.from(e.target.files);

    const files: DiscoveredLogFile[] = rawFiles
      .filter((file) => file.name.startsWith('eqlog_') && file.name.endsWith('.txt'))
      .map((file) => {
        const characterName = extractCharacterName(file.name);
        const type = classifyLogFile(file.name, characterName);
        return {
          name: file.name,
          characterName,
          sizeMb: Math.round((file.size / (1024 * 1024)) * 10) / 10,
          lastModified: new Date(file.lastModified),
          file,
          type,
        };
      })
      .filter((f) => f.sizeMb > 0);

    const groups = groupDiscoveredFiles(files);
    setCharacterGroups(groups);

    // If user selected files for exactly one character
    if (groups.length === 1) {
      if (groups[0].files.length > 1) {
        openStitchModal(groups[0]);
      } else if (groups[0].files.length === 1 && groups[0].files[0].file) {
        onSelectFiles([groups[0].files[0].file], groups[0].characterName);
      }
    }
  };

  const openStitchModal = async (group: CharacterLogGroup) => {
    setStitchModalGroup(group);
    setStitchError(null);

    // 1. Try to load saved settings from IndexedDB
    try {
      const saved = await getCharacterStitchSettings(group.characterName);
      if (saved && saved.length > 0) {
        const existingSaved = group.files.filter((f) => saved.includes(f.name)).map((f) => f.name);
        if (existingSaved.length > 0) {
          setSelectedFileNames(new Set(existingSaved));
          return;
        }
      }
    } catch (e) {
      console.warn('Failed to load stitch settings:', e);
    }

    // 2. Default: select all active & archive files, excluding copies
    const defaultSelected = group.files
      .filter((f) => f.type !== 'copy')
      .map((f) => f.name);

    if (defaultSelected.length === 0) {
      setSelectedFileNames(new Set(group.files.map((f) => f.name)));
    } else {
      setSelectedFileNames(new Set(defaultSelected));
    }
  };

  const handleToggleFileSelection = (fileName: string) => {
    setSelectedFileNames((prev) => {
      const next = new Set(prev);
      if (next.has(fileName)) {
        next.delete(fileName);
      } else {
        next.add(fileName);
      }
      return next;
    });
  };

  const handleSelectAllInModal = () => {
    if (!stitchModalGroup) return;
    setSelectedFileNames(new Set(stitchModalGroup.files.map((f) => f.name)));
  };

  const handleSelectRecommendedInModal = () => {
    if (!stitchModalGroup) return;
    setSelectedFileNames(
      new Set(stitchModalGroup.files.filter((f) => f.type !== 'copy').map((f) => f.name))
    );
  };

  const handleConfirmStitch = async () => {
    if (!stitchModalGroup || selectedFileNames.size === 0) return;
    setIsPreparingFiles(true);
    setStitchError(null);

    try {
      if (rememberSettings) {
        await saveCharacterStitchSettings(
          stitchModalGroup.characterName,
          Array.from(selectedFileNames)
        );
      }

      const filesToParse: File[] = [];
      for (const f of stitchModalGroup.files) {
        if (selectedFileNames.has(f.name)) {
          const file = f.file || (await f.fileHandle?.getFile());
          if (file) filesToParse.push(file);
        }
      }

      if (filesToParse.length === 0) {
        throw new Error('No valid files could be loaded');
      }

      const charName = stitchModalGroup.characterName;
      setStitchModalGroup(null);
      setIsPreparingFiles(false);
      onSelectFiles(filesToParse, charName);
    } catch (err: any) {
      setStitchError(`Failed to prepare files: ${err.message}`);
      setIsPreparingFiles(false);
    }
  };

  const handleSelectGroup = async (group: CharacterLogGroup) => {
    if (disabled || isScanning) return;
    if (group.files.length === 1) {
      try {
        const f = group.files[0];
        const file = f.file || (await f.fileHandle?.getFile());
        if (file) {
          onSelectFiles([file], group.characterName);
        }
      } catch (err: any) {
        setError(`Failed to read log file: ${err.message}`);
      }
    } else {
      await openStitchModal(group);
    }
  };

  const selectedSizeMb = stitchModalGroup
    ? Math.round(
        stitchModalGroup.files
          .filter((f) => selectedFileNames.has(f.name))
          .reduce((sum, f) => sum + f.sizeMb, 0) * 10
      ) / 10
    : 0;

  return (
    <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-5 backdrop-blur-sm space-y-4">
      {/* Hidden input for instant native file picking */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".txt"
        onChange={handleDirectFilesChosen}
        className="hidden"
      />

      <div className="flex flex-wrap justify-between items-start gap-4">
        <div>
          <h3 className="text-base font-bold text-gold-soft flex items-center gap-2">
            <span>📁</span> Connect TAKP Directory or Log Files
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Select your TAKP folder or individual log files.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Quick Select Files */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled || isScanning}
            className="px-3.5 py-2 rounded-lg bg-cyan/15 border border-cyan/60 text-cyan hover:bg-cyan/25 font-bold text-xs md:text-sm transition-all shadow-[0_0_15px_rgba(56,189,248,0.2)] disabled:opacity-50 flex items-center gap-1.5"
            title="Select log files"
          >
            <span>⚡</span> Select eqlog_*.txt Files
          </button>

          {/* Folder Picker with Saved Handle */}
          {supportsDirectoryPicker && (
            <>
              {hasSavedFolder ? (
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={handleReconnectSaved}
                    disabled={disabled || isScanning}
                    className="px-3.5 py-2 rounded-lg bg-gold/20 border border-gold text-gold-soft hover:bg-gold/30 font-bold text-xs md:text-sm transition-all shadow-gold-glow disabled:opacity-50 flex items-center gap-1.5"
                    title="Reconnect previously selected TAKP directory"
                  >
                    <span>🔄</span> {isScanning ? 'Scanning...' : 'Re-Scan Saved TAKPv22'}
                  </button>
                  <button
                    onClick={handleConnectDirectory}
                    disabled={disabled || isScanning}
                    className="px-2.5 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:text-white text-xs transition-all"
                    title="Choose a different folder"
                  >
                    Change
                  </button>
                </div>
              ) : (
                <button
                  onClick={handleConnectDirectory}
                  disabled={disabled || isScanning}
                  className="px-3.5 py-2 rounded-lg bg-gold/15 border border-gold text-gold-soft hover:bg-gold/25 font-bold text-xs md:text-sm transition-all shadow-gold-glow disabled:opacity-50 flex items-center gap-1.5"
                  title="Choose TAKP directory"
                >
                  <span>📂</span> {isScanning ? 'Scanning Folder...' : 'Choose TAKP Folder'}
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Security Reassurance */}
      <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-400 bg-slate-950/40 px-3 py-1.5 rounded-lg border border-slate-800/80 gap-2">
        <div className="flex items-center gap-1.5">
          <span className="text-emerald-400 text-xs">🔒</span>
          <span>Read-only access enforced by your browser. No files are modified or uploaded.</span>
        </div>
        {onOpenSecurityModal && (
          <button
            type="button"
            onClick={onOpenSecurityModal}
            className="text-cyan hover:underline font-medium"
          >
            Privacy &amp; Security Info &rarr;
          </button>
        )}
      </div>

      {hasSavedFolder && (
        <div className="flex items-center justify-between text-[11px] text-slate-400 bg-slate-950/40 px-3 py-1.5 rounded-lg border border-slate-800/80">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Connected to saved local TAKP directory
          </span>
          <button
            onClick={handleForgetSavedFolder}
            className="text-slate-500 hover:text-red-400 transition-colors"
          >
            Forget folder connection
          </button>
        </div>
      )}

      {error && (
        <div className="text-xs text-crimson bg-red-950/40 border border-red-800/60 p-2.5 rounded">
          {error}
        </div>
      )}

      {/* Discovered Characters Carousel/Grid */}
      {characterGroups.length > 0 && (
        <div className="pt-2 border-t border-slate-800">
          <div className="flex justify-between items-center mb-2.5">
            <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
              Discovered Characters ({characterGroups.length})
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 max-h-[380px] overflow-y-auto pr-1">
            {characterGroups.map((group) => {
              const fileCount = group.files.length;
              const hasMultipleLogs = fileCount > 1;
              return (
                <div
                  key={group.characterName}
                  onClick={() => !disabled && handleSelectGroup(group)}
                  className={`p-3 rounded-lg border border-slate-700 bg-slate-950/70 hover:border-gold hover:bg-slate-900 cursor-pointer transition-all flex flex-col justify-between group ${
                    disabled ? 'opacity-50 pointer-events-none' : ''
                  }`}
                >
                  <div>
                    <div className="font-bold text-sm text-slate-200 group-hover:text-gold-soft transition-colors flex items-center justify-between">
                      <span>{group.characterName}</span>
                      <span className="text-[11px] text-cyan font-mono">{group.totalSizeMb} MB</span>
                    </div>

                    <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
                      {hasMultipleLogs ? (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center gap-1">
                          <span>📚</span> {fileCount} logs (Stitch)
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-400 truncate max-w-[200px]" title={group.files[0].name}>
                          {group.files[0].name}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="mt-2 text-[10px] text-slate-400 flex justify-between items-center pt-1.5 border-t border-slate-800">
                    <span>{hasMultipleLogs ? 'Latest:' : 'Modified:'}</span>
                    <span>{group.lastModified.toLocaleDateString()}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Stitch Selection Modal */}
      {stitchModalGroup && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-gold/60 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] flex flex-col">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-bold text-gold-soft flex items-center gap-2">
                  <span>📚</span> Stitch Logs for {stitchModalGroup.characterName}
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Detected <strong className="text-slate-200">{stitchModalGroup.files.length} log files</strong> ({stitchModalGroup.totalSizeMb} MB). Select which files to stitch together into a single continuous chronicle.
                </p>
              </div>
              <button
                onClick={() => setStitchModalGroup(null)}
                className="text-slate-400 hover:text-white text-lg p-1"
              >
                &times;
              </button>
            </div>

            {stitchError && (
              <div className="text-xs text-crimson bg-red-950/60 border border-red-800/80 p-2.5 rounded">
                {stitchError}
              </div>
            )}

            {/* Quick action buttons */}
            <div className="flex items-center justify-between text-xs pt-1 border-b border-slate-800 pb-2">
              <span className="text-slate-400 font-medium">Select log files:</span>
              <div className="space-x-3">
                <button
                  type="button"
                  onClick={handleSelectRecommendedInModal}
                  className="text-cyan hover:underline"
                >
                  Recommended (Active + Archives)
                </button>
                <button
                  type="button"
                  onClick={handleSelectAllInModal}
                  className="text-slate-400 hover:text-slate-200"
                >
                  Select All
                </button>
              </div>
            </div>

            {/* File list */}
            <div className="flex-1 overflow-y-auto space-y-2 pr-1 max-h-[300px]">
              {stitchModalGroup.files.map((file) => {
                const isSelected = selectedFileNames.has(file.name);
                return (
                  <label
                    key={file.name}
                    className={`flex items-start gap-3 p-3 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'border-gold/60 bg-gold/5'
                        : 'border-slate-800 bg-slate-950/40 hover:border-slate-700'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => handleToggleFileSelection(file.name)}
                      className="mt-1 rounded border-slate-700 text-gold focus:ring-gold bg-slate-900"
                    />

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs font-semibold text-slate-200 break-all">
                          {file.name}
                        </span>
                        {file.type === 'active' && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/50">
                            ⚡ Active Log
                          </span>
                        )}
                        {file.type === 'archive' && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-500/20 text-sky-300 border border-sky-500/50">
                            📦 Archive
                          </span>
                        )}
                        {file.type === 'copy' && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/50">
                            ⚠️ Duplicate / Copy
                          </span>
                        )}
                      </div>

                      <div className="text-[11px] text-slate-400 mt-1 flex gap-3">
                        <span className="font-mono text-cyan">{file.sizeMb} MB</span>
                        <span>Modified: {file.lastModified.toLocaleDateString()}</span>
                      </div>

                      {file.type === 'copy' && (
                        <div className="text-[10px] text-amber-400/90 mt-1">
                          Likely duplicate copy
                        </div>
                      )}
                    </div>
                  </label>
                );
              })}
            </div>

            {/* Remember Settings */}
            <div className="pt-2 border-t border-slate-800">
              <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberSettings}
                  onChange={(e) => setRememberSettings(e.target.checked)}
                  className="rounded border-slate-700 text-gold focus:ring-gold bg-slate-900"
                />
                <span>Remember selection for {stitchModalGroup.characterName} on future re-parses</span>
              </label>
            </div>

            {/* Modal Actions */}
            <div className="flex justify-end items-center gap-3 pt-3 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setStitchModalGroup(null)}
                disabled={isPreparingFiles}
                className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300 hover:text-white text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmStitch}
                disabled={selectedFileNames.size === 0 || isPreparingFiles}
                className="px-5 py-2 rounded-lg bg-gold/20 border border-gold text-gold-soft hover:bg-gold/30 font-bold text-xs md:text-sm transition-all shadow-gold-glow disabled:opacity-50 flex items-center gap-1.5"
              >
                <span>⚡</span> {isPreparingFiles ? 'Loading Files...' : `Stitch & Parse (${selectedFileNames.size} files, ${selectedSizeMb} MB)`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

