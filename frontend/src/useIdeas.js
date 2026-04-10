import { useState, useCallback } from 'react';

const API = '/api';

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

// ── Hook ────────────────────────────────────────────────────────────────────

export function useIdeas() {
  const [results, setResults] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = useCallback(async () => {
    try {
      setHistory(await get(`${API}/history`));
    } catch (err) {
      console.error('History fetch failed:', err);
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

  return { results, history, loading, error, generate, fetchHistory, loadSession, regenerate, setError };
}
