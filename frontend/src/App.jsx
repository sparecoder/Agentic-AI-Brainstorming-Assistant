import { useEffect, useState } from 'react';
import { useIdeas } from './useIdeas';
import InputForm from './components/InputForm';
import LoadingPipeline from './components/LoadingPipeline';
import IdeaCard from './components/IdeaCard';
import HistoryPanel from './components/HistoryPanel';
import UploadPanel from './components/UploadPanel';
import BookmarksPanel from './components/BookmarksPanel';

export default function App() {
  const { 
    results, history, bookmarks, documents, loading, error, 
    generate, fetchHistory, fetchBookmarks, fetchDocuments,
    loadSession, regenerate, refineIdea, toggleBookmark, deleteDocument,
    chatWithKB, setError 
  } = useIdeas();

  const [activeTab, setActiveTab] = useState('generate');

  useEffect(() => { fetchHistory(); fetchBookmarks(); fetchDocuments(); }, [fetchHistory, fetchBookmarks, fetchDocuments]);

  return (
    <div className="min-h-screen relative">
      <div className="bg-mesh" />

      {/* Sidebar */}
      <HistoryPanel
        history={history}
        onSelect={(id) => { loadSession(id); setActiveTab('generate'); }}
        currentSessionId={results?.session_id}
      />

      {/* Main */}
      <main className="lg:pl-72 min-h-screen pb-20">
        
        {/* Navigation Tabs */}
        <div className="sticky top-0 z-40 backdrop-blur-xl bg-black/50 border-b border-white/5 pt-4 px-4 sm:px-6 lg:px-8 flex justify-center">
          <div className="flex space-x-1 glass p-1 rounded-xl mb-4">
            <button 
              onClick={() => setActiveTab('generate')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'generate' ? 'bg-white/10 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'}`}
            >
              Brainstorm
            </button>
            <button 
              onClick={() => setActiveTab('documents')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'documents' ? 'bg-white/10 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'}`}
            >
              Knowledge Base
            </button>
            <button 
              onClick={() => setActiveTab('bookmarks')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'bookmarks' ? 'bg-white/10 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'}`}
            >
              Saved Ideas
            </button>
          </div>
        </div>

        <div className="px-4 sm:px-6 lg:px-8 py-8 max-w-5xl mx-auto">
          
          {/* TAB: DOCUMENTS */}
          {activeTab === 'documents' && (
            <UploadPanel 
              documents={documents} 
              fetchDocuments={fetchDocuments}
              deleteDocument={deleteDocument}
              chatWithKB={chatWithKB}
            />
          )}

          {/* TAB: BOOKMARKS */}
          {activeTab === 'bookmarks' && (
            <BookmarksPanel 
              bookmarks={bookmarks} 
              fetchBookmarks={fetchBookmarks} 
              refineIdea={refineIdea}
              toggleBookmark={toggleBookmark}
            />
          )}

          {/* TAB: GENERATE */}
          {activeTab === 'generate' && (
            <>
              {/* Header */}
              <header className="text-center mb-10 pt-4">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-xs font-medium text-accent-cyan mb-5">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent-cyan animate-pulse" />
                  Agentic RAG Engine
                </div>
                <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight">
                  <span className="gradient-text">Agentic AI</span>
                  <br />
                  <span className="text-white">Brainstorming Assistant</span>
                </h1>
                <p className="text-slate-400 mt-4 text-base max-w-xl mx-auto leading-relaxed">
                  Provide any topic Across any Domain. Our multi-agent system will analyze, research, generate, evaluate, and refine the best ideas for you.
                </p>
              </header>

              {/* Input */}
              <InputForm onSubmit={generate} isLoading={loading} />

              {/* Error */}
              {error && (
                <div className="max-w-3xl mx-auto mt-6 p-4 rounded-xl bg-accent-rose/10 border border-accent-rose/20 text-accent-rose text-sm flex items-start gap-3">
                  <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div className="flex-1">
                    <p className="font-medium">Something went wrong</p>
                    <p className="text-accent-rose/70 mt-1">{error}</p>
                  </div>
                  <button onClick={() => setError(null)} className="text-accent-rose/50 hover:text-accent-rose cursor-pointer">✕</button>
                </div>
              )}

              {/* Loading */}
              {loading && <LoadingPipeline />}

              {/* Results */}
              {!loading && results && (
                <div className="w-full max-w-4xl mx-auto mt-10" id="results-section">
                  {results.context && (
                    <div className="glass rounded-2xl p-5 mb-6">
                      <div className="flex items-center justify-between flex-wrap gap-3">
                        <div>
                          <h2 className="text-lg font-bold text-white flex items-center gap-2">
                            <svg className="w-5 h-5 text-accent-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                            </svg>
                            {results.context.idea_type || 'Generated Ideas'}
                            {results.rag_sources > 0 && (
                              <span className="ml-2 text-[10px] uppercase tracking-wider bg-accent-cyan/20 text-accent-cyan px-2 py-0.5 rounded border border-accent-cyan/30">
                                RAG Grounded
                              </span>
                            )}
                          </h2>
                          <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-xs text-slate-400">
                            <span>Domain: <span className="text-slate-300">{results.context.domain}</span></span>
                            <span>Target: <span className="text-slate-300">{results.context.target_users}</span></span>
                            <span>Complexity: <span className="text-slate-300">{results.context.complexity}</span></span>
                            {results.context.sub_domains && <span>Sub: <span className="text-slate-300">{results.context.sub_domains.join(', ')}</span></span>}
                          </div>
                        </div>
                        <button
                          onClick={() => regenerate(results.session_id)}
                          disabled={loading}
                          className="px-4 py-2 rounded-xl text-xs font-medium border border-white/10 text-slate-300 hover:bg-white/[0.05] hover:text-white transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                        >
                          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                          Regenerate
                        </button>
                      </div>
                    </div>
                  )}

                  <div className="space-y-6">
                    {results.ideas
                      .sort((a, b) => a.rank - b.rank)
                      .map((idea, i) => (
                        <IdeaCard 
                          key={idea.id || i} 
                          idea={idea} 
                          index={i} 
                          onRefine={refineIdea}
                          onBookmark={toggleBookmark}
                        />
                      ))}
                  </div>
                </div>
              )}

              {/* Empty state */}
              {!loading && !results && !error && (
                <div className="text-center py-20">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-2xl glass flex items-center justify-center">
                    <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-slate-400 mb-2">Ready to brainstorm</h3>
                  <p className="text-sm text-slate-500 max-w-md mx-auto">
                    Enter a prompt above and let the AI pipeline generate structured, ranked project ideas for you.
                  </p>
                </div>
              )}
            </>
          )}

        </div>
      </main>
    </div>
  );
}
