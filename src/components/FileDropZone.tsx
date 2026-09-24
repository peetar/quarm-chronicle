import React, { useState, useRef } from 'react';

interface FileDropZoneProps {
  onSelectFiles: (files: File[], characterName: string) => void;
  disabled?: boolean;
}

export const FileDropZone: React.FC<FileDropZoneProps> = ({
  onSelectFiles,
  disabled = false,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [charHint, setCharHint] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const inferCharacterName = (fileName: string): string => {
    const match = fileName.match(/^eqlog_([A-Za-z0-9]+)_/i);
    if (match) return match[1];
    const simpleMatch = fileName.match(/^eqlog_([A-Za-z0-9]+)\.txt$/i);
    if (simpleMatch) return simpleMatch[1];
    return fileName.replace(/^eqlog_/i, '').replace(/\.txt$/i, '');
  };

  const processFiles = (fileList: FileList | File[]) => {
    const files = Array.from(fileList).filter(
      (f) => f.name.startsWith('eqlog_') && f.name.endsWith('.txt')
    );
    if (files.length === 0) return;
    setSelectedFiles(files);
    const inferred = inferCharacterName(files[0].name);
    if (!charHint) {
      setCharHint(inferred);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFiles(e.target.files);
    }
  };

  const handleStartParsing = () => {
    if (selectedFiles.length === 0) return;
    const name = charHint.trim() || inferCharacterName(selectedFiles[0].name);
    onSelectFiles(selectedFiles, name);
  };

  const totalSizeMb =
    Math.round(
      (selectedFiles.reduce((acc, f) => acc + f.size, 0) / (1024 * 1024)) * 10
    ) / 10;

  return (
    <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-5 backdrop-blur-sm space-y-4">
      <div>
        <h3 className="text-base font-bold text-gold-soft flex items-center gap-2">
          <span>📄</span> Upload Single or Multiple Log Files
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Drag & drop <code className="text-cyan bg-slate-950 px-1 py-0.5 rounded">eqlog_*.txt</code> files here.
        </p>
      </div>

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-gold bg-gold/10 shadow-gold-glow scale-[1.01]'
            : 'border-slate-700 hover:border-slate-500 bg-slate-950/40 hover:bg-slate-950/60'
        } ${disabled ? 'opacity-50 pointer-events-none cursor-not-allowed' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".txt"
          onChange={handleFileInputChange}
          className="hidden"
          disabled={disabled}
        />
        <div className="text-3xl mb-2">📜</div>
        <div className="text-sm font-semibold text-slate-200">
          {selectedFiles.length > 0 ? (
            <span className="text-gold-soft">
              {selectedFiles.length === 1
                ? `${selectedFiles[0].name} (${(selectedFiles[0].size / (1024 * 1024)).toFixed(1)} MB)`
                : `📚 ${selectedFiles.length} files selected (${totalSizeMb} MB total)`}
            </span>
          ) : (
            'Click to browse or drop eqlog_*.txt files here'
          )}
        </div>
      </div>

      {selectedFiles.length > 0 && (
        <div className="flex flex-wrap items-center gap-3 pt-2">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Character Name
            </label>
            <input
              type="text"
              value={charHint}
              onChange={(e) => setCharHint(e.target.value)}
              placeholder="e.g. Tweedlede"
              disabled={disabled}
              className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-sm text-slate-200 focus:outline-none focus:border-gold"
            />
          </div>
          <div className="self-end">
            <button
              onClick={handleStartParsing}
              disabled={disabled}
              className="px-5 py-2 rounded-lg bg-gold/20 border border-gold text-gold-soft hover:bg-gold/30 font-bold text-sm transition-all shadow-gold-glow disabled:opacity-50"
            >
              ⚡ Stream & Parse {selectedFiles.length > 1 ? `${selectedFiles.length} Logs` : 'Log'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
