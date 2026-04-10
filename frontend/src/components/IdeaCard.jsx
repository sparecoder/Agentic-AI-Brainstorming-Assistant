import { useState } from 'react';

const RANK_BADGE = { 
  1: <div className="flex items-center justify-center w-8 h-8 rounded-full bg-amber-500/20 text-amber-500 text-sm font-bold border border-amber-500/30 shadow-[0_0_10px_rgba(245,158,11,0.2)]">1</div>, 
  2: <div className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-300/20 text-slate-300 text-sm font-bold border border-slate-300/30 shadow-[0_0_10px_rgba(203,213,225,0.1)]">2</div>, 
  3: <div className="flex items-center justify-center w-8 h-8 rounded-full bg-amber-700/20 text-amber-500 text-sm font-bold border border-amber-700/30 shadow-[0_0_10px_rgba(180,83,9,0.2)]">3</div> 
};

// Inline score indicator — replaces the old ScoreBadge component
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

export default function IdeaCard({ idea, index }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className="glass rounded-2xl overflow-hidden opacity-0"
      style={{ animation: `slide-up 0.5s ease-out ${index * 0.15}s forwards` }}
      id={`idea-card-${idea.rank}`}
    >
      <div className="p-6">
        {/* Header row */}
        <div className="flex items-start gap-3 mb-4">
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
            </div>
            <h3 className="text-lg font-bold text-white">{idea.title}</h3>
          </div>

          {/* Scores */}
          <div className="flex-shrink-0 flex gap-3">
            <Score label="Feasibility" value={idea.feasibility_score} />
            <Score label="Novelty" value={idea.novelty_score} />
            <Score label="Impact" value={idea.impact_score} />
          </div>
        </div>

        {/* Problem & Solution */}
        <div className="mb-3">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Problem</h4>
          <p className="text-slate-300 text-sm leading-relaxed">{idea.problem_statement}</p>
        </div>
        <div className="mb-3">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Solution</h4>
          <p className="text-slate-300 text-sm leading-relaxed">{idea.solution_overview}</p>
        </div>

        {/* Key Features */}
        <div className="mb-3">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Key Features</h4>
          <div className="flex flex-wrap gap-2">
            {idea.key_features?.map((f, i) => (
              <span key={i} className="px-3 py-1 rounded-lg text-xs bg-white/[0.04] border border-white/[0.08] text-slate-300">{f}</span>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mb-3">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Tech Stack</h4>
          <div className="flex flex-wrap gap-2">
            {idea.tech_stack?.map((t, i) => (
              <span key={i} className="px-3 py-1 rounded-lg text-xs font-medium bg-accent-teal/10 text-accent-teal border border-accent-teal/20">{t}</span>
            ))}
          </div>
        </div>

        {/* Expandable MVP & Future Scope */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-slate-400 hover:text-accent-cyan flex items-center gap-1 transition-colors cursor-pointer mt-2"
        >
          <svg className={`w-3.5 h-3.5 transition-transform ${expanded ? 'rotate-180' : ''}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
          {expanded ? 'Hide details' : 'Show MVP & Future Scope'}
        </button>

        {expanded && (
          <div className="mt-3 space-y-3 animate-[fade-in_0.3s_ease-out]">
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">MVP Scope</h4>
              <p className="text-slate-300 text-sm leading-relaxed">{idea.mvp_scope}</p>
            </div>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Future Scope</h4>
              <p className="text-slate-300 text-sm leading-relaxed">{idea.future_scope}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
