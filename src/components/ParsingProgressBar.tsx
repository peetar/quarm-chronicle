import React from 'react';

export interface ParsingProgress {
  linesProcessed: number;
  bytesRead: number;
  totalBytes: number;
  percent: number;
  linesPerSec: number;
}

interface ParsingProgressBarProps {
  characterName: string;
  progress: ParsingProgress;
  onCancel?: () => void;
}

export const ParsingProgressBar: React.FC<ParsingProgressBarProps> = ({
  characterName,
  progress,
  onCancel,
}) => {
  const mbRead = (progress.bytesRead / (1024 * 1024)).toFixed(1);
  const totalMb = (progress.totalBytes / (1024 * 1024)).toFixed(1);
  const formattedLines = progress.linesProcessed.toLocaleString();
  const formattedRate = progress.linesPerSec.toLocaleString();

  return (
    <div className="bg-[#101522] border border-gold/60 rounded-xl p-5 shadow-[0_10px_30px_rgba(0,0,0,0.6),0_0_20px_rgba(212,175,55,0.15)] space-y-4">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-cyan animate-ping" />
          <div>
            <h3 className="text-base font-bold text-gold-soft">
              Parsing <span className="text-white">{characterName}</span>...
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-2xl font-black text-cyan font-mono">
            {progress.percent}%
          </span>
          {onCancel && (
            <button
              onClick={onCancel}
              className="text-xs px-2.5 py-1 rounded border border-red-800 text-red-400 hover:bg-red-950/60 transition-colors"
            >
              Cancel
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar Track */}
      <div className="w-full bg-slate-900 h-3.5 rounded-full overflow-hidden border border-slate-700 p-0.5">
        <div
          className="h-full bg-gradient-to-r from-gold via-cyan to-emerald-400 rounded-full transition-all duration-150 shadow-[0_0_10px_rgba(56,189,248,0.5)]"
          style={{ width: `${Math.max(2, progress.percent)}%` }}
        />
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-1 border-t border-slate-800/80">
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
          <div className="text-[10px] uppercase tracking-wider text-slate-400">Lines Scanned</div>
          <div className="text-sm font-bold text-slate-100 font-mono mt-0.5">{formattedLines}</div>
        </div>
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
          <div className="text-[10px] uppercase tracking-wider text-slate-400">Log Size Read</div>
          <div className="text-sm font-bold text-cyan font-mono mt-0.5">{mbRead} / {totalMb} MB</div>
        </div>
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
          <div className="text-[10px] uppercase tracking-wider text-slate-400">Processing Rate</div>
          <div className="text-sm font-bold text-emerald-400 font-mono mt-0.5">{formattedRate} lines/sec</div>
        </div>
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
          <div className="text-[10px] uppercase tracking-wider text-slate-400">Status</div>
          <div className="text-sm font-bold text-gold-soft font-mono mt-0.5 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            Reading log...
          </div>
        </div>
      </div>
    </div>
  );
};
