import { useState } from 'react';

export default function RefinePanel({ ideaId, onRefine, onClose }) {
  const [instruction, setInstruction] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!instruction.trim()) return;
    onRefine(ideaId, instruction);
    setInstruction('');
    onClose();
  };

  return (
    <div className="mt-4 p-4 rounded-xl border border-accent-cyan/30 bg-accent-cyan/5">
      <div className="flex justify-between items-center mb-2">
        <h4 className="text-sm font-semibold text-accent-cyan">Refine this idea</h4>
        <button onClick={onClose} className="text-slate-400 hover:text-white cursor-pointer p-1">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <p className="text-xs text-slate-400 mb-3">
        Tell the AI how to improve this idea (e.g., "Make it more scalable", "Target students instead", "Use open source tools")
      </p>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          placeholder="Refinement instruction..."
          className="flex-1 bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-accent-cyan/50 focus:ring-1 focus:ring-accent-cyan/50"
          autoFocus
        />
        <button
          type="submit"
          disabled={!instruction.trim()}
          className="px-4 py-2 bg-accent-cyan text-black font-medium text-sm rounded-lg hover:bg-accent-cyan/90 disabled:opacity-50 cursor-pointer"
        >
          Refine
        </button>
      </form>
    </div>
  );
}
