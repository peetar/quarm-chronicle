import React from 'react';
import { ProjectorProps } from '../types/projectors';
import { InteractiveTimelineCard } from '../cards/InteractiveTimelineCard';

export const TimelineProjector: React.FC<ProjectorProps> = ({
  data,
  onBackToSelector,
}) => {
  return (
    <div className="w-full max-w-7xl mx-auto space-y-4">
      {onBackToSelector && (
        <div className="flex items-center gap-2 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
          <button
            onClick={onBackToSelector}
            className="text-xs px-3 py-1.5 rounded border border-slate-700 text-slate-300 hover:text-white hover:border-slate-500 transition-colors"
          >
            &larr; Back
          </button>
          <span className="text-xs text-gold-soft font-semibold">
            Timeline Projector Mode
          </span>
        </div>
      )}

      <InteractiveTimelineCard data={data} />
    </div>
  );
};
