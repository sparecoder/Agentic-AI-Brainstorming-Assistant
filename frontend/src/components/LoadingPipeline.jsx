const STEPS = [
  { label: 'Extracting Context', desc: 'Analyzing your prompt...' },
  { label: 'Generating Ideas', desc: 'Creating diverse project concepts...' },
  { label: 'Deduplicating', desc: 'Ensuring fresh, unique ideas...' },
  { label: 'Refining & Ranking', desc: 'Scoring by feasibility, novelty & impact...' },
];

export default function LoadingPipeline() {
  return (
    <div className="w-full max-w-2xl mx-auto py-12 text-center">
      <div className="text-accent-cyan text-sm font-medium mb-2 flex items-center justify-center gap-1.5">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        AI Pipeline Running
      </div>
      <h2 className="text-2xl font-bold text-white mb-2">Brainstorming in Progress</h2>
      <p className="text-slate-400 text-sm mb-8">Our multi-step agent is working through the reasoning pipeline...</p>

      <div className="space-y-3">
        {STEPS.map((step, i) => (
          <div
            key={step.label}
            className="glass rounded-xl p-4 flex items-center gap-4 opacity-0"
            style={{ animation: `slide-up 0.5s ease-out ${i * 1}s forwards` }}
          >
            <div className="w-8 h-8 rounded-lg bg-accent-cyan/10 border border-accent-cyan/30 flex items-center justify-center flex-shrink-0">
              <span className="text-accent-cyan text-sm font-bold">{i + 1}</span>
            </div>
            <div className="text-left">
              <h3 className="text-white font-semibold text-sm">{step.label}</h3>
              <p className="text-slate-400 text-xs">{step.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
