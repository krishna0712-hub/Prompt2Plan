import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

function getComplexityBadge(level) {
  const l = (level || '').toLowerCase();
  if (l.includes('very high') || l.includes('high')) {
    return { text: level || 'High Complexity', bg: 'bg-red-500/10', textCol: 'text-red-400', border: 'border-red-500/30' };
  }
  if (l.includes('medium') || l.includes('moderate')) {
    return { text: level || 'Medium Complexity', bg: 'bg-amber-500/10', textCol: 'text-amber-400', border: 'border-amber-500/30' };
  }
  return { text: level || 'Low Complexity', bg: 'bg-emerald-500/10', textCol: 'text-emerald-400', border: 'border-emerald-500/30' };
}

export default function ProjectHeader({ project, onNewPlan }) {
  const [isExportOpen, setIsExportOpen] = useState(false);

  if (!project) return null;

  const badge = getComplexityBadge(project.risk_analysis?.complexity_level);
  const formattedDate = project.created_at
    ? new Date(project.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
    : 'Just now';

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full border rounded-2xl p-6 mb-8 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl"
      style={{
        backgroundColor: 'var(--bg-surface)',
        borderColor: 'var(--border-subtle)',
      }}
    >
      {/* Left Details */}
      <div className="space-y-2">
        <div className="flex items-center gap-3 flex-wrap">
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>
            Project Plan #{project.id}
          </h2>
          <span className={`text-xs px-3 py-1 rounded-full font-mono font-semibold border ${badge.bg} ${badge.textCol} ${badge.border}`}>
            {badge.text}
          </span>
          <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
            Created: {formattedDate}
          </span>
        </div>
        <p className="text-sm sm:text-base font-normal leading-relaxed max-w-3xl" style={{ color: 'var(--text-secondary)' }}>
          "{project.idea_text}"
        </p>
      </div>

      {/* Right Action Buttons */}
      <div className="flex items-center gap-3 relative flex-wrap shrink-0">
        {/* Export Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsExportOpen(!isExportOpen)}
            className="text-xs font-semibold px-4 py-2.5 rounded-xl border transition-all flex items-center gap-2 cursor-pointer shadow-sm hover:border-[var(--accent-color)]"
            style={{
              backgroundColor: 'var(--bg-elevated)',
              borderColor: 'var(--border-subtle)',
              color: 'var(--text-primary)',
            }}
          >
            <span>📥 Export Plan</span>
            <span>{isExportOpen ? '▲' : '▼'}</span>
          </button>

          <AnimatePresence>
            {isExportOpen && (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 top-12 w-52 rounded-xl border shadow-2xl p-2 z-50 space-y-1"
                style={{
                  backgroundColor: 'var(--bg-surface)',
                  borderColor: 'var(--border-subtle)',
                }}
              >
                <a
                  href={`/api/projects/${project.id}/export?format=markdown`}
                  target="_blank"
                  rel="noreferrer"
                  className="block text-xs px-3 py-2 rounded-lg transition-colors hover:bg-[var(--bg-elevated)]"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  📝 Markdown (.md)
                </a>
                <a
                  href={`/api/projects/${project.id}/export?format=json`}
                  target="_blank"
                  rel="noreferrer"
                  className="block text-xs px-3 py-2 rounded-lg transition-colors hover:bg-[var(--bg-elevated)]"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  📦 JSON Data (.json)
                </a>
                <a
                  href={`/api/projects/${project.id}/export?format=jira_csv`}
                  target="_blank"
                  rel="noreferrer"
                  className="block text-xs px-3 py-2 rounded-lg transition-colors hover:bg-[var(--bg-elevated)]"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  🔷 Jira Import (.csv)
                </a>
                <a
                  href={`/api/projects/${project.id}/export?format=github_csv`}
                  target="_blank"
                  rel="noreferrer"
                  className="block text-xs px-3 py-2 rounded-lg transition-colors hover:bg-[var(--bg-elevated)]"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  🐙 GitHub Issues (.csv)
                </a>
                <a
                  href={`/api/projects/${project.id}/export?format=pdf`}
                  target="_blank"
                  rel="noreferrer"
                  className="block text-xs px-3 py-2 rounded-lg transition-colors hover:bg-[var(--bg-elevated)]"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  📄 Report / Printable PDF
                </a>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* New Plan Button */}
        <motion.button
          onClick={onNewPlan}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.95 }}
          className="text-xs font-bold px-4 py-2.5 rounded-xl gradient-bg text-white shadow-md cursor-pointer flex items-center gap-1.5"
        >
          <span>+</span> New Plan
        </motion.button>
      </div>
    </motion.div>
  );
}

