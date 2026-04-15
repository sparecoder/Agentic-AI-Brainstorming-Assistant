import { useState, useCallback } from 'react';

// Use environment variable for production API, fallback to local proxy for dev
const API = import.meta.env.VITE_API_URL || '/api';

// ── API helpers ─────────────────────────────────────────────────────────────

async function post(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

async function get(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

async function del(url) {
  const res = await fetch(url, { method: 'DELETE' });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API}/upload-document`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

// ── Hook ────────────────────────────────────────────────────────────────────

export function useIdeas() {
  const [results, setResults] = useState(null);
  const [history, setHistory] = useState([]);
  const [bookmarks, setBookmarks] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = useCallback(async () => {
    try {
      setHistory(await get(`${API}/history`));
    } catch (err) {
      console.error('History fetch failed:', err);
    }
  }, []);

  const fetchBookmarks = useCallback(async () => {
    try {
      setBookmarks(await get(`${API}/bookmarks`));
    } catch (err) {
      console.error('Bookmarks fetch failed:', err);
    }
  }, []);

  const fetchDocuments = useCallback(async () => {
    try {
      setDocuments(await get(`${API}/documents`));
    } catch (err) {
      console.error('Documents fetch failed:', err);
    }
  }, []);

  const generate = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const data = await post(`${API}/generate-ideas`, payload);
      setResults(data);
      fetchHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [fetchHistory]);

  const loadSession = useCallback(async (sessionId) => {
    setLoading(true);
    setError(null);
    try {
      const data = await get(`${API}/history/${sessionId}`);
      setResults({
        session_id: data.id,
        context: data.extracted_context,
        ideas: data.ideas,
        created_at: data.created_at,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const regenerate = useCallback(async (sessionId) => {
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const data = await post(`${API}/regenerate/${sessionId}`);
      setResults(data);
      fetchHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [fetchHistory]);

  const refineIdea = useCallback(async (ideaId, instruction) => {
    setLoading(true);
    setError(null);
    try {
      const updatedIdea = await post(`${API}/refine-idea/${ideaId}`, { instruction });
      // Update the local results state
      setResults(prev => {
        if (!prev) return prev;
        return {
          ...prev,
          ideas: prev.ideas.map(i => i.id === ideaId ? updatedIdea : i)
        };
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const toggleBookmark = useCallback(async (ideaId, note = null) => {
    try {
      await post(`${API}/bookmark/${ideaId}`, { note });
      // Update local ideas state
      setResults(prev => {
        if (!prev) return prev;
        return {
          ...prev,
          ideas: prev.ideas.map(i => i.id === ideaId ? { ...i, is_bookmarked: !i.is_bookmarked } : i)
        };
      });
      // Refresh bookmarks list
      fetchBookmarks();
    } catch (err) {
      console.error('Bookmark toggle failed:', err);
    }
  }, [fetchBookmarks]);

  const deleteDocument = useCallback(async (docId) => {
    try {
      await del(`${API}/documents/${docId}`);
      fetchDocuments();
    } catch (err) {
      console.error('Delete document failed:', err);
    }
  }, [fetchDocuments]);

  const chatWithKB = useCallback(async (message) => {
    return await post(`${API}/chat-kb`, { message });
  }, []);

  return { 
    results, history, bookmarks, documents, loading, error, 
    generate, fetchHistory, fetchBookmarks, fetchDocuments,
    loadSession, regenerate, refineIdea, toggleBookmark, deleteDocument,
    chatWithKB, setError 
  };
}
