import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';

const COLUMNS = {
  todo: { title: 'To Do', icon: '📋', color: '#A0A0B0' },
  in_progress: { title: 'In Progress', icon: '🔨', color: '#F59E0B' },
  done: { title: 'Done', icon: '✅', color: '#10B981' },
};

const PHASES = [
  'Setup & Infrastructure',
  'Core Development',
  'Testing & QA',
  'Deployment & Launch',
];

export default function TaskBoard({ projectId, tasks, onUpdateResult }) {
  const [activePhase, setActivePhase] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newTaskName, setNewTaskName] = useState('');
  const [newTaskComponent, setNewTaskComponent] = useState('');
  const [newTaskPhase, setNewTaskPhase] = useState('Core Development');
  const [newTaskHours, setNewTaskHours] = useState(4);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const buildInitialColumns = (taskList) => {
    const cols = { todo: [], in_progress: [], done: [] };
    (taskList || []).forEach((t) => {
      const statusKey = t.status && cols[t.status] ? t.status : 'todo';
      cols[statusKey].push({ ...t });
    });
    return cols;
  };

  const [columns, setColumns] = useState(() => buildInitialColumns(tasks));

  useEffect(() => {
    setColumns(buildInitialColumns(tasks));
  }, [tasks]);

  const uniquePhases = ['All', ...new Set((tasks || []).map((t) => t.phase).filter(Boolean))];

  const filterTaskList = (taskList) => {
    return (taskList || []).filter((t) => {
      const matchesPhase = activePhase === 'All' || t.phase === activePhase;
      const matchesSearch =
        !searchQuery ||
        (t.name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (t.component || '').toLowerCase().includes(searchQuery.toLowerCase());
      return matchesPhase && matchesSearch;
    });
  };

  // Drag-and-drop end handler
  const handleDragEnd = async (result) => {
    const { source, destination, draggableId } = result;
    if (!destination) return;

    const sourceColId = source.droppableId;
    const destColId = destination.droppableId;

    if (sourceColId === destColId && source.index === destination.index) return;

    const numericTaskId = draggableId.startsWith('task-')
      ? parseInt(draggableId.replace('task-', ''), 10)
      : parseInt(draggableId, 10);

    // Optimistic UI state update
    const sourceList = [...columns[sourceColId]];
    const destList = sourceColId === destColId ? sourceList : [...columns[destColId]];

    const itemIndex = sourceList.findIndex((t) => t.id === numericTaskId || `task-${t.id}` === draggableId);
    if (itemIndex === -1) return;

    const [movedTask] = sourceList.splice(itemIndex, 1);
    movedTask.status = destColId;

    if (sourceColId === destColId) {
      sourceList.splice(destination.index, 0, movedTask);
      setColumns((prev) => ({ ...prev, [sourceColId]: sourceList }));
    } else {
      destList.splice(destination.index, 0, movedTask);
      setColumns((prev) => ({
        ...prev,
        [sourceColId]: sourceList,
        [destColId]: destList,
      }));
    }

    // Backend sync if real project ID exists
    if (projectId && numericTaskId) {
      try {
        const res = await fetch(`/api/projects/${projectId}/tasks/${numericTaskId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: destColId }),
        });
        if (res.ok) {
          const data = await res.json();
          if (data.success && onUpdateResult) {
            onUpdateResult(data.data);
          }
        }
      } catch (err) {
        console.error('Failed to update task status:', err);
      }
    }
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    if (!newTaskName.trim() || !projectId) return;

    setIsSubmitting(true);
    try {
      const res = await fetch(`/api/projects/${projectId}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newTaskName.trim(),
          component: newTaskComponent.trim() || 'General',
          phase: newTaskPhase,
          estimated_hours: parseFloat(newTaskHours) || 4.0,
          status: 'todo',
        }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.success && onUpdateResult) {
          onUpdateResult(data.data);
          setIsAddModalOpen(false);
          setNewTaskName('');
          setNewTaskComponent('');
        }
      }
    } catch (err) {
      console.error('Failed to add task:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!projectId || !taskId) return;
    try {
      const res = await fetch(`/api/projects/${projectId}/tasks/${taskId}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        const data = await res.json();
        if (data.success && onUpdateResult) {
          onUpdateResult(data.data);
        }
      }
    } catch (err) {
      console.error('Failed to delete task:', err);
    }
  };

  const allTaskList = tasks || [];
  const totalTasks = allTaskList.length;
  const totalHours = allTaskList.reduce((sum, t) => sum + (t.estimated_hours || 0), 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full border rounded-2xl p-6 shadow-xl mb-8"
      style={{
        backgroundColor: 'var(--bg-surface)',
        borderColor: 'var(--border-subtle)',
      }}
    >
      {/* Header Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
        <div>
          <h3 className="text-lg font-bold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <span>📋</span> Development Task Board
          </h3>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
            Kanban view grouped by phase with drag-and-drop support
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <input
            type="text"
            placeholder="Filter tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="text-xs px-3.5 py-2 rounded-xl border outline-none focus:border-[var(--accent-color)] shadow-sm"
            style={{
              backgroundColor: 'var(--bg-base)',
              borderColor: 'var(--border-subtle)',
              color: 'var(--text-primary)',
            }}
          />
          {projectId && (
            <button
              onClick={() => setIsAddModalOpen(true)}
              className="text-xs font-bold px-3.5 py-2 rounded-xl gradient-bg text-white shadow-md hover:brightness-110 cursor-pointer"
            >
              + Add Task
            </button>
          )}
        </div>
      </div>

      {/* Phase Filter Chips */}
      <div className="flex flex-wrap gap-2 mb-6">
        {uniquePhases.map((phase) => (
          <button
            key={phase}
            onClick={() => setActivePhase(phase)}
            className={`text-xs px-3 py-1.5 rounded-full font-medium transition-all cursor-pointer ${
              activePhase === phase
                ? 'gradient-bg text-white shadow-sm'
                : 'border hover:border-[var(--accent-color)]'
            }`}
            style={
              activePhase !== phase
                ? {
                    backgroundColor: 'var(--bg-base)',
                    borderColor: 'var(--border-subtle)',
                    color: 'var(--text-secondary)',
                  }
                : {}
            }
          >
            {phase === 'All' ? '🏷️ All Phases' : phase}
          </button>
        ))}
      </div>

      {/* Kanban Drag and Drop Columns */}
      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(COLUMNS).map(([colId, colMeta]) => {
            const colTasks = filterTaskList(columns[colId]);
            return (
              <div
                key={colId}
                className="border rounded-xl flex flex-col min-h-[350px] shadow-sm"
                style={{
                  backgroundColor: 'var(--bg-base)',
                  borderColor: 'var(--border-subtle)',
                }}
              >
                {/* Column Header */}
                <div className="p-4 border-b flex items-center justify-between" style={{ borderColor: 'var(--border-subtle)' }}>
                  <div className="flex items-center gap-2">
                    <span>{colMeta.icon}</span>
                    <span className="font-semibold text-sm" style={{ color: colMeta.color }}>
                      {colMeta.title}
                    </span>
                  </div>
                  <span
                    className="text-xs font-mono font-bold px-2 py-0.5 rounded-full border"
                    style={{
                      backgroundColor: 'var(--bg-surface)',
                      borderColor: 'var(--border-subtle)',
                      color: 'var(--text-muted)',
                    }}
                  >
                    {colTasks.length}
                  </span>
                </div>

                {/* Droppable Container */}
                <Droppable droppableId={colId}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className={`p-3 flex-1 transition-colors space-y-3 ${
                        snapshot.isDraggingOver ? 'bg-[var(--accent-color)]/10' : ''
                      }`}
                    >
                      {colTasks.map((task, index) => {
                        const dragId = `task-${task.id || index}`;
                        return (
                          <Draggable key={dragId} draggableId={dragId} index={index}>
                            {(provided, snapshot) => (
                              <div
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                {...provided.dragHandleProps}
                                className={`p-3.5 rounded-xl border transition-all group relative cursor-grab active:cursor-grabbing shadow-sm ${
                                  snapshot.isDragging ? 'scale-[1.02] shadow-xl border-[var(--accent-color)]' : ''
                                }`}
                                style={{
                                  backgroundColor: 'var(--bg-surface)',
                                  borderColor: 'var(--border-subtle)',
                                }}
                              >
                                {/* Delete Button */}
                                {projectId && task.id && (
                                  <button
                                    onClick={() => handleDeleteTask(task.id)}
                                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 text-xs px-1.5 py-0.5 rounded text-red-500 hover:bg-red-500/20 transition-all cursor-pointer"
                                  >
                                    ✕
                                  </button>
                                )}

                                {/* Task Name */}
                                <p className="text-sm font-semibold leading-snug line-clamp-2 mb-2 pr-4" style={{ color: 'var(--text-primary)' }}>
                                  {task.name}
                                </p>

                                {/* Task Info Footer */}
                                <div className="flex items-center justify-between text-xs mt-2 pt-2 border-t" style={{ borderColor: 'var(--border-subtle)' }}>
                                  <span className="font-mono text-[11px] truncate max-w-[120px]" style={{ color: 'var(--text-muted)' }}>
                                    {task.component || 'General'}
                                  </span>
                                  <div className="flex items-center gap-2">
                                    <span className="font-mono text-[11px]" style={{ color: 'var(--text-secondary)' }}>
                                      {task.estimated_hours || 4}h
                                    </span>
                                    {task.phase && (
                                      <span className="text-[10px] px-2 py-0.5 rounded-full font-mono bg-indigo-500/15 text-indigo-500 font-semibold border border-indigo-500/30">
                                        {task.phase.split(' ')[0]}
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>
                            )}
                          </Draggable>
                        );
                      })}
                      {provided.placeholder}

                      {colTasks.length === 0 && (
                        <div className="flex flex-col items-center justify-center h-32 text-xs" style={{ color: 'var(--text-muted)' }}>
                          <span>No tasks in this column</span>
                        </div>
                      )}
                    </div>
                  )}
                </Droppable>
              </div>
            );
          })}
        </div>
      </DragDropContext>

      {/* Add Task Modal */}
      <AnimatePresence>
        {isAddModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-md p-6 rounded-2xl border shadow-2xl"
              style={{
                backgroundColor: 'var(--bg-surface)',
                borderColor: 'var(--border-subtle)',
              }}
            >
              <div className="flex items-center justify-between mb-4 pb-2 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
                <h4 className="font-bold text-base" style={{ color: 'var(--text-primary)' }}>➕ Add Custom Task</h4>
                <button onClick={() => setIsAddModalOpen(false)} className="text-sm cursor-pointer" style={{ color: 'var(--text-muted)' }}>✕</button>
              </div>

              <form onSubmit={handleAddTask} className="space-y-4 text-xs">
                <div>
                  <label className="block mb-1 font-semibold" style={{ color: 'var(--text-secondary)' }}>Task Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g., Set up Redis cache cluster"
                    value={newTaskName}
                    onChange={(e) => setNewTaskName(e.target.value)}
                    className="w-full p-3 rounded-xl border outline-none focus:border-[var(--accent-color)]"
                    style={{
                      backgroundColor: 'var(--bg-base)',
                      borderColor: 'var(--border-subtle)',
                      color: 'var(--text-primary)',
                    }}
                  />
                </div>

                <div>
                  <label className="block mb-1 font-semibold" style={{ color: 'var(--text-secondary)' }}>Component Name</label>
                  <input
                    type="text"
                    placeholder="e.g., Cache Service"
                    value={newTaskComponent}
                    onChange={(e) => setNewTaskComponent(e.target.value)}
                    className="w-full p-3 rounded-xl border outline-none focus:border-[var(--accent-color)]"
                    style={{
                      backgroundColor: 'var(--bg-base)',
                      borderColor: 'var(--border-subtle)',
                      color: 'var(--text-primary)',
                    }}
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block mb-1 font-semibold" style={{ color: 'var(--text-secondary)' }}>Phase</label>
                    <select
                      value={newTaskPhase}
                      onChange={(e) => setNewTaskPhase(e.target.value)}
                      className="w-full p-3 rounded-xl border outline-none focus:border-[var(--accent-color)]"
                      style={{
                        backgroundColor: 'var(--bg-base)',
                        borderColor: 'var(--border-subtle)',
                        color: 'var(--text-primary)',
                      }}
                    >
                      {PHASES.map((p) => (
                        <option key={p} value={p}>{p}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block mb-1 font-semibold" style={{ color: 'var(--text-secondary)' }}>Estimated Hours</label>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      step="0.5"
                      value={newTaskHours}
                      onChange={(e) => setNewTaskHours(e.target.value)}
                      className="w-full p-3 rounded-xl border outline-none focus:border-[var(--accent-color)]"
                      style={{
                        backgroundColor: 'var(--bg-base)',
                        borderColor: 'var(--border-subtle)',
                        color: 'var(--text-primary)',
                      }}
                    />
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-3 border-t" style={{ borderColor: 'var(--border-subtle)' }}>
                  <button
                    type="button"
                    onClick={() => setIsAddModalOpen(false)}
                    className="px-4 py-2.5 rounded-xl border font-semibold cursor-pointer"
                    style={{
                      backgroundColor: 'var(--bg-base)',
                      borderColor: 'var(--border-subtle)',
                      color: 'var(--text-secondary)',
                    }}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-4 py-2.5 rounded-xl font-bold gradient-bg text-white shadow-md hover:brightness-110 cursor-pointer"
                  >
                    {isSubmitting ? 'Saving...' : 'Add Task'}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

