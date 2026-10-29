import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const EXAMPLES = [
  'Build an e-commerce platform for handcrafted items with live chat and payments...',
  'Create a telemedicine app with video calls, doctor booking, and EHR integration...',
  'Design a food delivery service with real-time GPS tracking and live order updates...',
  'Build an AI-powered code review tool with GitHub integration and automated metrics...',
];

const STARTERS = [
  { label: '🛒 E-Commerce', prompt: 'Build an e-commerce app for handmade crafts with payments, cart, and seller dashboard.' },
  { label: '🏥 Telemedicine', prompt: 'Create a telemedicine platform with video consultations, doctor booking, and medical records.' },
  { label: '📦 Delivery Tracker', prompt: 'Design a food delivery app with real-time GPS tracking, order management, and live chat.' },
  { label: '🤖 AI Learning Platform', prompt: 'Build a learning platform with video courses, interactive quizzes, progress tracking, and certificates.' },
];

export default function PromptInput({ onSubmit, isLoading, errorMessage, onClearError }) {
  const [idea, setIdea] = useState('');
  const [exampleIndex, setExampleIndex] = useState(0);
  const textareaRef = useRef(null);

  // Rotate placeholder every 4 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      setExampleIndex((prev) => (prev + 1) % EXAMPLES.length);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  // Auto-dismiss error message after 5s
  useEffect(() => {
    if (errorMessage) {
      const timer = setTimeout(() => {
        if (onClearError) onClearError();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [errorMessage, onClearError]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (idea.trim() && !isLoading) {
      onSubmit(idea.trim());
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSelectStarter = (promptText) => {
    setIdea(promptText);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="w-full max-w-4xl mx-auto flex flex-col items-center px-4 py-8"
    >
      {/* Headline */}
      <div className="text-center mb-6">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tight leading-tight">
          <span className="gradient-text block">Prompt in,</span>
          <span className="block" style={{ color: 'var(--text-primary)' }}>project plan out.</span>
        </h1>
        <p className="mt-4 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          Describe your software idea in plain English. Get an architecture diagram,
          development task board, cloud costs, and milestone roadmap — instantly.
        </p>
      </div>

      {/* Error State Banner */}
      <AnimatePresence>
        {errorMessage && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="w-full mb-4 p-4 rounded-xl bg-red-500/10 border border-red-500/40 text-red-500 text-sm flex items-center justify-between shadow-sm"
          >
            <div className="flex items-center gap-2">
              <span className="text-lg">⚠️</span>
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={onClearError}
              className="text-red-500 hover:underline text-xs px-2 py-1 rounded bg-red-500/20 cursor-pointer"
            >
              Dismiss
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="w-full flex flex-col items-center">
        {/* Quick Starters Pills */}
        <div className="flex flex-wrap items-center justify-center gap-2 mb-4">
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
            Quick Starters:
          </span>
          {STARTERS.map((item) => (
            <button
              key={item.label}
              type="button"
              onClick={() => handleSelectStarter(item.prompt)}
              className="text-xs px-3.5 py-1.5 rounded-full border transition-all duration-200 cursor-pointer shadow-sm hover:border-[var(--accent-color)] hover:scale-105"
              style={{
                backgroundColor: 'var(--bg-surface)',
                borderColor: 'var(--border-subtle)',
                color: 'var(--text-secondary)',
              }}
            >
              {item.label}
            </button>
          ))}
        </div>

        {/* Textarea Box */}
        <div className="relative w-full">
          <textarea
            ref={textareaRef}
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={EXAMPLES[exampleIndex]}
            disabled={isLoading}
            rows={4}
            className="w-full h-[140px] p-4 rounded-2xl border text-base outline-none resize-none transition-all duration-200 focus:border-[var(--accent-color)] focus:ring-2 focus:ring-[var(--accent-color)]/30 disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
            style={{
              backgroundColor: 'var(--bg-surface)',
              borderColor: 'var(--border-subtle)',
              color: 'var(--text-primary)',
            }}
          />
          <div className="absolute bottom-3 right-4 text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
            {idea.length} chars
          </div>
        </div>

        {/* Generate Button */}
        <motion.button
          type="submit"
          disabled={!idea.trim() || isLoading}
          whileHover={idea.trim() && !isLoading ? { scale: 1.02 } : {}}
          whileTap={idea.trim() && !isLoading ? { scale: 0.95 } : {}}
          className={`w-full mt-5 py-4 rounded-2xl font-bold text-base flex items-center justify-center gap-2.5 transition-all duration-200 shadow-lg ${
            !idea.trim() || isLoading
              ? 'opacity-50 cursor-not-allowed'
              : 'gradient-bg text-white hover:brightness-110 gradient-glow cursor-pointer'
          }`}
          style={
            !idea.trim() || isLoading
              ? { backgroundColor: 'var(--bg-elevated)', color: 'var(--text-muted)' }
              : {}
          }
        >
          {isLoading ? (
            <>
              <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span>Generating Plan...</span>
            </>
          ) : (
            <>
              <span>Generate Project Plan</span>
              <span className="text-xl">⚡</span>
            </>
          )}
        </motion.button>
      </form>

      {/* Feature Tags Badges */}
      <div className="flex flex-wrap justify-center items-center gap-2.5 mt-8">
        {[
          '🏗️ Architecture Diagram',
          '📋 Task Breakdown',
          '📅 Milestone Timeline',
          '🤖 AI-Powered',
        ].map((tag) => (
          <span
            key={tag}
            className="text-xs px-3.5 py-1.5 rounded-full border font-medium shadow-sm"
            style={{
              backgroundColor: 'var(--bg-surface)',
              borderColor: 'var(--border-subtle)',
              color: 'var(--text-secondary)',
            }}
          >
            {tag}
          </span>
        ))}
      </div>
    </motion.div>
  );
}

