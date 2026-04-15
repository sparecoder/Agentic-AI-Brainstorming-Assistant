import { useState, useEffect } from 'react';
import { uploadFile } from '../useIdeas';

export default function UploadPanel({ documents, fetchDocuments, deleteDocument, chatWithKB }) {
  const [uploading, setUploading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState(null);

  const [chatLoading, setChatLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [msgInput, setMsgInput] = useState('');

  useEffect(() => {
    setFetching(true);
    fetchDocuments().finally(() => setFetching(false));
  }, [fetchDocuments]);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (file.type !== 'application/pdf') {
      setError('Only PDF files are supported.');
      return;
    }

    setUploading(true);
    setError(null);
    try {
      await uploadFile(file);
      fetchDocuments();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      e.target.value = ''; // Reset input
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!msgInput.trim() || chatLoading) return;

    const userMsg = { role: 'user', content: msgInput };
    setMessages(prev => [...prev, userMsg]);
    setMsgInput('');
    setChatLoading(true);

    try {
      const data = await chatWithKB(msgInput);
      setMessages(prev => [...prev, { role: 'ai', content: data.answer, sources: data.sources }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'error', content: err.message }]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left: Upload & Documents List */}
        <div className="space-y-8">
          <div className="glass rounded-2xl p-6">
            <h2 className="text-xl font-bold text-white mb-2">Knowledge Base</h2>
            <p className="text-slate-400 text-sm mb-6 leading-relaxed">
              Upload domain-specific documents (PDFs) to ground the AI's ideas in real data. The Researcher Agent will silently query this knowledge base during generation.
            </p>

            <div className="border-2 border-dashed border-white/10 rounded-xl p-8 text-center hover:border-accent-cyan/50 transition-colors">
              <input
                type="file"
                id="pdf-upload"
                className="hidden"
                accept="application/pdf"
                onChange={handleFileChange}
                disabled={uploading}
              />
              <label htmlFor="pdf-upload" className="cursor-pointer flex flex-col items-center">
                <div className="w-12 h-12 rounded-full glass flex items-center justify-center mb-3">
                  {uploading ? (
                    <svg className="w-6 h-6 text-accent-cyan animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : (
                    <svg className="w-6 h-6 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  )}
                </div>
                <span className="text-sm font-medium text-slate-300">
                  {uploading ? 'Processing document...' : 'Click to upload PDF'}
                </span>
                <span className="text-xs text-slate-500 mt-1">Maximum 10MB</span>
              </label>
            </div>
            {error && <p className="text-accent-rose text-sm mt-3">{error}</p>}
          </div>

          <div className="space-y-4">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Uploaded Documents</h3>
            {fetching ? (
              <div className="space-y-3">
                {[1, 2].map(i => (
                  <div key={i} className="glass p-4 rounded-xl animate-pulse flex items-center gap-3">
                    <div className="w-8 h-8 rounded bg-white/5" />
                    <div className="flex-1 space-y-2">
                      <div className="h-3 bg-white/5 rounded w-1/2" />
                      <div className="h-2 bg-white/5 rounded w-1/4" />
                    </div>
                  </div>
                ))}
              </div>
            ) : documents.length === 0 ? (
              <p className="text-slate-500 text-sm">No documents uploaded yet.</p>
            ) : (
              <div className="flex flex-col gap-3">
                {documents.map(doc => (
                  <div key={doc.id} className="glass p-4 rounded-xl flex items-center justify-between">
                    <div className="flex items-center gap-3 overflow-hidden">
                      <svg className="w-8 h-8 text-accent-rose flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-white truncate">{doc.filename}</p>
                        <p className="text-[10px] text-slate-400 font-mono tracking-tighter uppercase">{doc.total_chunks} blocks indexed</p>
                      </div>
                    </div>
                    <button
                      onClick={() => deleteDocument(doc.id)}
                      className="p-2 text-slate-500 hover:text-accent-rose hover:bg-accent-rose/10 rounded-lg transition-colors cursor-pointer"
                    >
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: Knowledge Base Chat */}
        <div className="glass rounded-2xl flex flex-col h-[600px] overflow-hidden border border-white/10">
          <div className="p-4 border-b border-white/5 bg-white/[0.02]">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <svg className="w-4 h-4 text-accent-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              Chat with Knowledge Base
            </h3>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center opacity-40">
                <svg className="w-12 h-12 mb-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M3 10h10a8 8 0 018 8v2M3 10l5 5m-5-5l5-5" />
                </svg>
                <p className="text-xs">Select a document and ask a question about the research.</p>
              </div>
            ) : (
              messages.map((m, idx) => (
                <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] p-3 rounded-2xl text-sm ${
                    m.role === 'user' 
                      ? 'bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/20' 
                      : m.role === 'error'
                        ? 'bg-accent-rose/20 text-accent-rose border border-accent-rose/20'
                        : 'bg-white/5 text-slate-200 border border-white/5'
                  }`}>
                    {m.content}
                    {m.sources && m.sources.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-white/5 flex flex-wrap gap-1">
                        {m.sources.map((s, i) => (
                          <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-slate-400">
                            {s}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-white/5 p-3 rounded-2xl flex gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce" />
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce delay-75" />
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce delay-150" />
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <form onSubmit={handleChat} className="p-4 border-t border-white/5 bg-black/20">
            <div className="relative">
              <input
                type="text"
                placeholder={documents.length > 0 ? "Ask about your data..." : "Upload documents to start chatting..."}
                disabled={documents.length === 0 || chatLoading}
                value={msgInput}
                onChange={(e) => setMsgInput(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-4 pr-12 text-sm text-white focus:outline-none focus:border-accent-cyan disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={documents.length === 0 || chatLoading || !msgInput.trim()}
                className="absolute right-2 top-2 bottom-2 px-3 rounded-lg bg-accent-cyan text-black hover:bg-accent-cyan/80 transition-all disabled:opacity-50 disabled:grayscale cursor-pointer"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
