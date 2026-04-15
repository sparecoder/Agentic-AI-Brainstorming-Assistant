import { useEffect } from 'react';
import IdeaCard from './IdeaCard';

export default function BookmarksPanel({ bookmarks, fetchBookmarks, refineIdea, toggleBookmark }) {
  useEffect(() => {
    fetchBookmarks();
  }, [fetchBookmarks]);

  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="mb-8">
        <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
          <svg className="w-6 h-6 text-accent-cyan" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
          </svg>
          Saved Ideas
        </h2>
        <p className="text-slate-400 text-sm">
          A collection of your favorite ideas across all brainstorming sessions.
        </p>
      </div>

      {bookmarks.length === 0 ? (
        <div className="text-center py-16 glass rounded-2xl">
          <svg className="w-12 h-12 text-slate-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <p className="text-slate-400 text-sm">No ideas bookmarked yet.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {bookmarks.map((bm, index) => (
            <div key={bm.id} className="relative">
              {bm.note && (
                <div className="absolute -top-3 left-4 bg-accent-rose text-black text-[10px] font-bold px-2 py-0.5 rounded shadow-lg z-10">
                  NOTE: {bm.note}
                </div>
              )}
              <IdeaCard 
                idea={bm.idea} 
                index={index} 
                onRefine={refineIdea} 
                onBookmark={toggleBookmark} 
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
