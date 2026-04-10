import { useState } from 'react';

export default function HistoryPanel({ history, onSelect, currentSessionId }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed top-4 left-4 z-50 lg:hidden glass rounded-xl p-2.5 text-slate-400 hover:text-white transition-colors cursor-pointer"
        aria-label="Toggle history"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>

      {/* Mobile overlay */}
      {open && <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setOpen(false)} />}

      {/* Sidebar */}
      <aside className={`fixed top-0 left-0 h-full w-72 bg-navy-900/95 backdrop-blur-xl border-r border-white/[0.06] z-40 transition-transform lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-5 border-b border-white/[0.06] flex items-center justify-between">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <svg className="w-4 h-4 text-accent-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              History
            </h2>
            <span className="text-xs text-slate-500">{history.length} sessions</span>
          </div>

          {/* List */}
          <div className="flex-1 overflow-y-auto py-2">
            {history.length === 0 ? (
              <div className="px-5 py-8 text-center">
                <p className="text-slate-500 text-xs">No sessions yet</p>
                <p className="text-slate-600 text-xs mt-1">Your history will appear here</p>
              </div>
            ) : (
              history.map((s) => (
                <button
                  key={s.id}
                  onClick={() => { onSelect(s.id); setOpen(false); }}
                  className={`w-full text-left px-5 py-3 hover:bg-white/[0.04] transition-colors border-l-2 cursor-pointer ${
                    currentSessionId === s.id ? 'border-accent-cyan bg-white/[0.03]' : 'border-transparent'
                  }`}
                >
                  <p className="text-sm text-slate-200 truncate font-medium">{s.prompt}</p>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-[10px] text-slate-500">
                      {new Date(s.created_at).toLocaleDateString('en-US', {
                        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
                      })}
                    </span>
                    <span className="text-[10px] text-accent-cyan/60 font-medium">{s.idea_count} ideas</span>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
