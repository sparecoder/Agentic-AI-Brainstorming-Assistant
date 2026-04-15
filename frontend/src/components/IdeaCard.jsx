import { useState } from 'react';
import RefinePanel from './RefinePanel';

const RANK_BADGE = { 
  1: <div className="flex items-center justify-center w-8 h-8 rounded-full bg-amber-500/20 text-amber-500 text-sm font-bold border border-amber-500/30 shadow-[0_0_10px_rgba(245,158,11,0.2)]">1</div>, 
  2: <div className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-300/20 text-slate-300 text-sm font-bold border border-slate-300/30 shadow-[0_0_10px_rgba(203,213,225,0.1)]">2</div>, 
  3: <div className="flex items-center justify-center w-8 h-8 rounded-full bg-amber-700/20 text-amber-500 text-sm font-bold border border-amber-700/30 shadow-[0_0_10px_rgba(180,83,9,0.2)]">3</div> 
};

// Inline score indicator
function Score({ label, value }) {
  const color = value <= 3 ? '#f43f5e' : value <= 6 ? '#f59e0b' : '#10b981';
  const radius = 20;
  const circ = 2 * Math.PI * radius;
  const offset = circ - (value / 10) * circ;

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="score-ring" style={{ width: 48, height: 48 }}>
        <svg width={48} height={48}>
          <circle cx={24} cy={24} r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="3" />
          <circle cx={24} cy={24} r={radius} fill="none" stroke={color} strokeWidth="3"
            strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={offset}
            style={{ filter: `drop-shadow(0 0 4px ${color}40)` }} />
        </svg>
        <span className="absolute text-xs font-bold" style={{ color }}>{value.toFixed(1)}</span>
      </div>
      <span className="text-[10px] text-slate-500 uppercase tracking-wider font-medium">{label}</span>
    </div>
  );
}

export default function IdeaCard({ idea, index, onRefine, onBookmark }) {
  const [expanded, setExpanded] = useState(false);
  const [showRefine, setShowRefine] = useState(false);

  return (
    <div
      className="glass rounded-2xl overflow-hidden opacity-0"
      style={{ animation: `slide-up 0.5s ease-out ${index * 0.15}s forwards` }}
      id={`idea-card-${idea.rank}`}
    >
      <div className="p-6">
        {/* Header row */}
        <div className="flex items-start gap-4 mb-4">
          <div className="flex-shrink-0">{RANK_BADGE[idea.rank] || <div className="flex items-center justify-center w-8 h-8 rounded-full bg-white/5 text-slate-400 text-sm font-bold border border-white/10">{idea.rank}</div>}</div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              {idea.category && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20">
                  {idea.category}
                </span>
              )}
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider bg-accent-violet/10 text-accent-violet border border-accent-violet/20">
                {idea.difficulty_level}
              </span>
              {idea.confidence && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wider bg-white/5 text-slate-300 border border-white/10" title="AI Confidence Score">
                  Confidence: {Math.round(idea.confidence * 100)}%
                </span>
              )}
            </div>
            <div className="flex justify-between items-start gap-4">
              <h3 className="text-lg font-bold text-white">{idea.title}</h3>
              {onBookmark && (
                <button 
                  onClick={() => onBookmark(idea.id)} 
                  className={`p-1.5 rounded-full transition-colors cursor-pointer ${idea.is_bookmarked ? 'text-accent-rose bg-accent-rose/10 hover:bg-accent-rose/20' : 'text-slate-500 hover:text-white hover:bg-white/10'}`}
                  title={idea.is_bookmarked ? "Remove bookmark" : "Save this idea"}
                >
                  <svg className="w-5 h-5" fill={idea.is_bookmarked ? "currentColor" : "none"} viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={idea.is_bookmarked ? 1 : 2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Scores */}
        <div className="flex flex-col sm:flex-row gap-6 mb-6">
          {/* Main text content */}
          <div className="flex-1 space-y-4">
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Problem</h4>
              <p className="text-slate-300 text-sm leading-relaxed">{idea.problem_statement}</p>
            </div>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Solution</h4>
              <p className="text-slate-300 text-sm leading-relaxed">{idea.solution_overview}</p>
            </div>
          </div>
          
          {/* Scores sidebar */}
          <div className="flex-shrink-0 sm:w-48 p-4 rounded-xl bg-black/20 border border-white/5 space-y-4">
            <div className="flex justify-center gap-3">
              <Score label="Feasible" value={idea.feasibility_score} />
              <Score label="Scale" value={idea.scalability_score} />
              <Score label="Impact" value={idea.impact_score} />
            </div>
            {idea.score_explanation && (
              <div className="pt-3 border-t border-white/10">
                <p className="text-[10px] text-slate-400 leading-snug italic">"{idea.score_explanation}"</p>
              </div>
            )}
          </div>
        </div>

        {/* Key Features */}
        <div className="mb-3">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Key Features / Approaches</h4>
          <div className="flex flex-wrap gap-2">
            {idea.key_features?.map((f, i) => (
              <span key={i} className="px-3 py-1 rounded-lg text-xs bg-white/[0.04] border border-white/[0.08] text-slate-300">{f}</span>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mb-4">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Tools / Stack</h4>
          <div className="flex flex-wrap gap-2">
            {idea.tech_stack?.map((t, i) => (
              <span key={i} className="px-3 py-1 rounded-lg text-xs font-medium bg-accent-teal/10 text-accent-teal border border-accent-teal/20">{t}</span>
            ))}
          </div>
        </div>

        {/* Action Bar */}
        <div className="flex items-center justify-between border-t border-white/5 pt-3">
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-slate-400 hover:text-accent-cyan flex items-center gap-1 transition-colors cursor-pointer"
          >
            <svg className={`w-3.5 h-3.5 transition-transform ${expanded ? 'rotate-180' : ''}`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
            {expanded ? 'Hide details' : 'Show Scope Details'}
          </button>

          {onRefine && (
            <button
              onClick={() => setShowRefine(!showRefine)}
              className="text-xs text-slate-900 bg-white hover:bg-slate-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors font-medium cursor-pointer"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Iterate / Refine
            </button>
          )}
        </div>

        {idea.refinement_note && (
          <div className="mt-3 p-2 rounded-lg bg-accent-cyan/10 border border-accent-cyan/20 text-xs text-accent-cyan">
            <span className="font-bold">Latest refinement:</span> {idea.refinement_note}
          </div>
        )}

        {showRefine && onRefine && (
          <RefinePanel 
            ideaId={idea.id} 
            onRefine={onRefine} 
            onClose={() => setShowRefine(false)} 
          />
        )}

        {expanded && (
          <div className="mt-4 space-y-4 pt-4 border-t border-white/5 animate-[fade-in_0.3s_ease-out]">
            <div className="bg-black/20 p-4 rounded-xl border border-white/5">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-2">
                <svg className="w-4 h-4 text-accent-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                MVP Scope
              </h4>
              <p className="text-slate-300 text-sm leading-relaxed">{idea.mvp_scope}</p>
            </div>
            <div className="bg-black/20 p-4 rounded-xl border border-white/5">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-2">
                <svg className="w-4 h-4 text-accent-violet" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Future Scope
              </h4>
              <p className="text-slate-300 text-sm leading-relaxed">{idea.future_scope}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
