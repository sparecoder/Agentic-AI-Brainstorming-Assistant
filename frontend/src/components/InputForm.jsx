import { useState } from 'react';

const DIFFICULTY_OPTIONS = ['Beginner', 'Intermediate', 'Advanced'];
const TIMELINE_OPTIONS = ['Hackathon', 'Semester', 'Long-term'];
const TECH_OPTIONS = ['Python', 'JavaScript / Web', 'Machine Learning', 'Mobile', 'Cloud / DevOps', 'Any'];

export default function InputForm({ onSubmit, isLoading }) {
  const [prompt, setPrompt] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [timeline, setTimeline] = useState('');
  const [techPreference, setTechPreference] = useState('');
  const [showOptions, setShowOptions] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    onSubmit({
      prompt: prompt.trim(),
      difficulty: difficulty || null,
      timeline: timeline || null,
      tech_preference: techPreference || null,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto" id="input-form">
      {/* Main prompt area */}
      <div className="glass rounded-2xl p-6 transition-all duration-300">
        <label htmlFor="prompt-input" className="block text-sm font-medium text-slate-400 mb-2">
          What kind of project ideas are you looking for?
        </label>
        <textarea
          id="prompt-input"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., Suggest AI + ML project ideas for healthcare that use computer vision..."
          rows={3}
          disabled={isLoading}
          className="w-full bg-transparent border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 resize-none focus:outline-none focus:border-accent-cyan/50 focus:ring-1 focus:ring-accent-cyan/30 transition-all duration-300 text-base"
        />

        {/* Toggle options */}
        <button
          type="button"
          onClick={() => setShowOptions(!showOptions)}
          className="mt-3 text-sm text-slate-400 hover:text-accent-cyan flex items-center gap-1.5 transition-colors"
          id="toggle-options-btn"
        >
          <svg
            className={`w-4 h-4 transition-transform duration-300 ${showOptions ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
          {showOptions ? 'Hide' : 'Show'} preferences
        </button>

        {/* Preference options */}
        {showOptions && (
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4 animate-[fade-in_0.3s_ease-out]">
            {/* Difficulty */}
            <div>
              <label htmlFor="difficulty-select" className="block text-xs font-medium text-slate-500 mb-1.5 uppercase tracking-wider">
                Difficulty
              </label>
              <select
                id="difficulty-select"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full bg-navy-800 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-accent-cyan/50 transition-colors appearance-none cursor-pointer"
              >
                <option value="">Any</option>
                {DIFFICULTY_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>

            {/* Timeline */}
            <div>
              <label htmlFor="timeline-select" className="block text-xs font-medium text-slate-500 mb-1.5 uppercase tracking-wider">
                Timeline
              </label>
              <select
                id="timeline-select"
                value={timeline}
                onChange={(e) => setTimeline(e.target.value)}
                className="w-full bg-navy-800 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-accent-cyan/50 transition-colors appearance-none cursor-pointer"
              >
                <option value="">Any</option>
                {TIMELINE_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>

            {/* Tech Preference */}
            <div>
              <label htmlFor="tech-select" className="block text-xs font-medium text-slate-500 mb-1.5 uppercase tracking-wider">
                Tech Preference
              </label>
              <select
                id="tech-select"
                value={techPreference}
                onChange={(e) => setTechPreference(e.target.value)}
                className="w-full bg-navy-800 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-accent-cyan/50 transition-colors appearance-none cursor-pointer"
              >
                <option value="">Any</option>
                {TECH_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Submit button */}
        <div className="mt-5 flex justify-end">
          <button
            type="submit"
            disabled={!prompt.trim() || isLoading}
            className="btn-gradient px-8 py-3 rounded-xl font-semibold text-white text-sm tracking-wide flex items-center gap-2 cursor-pointer"
            id="generate-btn"
          >
            {isLoading ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Generating...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Generate Ideas
              </>
            )}
          </button>
        </div>
      </div>
    </form>
  );
}
