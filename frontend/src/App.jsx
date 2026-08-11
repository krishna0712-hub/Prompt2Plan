import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import PromptInput from './components/PromptInput';
import LoadingAnimation from './components/LoadingAnimation';
import ProjectHeader from './components/ProjectHeader';
import ArchitectureDiagram from './components/ArchitectureDiagram';
import TaskBoard from './components/TaskBoard';
import Timeline from './components/Timeline';
import OverviewCost from './components/OverviewCost';

const TABS = [
  { id: 'overview', label: 'Overview & Costs', icon: '📊' },
  { id: 'architecture', label: 'Architecture', icon: '🏗️' },
  { id: 'tasks', label: 'Tasks', icon: '📋' },
  { id: 'timeline', label: 'Timeline', icon: '📅' },
];

export default function App() {
  const [loading, setLoading] = useState(false);
  const [projectData, setProjectData] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [history, setHistory] = useState([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/projects');
      if (res.ok) {
        const data = await res.json();
        if (data.success) {
          setHistory(data.data || []);
        }
      }
    } catch (e) {
      console.error('Failed to fetch history:', e);
    }
  };

  const loadProject = async (id) => {
    setLoading(true);
    setError(null);
    setIsHistoryOpen(false);
    try {
      const res = await fetch(`/api/projects/${id}`);
      if (!res.ok) throw new Error('Project not found');
      const data = await res.json();
      if (data.success && data.data) {
        setProjectData(data.data);
        setActiveTab('overview');
      }
    } catch (err) {
      setError(err.message || 'Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePlan = async (idea) => {
    setLoading(true);
    setError(null);
    setProjectData(null);

    try {
      const response = await fetch('/api/generate-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea }),
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server error (${response.status})`);
      }

      const data = await response.json();
      if (data.success && data.data) {
        setProjectData(data.data);
        setActiveTab('overview');
      } else {
        throw new Error('Invalid server response format');
      }
    } catch (err) {
      console.error('Plan generation error:', err);
      setError(err.message || 'Failed to generate plan. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNewPlan = () => {
    setProjectData(null);
    setError(null);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0A0A0F] text-white font-sans selection:bg-[#7C5CFF]/30 selection:text-white">
      {/* Fixed Glass-Morphism Header */}
      <header className="sticky top-0 z-50 w-full glass-morphism px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3 cursor-pointer" onClick={handleNewPlan}>
          {/* Logo */}
          <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center font-extrabold text-sm text-white shadow-lg gradient-glow">
            P2P
          </div>

          <div className="flex items-center gap-2">
            <h1 className="text-xl font-extrabold tracking-tight">
              <span className="gradient-text">Prompt2Plan</span>
            </h1>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#1E1E28] text-[#9B7BFF] border border-[#7C5CFF]/30 font-semibold">
              v2.0
            </span>
          </div>
        </div>

        {/* Header Right Actions */}
        <div className="flex items-center gap-4 relative">
          {/* Status Indicator Green Pulse Dot */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#13131A] border border-[#1E1E28] text-xs font-mono text-[#A0A0B0]">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#10B981] opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#10B981]" />
            </span>
            <span>API Ready</span>
          </div>

          <button
            onClick={() => {
              if (!isHistoryOpen) fetchHistory();
              setIsHistoryOpen(!isHistoryOpen);
            }}
            className="text-xs font-semibold px-3.5 py-2 rounded-xl bg-[#13131A] text-[#A0A0B0] border border-[#1E1E28] hover:text-white hover:border-[#7C5CFF] transition-all cursor-pointer"
          >
            📜 History
          </button>

          {/* History Dropdown */}
          <AnimatePresence>
            {isHistoryOpen && (
              <motion.div
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                className="absolute right-0 top-12 w-80 rounded-2xl bg-[#13131A] border border-[#1E1E28] shadow-2xl p-3 z-50"
              >
                <div className="text-xs font-bold text-[#6B6B7B] uppercase tracking-wider px-2 py-1 border-b border-[#1E1E28] mb-2">
                  Recent Saved Plans
                </div>
                <div className="max-h-60 overflow-y-auto space-y-1">
                  {history.length === 0 ? (
                    <div className="text-center py-4 text-xs text-[#6B6B7B]">
                      No previous plans found
                    </div>
                  ) : (
                    history.map((p) => (
                      <button
                        key={p.id}
                        onClick={() => loadProject(p.id)}
                        className="w-full text-left p-2.5 rounded-xl text-xs hover:bg-[#1E1E28] transition-colors"
                      >
                        <div className="font-bold text-white mb-0.5">Plan #{p.id}</div>
                        <div className="text-[#A0A0B0] truncate">{p.idea_text}</div>
                      </button>
                    ))
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 py-8 sm:py-12">
        <AnimatePresence mode="wait">
          {/* HERO STATE */}
          {!projectData && !loading && (
            <motion.div
              key="hero"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <PromptInput
                onSubmit={handleGeneratePlan}
                isLoading={loading}
                errorMessage={error}
                onClearError={() => setError(null)}
              />
            </motion.div>
          )}

          {/* LOADING STATE */}
          {loading && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <LoadingAnimation />
            </motion.div>
          )}

          {/* RESULTS STATE */}
          {projectData && !loading && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              {/* Project Header Component */}
              <ProjectHeader project={projectData} onNewPlan={handleNewPlan} />

              {/* Tab Navigation */}
              <div className="flex items-center gap-2 mb-6 p-1.5 bg-[#13131A] border border-[#1E1E28] rounded-2xl w-fit flex-wrap">
                {TABS.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`text-xs font-semibold px-4 py-2.5 rounded-xl transition-all flex items-center gap-2 cursor-pointer ${
                      activeTab === tab.id
                        ? 'bg-[#7C5CFF] text-white shadow-[0_0_15px_rgba(124,92,255,0.4)]'
                        : 'text-[#A0A0B0] hover:text-white hover:bg-[#1E1E28]'
                    }`}
                  >
                    <span>{tab.icon}</span>
                    <span>{tab.label}</span>
                  </button>
                ))}
              </div>

              {/* Tab Content Rendering */}
              <AnimatePresence mode="wait">
                {activeTab === 'overview' && (
                  <motion.div key="overview" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <OverviewCost result={projectData} />
                  </motion.div>
                )}
                {activeTab === 'architecture' && (
                  <motion.div key="architecture" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <ArchitectureDiagram architecture={projectData.architecture} />
                  </motion.div>
                )}
                {activeTab === 'tasks' && (
                  <motion.div key="tasks" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <TaskBoard
                      projectId={projectData.id}
                      tasks={projectData.tasks}
                      onUpdateResult={(updated) => setProjectData((prev) => ({ ...prev, ...updated }))}
                    />
                  </motion.div>
                )}
                {activeTab === 'timeline' && (
                  <motion.div key="timeline" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <Timeline milestones={projectData.milestones} tasks={projectData.tasks} />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-[#1E1E28] py-6 px-6 text-center text-xs text-[#6B6B7B]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            © 2026 Prompt2Plan ⚡ AI-Powered Software Architecture & Project Planning
          </div>
          <div className="flex items-center gap-4 text-[#A0A0B0]">
            <span>FastAPI + React 18</span>
            <span>•</span>
            <span>Mermaid.js</span>
            <span>•</span>
            <span>Tailwind CSS</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
