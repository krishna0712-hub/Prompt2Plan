import { motion } from 'framer-motion';

export default function Timeline({ milestones, tasks }) {
  const milestoneList = milestones || [];
  const taskList = tasks || [];

  // Calculate total duration ranges across all phases
  const totalDays = milestoneList.reduce((max, m) => Math.max(max, m.end_day || 0), 1);
  const totalMonths = (totalDays / 30).toFixed(1);
  const totalPhases = milestoneList.length;
  const totalTaskCount = taskList.length > 0
    ? taskList.length
    : milestoneList.reduce((sum, m) => sum + (m.tasks?.length || 0), 0);

  const totalLikelyHours = milestoneList.reduce((sum, m) => sum + (m.total_hours || 0), 0);
  const totalOptHours = milestoneList.reduce((sum, m) => sum + (m.optimistic_hours || m.total_hours * 0.75 || 0), 0);
  const totalPessHours = milestoneList.reduce((sum, m) => sum + (m.pessimistic_hours || m.total_hours * 1.35 || 0), 0);

  const totalOptDays = Math.max(1, Math.round(totalOptHours / 6));
  const totalPessDays = Math.max(totalDays, Math.round(totalPessHours / 6));

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full border rounded-2xl p-6 shadow-xl mb-8 space-y-8"
      style={{
        backgroundColor: 'var(--bg-surface)',
        borderColor: 'var(--border-subtle)',
      }}
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
        <div>
          <h3 className="text-lg font-bold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <span>📅</span> Milestone Timeline & Schedule Range
          </h3>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
            Sequential phase scheduling calculated from historical PROMISE empirical dataset (6 hours/dev-day)
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/15 border border-indigo-500/40 text-xs text-indigo-500 font-mono font-semibold">
          <span>🧠 Learned AI Estimator Active</span>
        </div>
      </div>

      {/* Stats Dashboard */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl border text-center shadow-sm" style={{ backgroundColor: 'var(--bg-base)', borderColor: 'var(--border-subtle)' }}>
          <span className="text-xs font-semibold uppercase tracking-wider block" style={{ color: 'var(--text-muted)' }}>
            Likely Duration
          </span>
          <span className="text-2xl sm:text-[2rem] font-bold mt-1 block leading-none" style={{ color: 'var(--text-primary)' }}>
            {totalDays} Days
          </span>
          <span className="text-[11px] font-mono mt-1 block" style={{ color: 'var(--text-secondary)' }}>
            Range: {totalOptDays}d – {totalPessDays}d
          </span>
        </div>

        <div className="p-4 rounded-xl border text-center shadow-sm" style={{ backgroundColor: 'var(--bg-base)', borderColor: 'var(--border-subtle)' }}>
          <span className="text-xs font-semibold uppercase tracking-wider block" style={{ color: 'var(--text-muted)' }}>
            Project Phases
          </span>
          <span className="text-2xl sm:text-[2rem] font-bold text-indigo-500 mt-1 block leading-none">
            {totalPhases}
          </span>
          <span className="text-[11px] font-mono mt-1 block" style={{ color: 'var(--text-secondary)' }}>
            4 Phased Milestones
          </span>
        </div>

        <div className="p-4 rounded-xl border text-center shadow-sm" style={{ backgroundColor: 'var(--bg-base)', borderColor: 'var(--border-subtle)' }}>
          <span className="text-xs font-semibold uppercase tracking-wider block" style={{ color: 'var(--text-muted)' }}>
            Total Effort (Hours)
          </span>
          <span className="text-2xl sm:text-[2rem] font-bold text-sky-500 mt-1 block leading-none">
            {totalLikelyHours.toFixed(1)}h
          </span>
          <span className="text-[11px] font-mono mt-1 block" style={{ color: 'var(--text-secondary)' }}>
            {totalOptHours.toFixed(1)}h – {totalPessHours.toFixed(1)}h
          </span>
        </div>

        <div className="p-4 rounded-xl border text-center shadow-sm" style={{ backgroundColor: 'var(--bg-base)', borderColor: 'var(--border-subtle)' }}>
          <span className="text-xs font-semibold uppercase tracking-wider block" style={{ color: 'var(--text-muted)' }}>
            Total Tasks
          </span>
          <span className="text-2xl sm:text-[2rem] font-bold text-emerald-500 mt-1 block leading-none">
            {totalTaskCount}
          </span>
          <span className="text-[11px] font-mono mt-1 block" style={{ color: 'var(--text-secondary)' }}>
            Est. {totalMonths} Months
          </span>
        </div>
      </div>

      {/* Gantt Chart Section */}
      <div className="space-y-6 pt-2">
        {/* Top Day Scale */}
        <div className="flex justify-between text-xs font-mono px-1" style={{ color: 'var(--text-muted)' }}>
          <span>Day 0</span>
          <span>Day {totalDays} (Pessimistic: ~Day {totalPessDays})</span>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-6 text-xs px-1" style={{ color: 'var(--text-secondary)' }}>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-indigo-500/30 border border-indigo-500" />
            <span>Pessimistic Spread</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full gradient-bg shadow-sm" />
            <span>Most Likely Duration</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-0.5 h-3 bg-sky-500 rounded-full" />
            <span>Optimistic Marker</span>
          </div>
        </div>

        {/* Phase Gantt Range Bars */}
        <div className="space-y-6">
          {milestoneList.map((m, index) => {
            const startDay = m.start_day || 1;
            const endDay = m.end_day || totalDays;

            const likelyDuration = m.total_days || Math.max(1, endDay - startDay + 1);
            const optDuration = m.optimistic_days || Math.max(1, Math.round(likelyDuration * 0.75));
            const pessDuration = m.pessimistic_days || Math.max(likelyDuration, Math.round(likelyDuration * 1.35));

            const totalScaleDays = Math.max(totalDays, totalPessDays);

            const leftPercent = ((startDay - 1) / totalScaleDays) * 100;
            const likelyWidthPercent = (likelyDuration / totalScaleDays) * 100;
            const pessWidthPercent = (pessDuration / totalScaleDays) * 100;
            const optWidthPercent = (optDuration / totalScaleDays) * 100;

            const likelyHours = m.total_hours || 0;
            const optHours = m.optimistic_hours || round(likelyHours * 0.75, 1);
            const pessHours = m.pessimistic_hours || round(likelyHours * 1.35, 1);

            return (
              <div key={m.phase_name || index} className="space-y-2">
                {/* Label row */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs">
                  <span className="font-semibold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
                    <span>{m.phase_name}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded border text-indigo-500 font-semibold" style={{ backgroundColor: 'var(--bg-base)', borderColor: 'var(--border-subtle)' }}>
                      Range: {optDuration}d – {pessDuration}d
                    </span>
                  </span>
                  <span className="font-mono text-[11px]" style={{ color: 'var(--text-secondary)' }}>
                    Day {startDay} → Day {endDay} ({likelyDuration}d, {likelyHours}h likely [{optHours}h–{pessHours}h])
                  </span>
                </div>

                {/* Range Track and Dual Bars */}
                <div className="relative w-full h-5 border rounded-full overflow-visible p-0.5 shadow-inner" style={{ backgroundColor: 'var(--bg-base)', borderColor: 'var(--border-subtle)' }}>
                  {/* Lighter Outer Range Bar (Optimistic to Pessimistic Spread) */}
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${pessWidthPercent}%` }}
                    transition={{ duration: 0.8, delay: index * 0.1, ease: 'easeOut' }}
                    style={{ left: `${leftPercent}%` }}
                    className="absolute top-0 bottom-0 rounded-full bg-indigo-500/20 border border-indigo-500/40 backdrop-blur-sm"
                  />

                  {/* Prominent Likely Duration Bar */}
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${likelyWidthPercent}%` }}
                    transition={{ duration: 0.8, delay: index * 0.15, ease: 'easeOut' }}
                    style={{ left: `${leftPercent}%` }}
                    className="absolute top-0 bottom-0 rounded-full gradient-bg hover:brightness-110 transition-all cursor-pointer group shadow-sm"
                  >
                    {/* Hover Tooltip */}
                    <div
                      className="opacity-0 group-hover:opacity-100 transition-opacity absolute bottom-7 left-1/2 -translate-x-1/2 px-3 py-1.5 rounded-xl border text-[11px] font-mono whitespace-nowrap z-30 pointer-events-none shadow-2xl space-y-0.5"
                      style={{
                        backgroundColor: 'var(--bg-surface)',
                        borderColor: 'var(--border-subtle)',
                        color: 'var(--text-primary)',
                      }}
                    >
                      <div className="font-bold text-indigo-500">{m.phase_name} Duration Range</div>
                      <div>⚡ Most Likely: {likelyDuration} days ({likelyHours}h)</div>
                      <div className="text-sky-500">🟢 Optimistic: {optDuration} days ({optHours}h)</div>
                      <div className="text-amber-500">🔴 Pessimistic: {pessDuration} days ({pessHours}h)</div>
                    </div>
                  </motion.div>

                  {/* Optimistic Marker Line */}
                  <div
                    style={{ left: `${leftPercent + optWidthPercent}%` }}
                    className="absolute top-0 bottom-0 w-0.5 bg-sky-500 shadow-[0_0_6px_#38bdf8] z-10 pointer-events-none"
                    title={`Optimistic target: ${optDuration} days`}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}

function round(val, dec) {
  return Number(Math.round(val + 'e' + dec) + 'e-' + dec);
}

