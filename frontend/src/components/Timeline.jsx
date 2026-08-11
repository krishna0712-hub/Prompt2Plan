import { motion } from 'framer-motion';

export default function Timeline({ milestones, tasks }) {
  const milestoneList = milestones || [];
  const taskList = tasks || [];

  // Calculate total days
  const maxEndDay = milestoneList.reduce((max, m) => Math.max(max, m.end_day || 0), 1);
  const totalDays = maxEndDay;
  const totalMonths = (totalDays / 30).toFixed(1);
  const totalPhases = milestoneList.length;
  const totalTaskCount = taskList.length > 0
    ? taskList.length
    : milestoneList.reduce((sum, m) => sum + (m.tasks?.length || 0), 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full bg-[#13131A] border border-[#1E1E28] rounded-2xl p-6 shadow-xl mb-8 space-y-8"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1E1E28]">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <span>📅</span> Milestone Timeline & Schedule
          </h3>
          <p className="text-xs text-[#A0A0B0] mt-0.5">
            Sequential phase scheduling calculated at 6 hours/day per developer
          </p>
        </div>
      </div>

      {/* Stats Dashboard (4 Columns with 2rem bold values) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#0A0A0F] border border-[#1E1E28] text-center">
          <span className="text-xs font-semibold text-[#6B6B7B] uppercase tracking-wider block">
            Total Duration
          </span>
          <span className="text-2xl sm:text-[2rem] font-bold text-white mt-1 block leading-none">
            {totalDays} Days
          </span>
        </div>

        <div className="p-4 rounded-xl bg-[#0A0A0F] border border-[#1E1E28] text-center">
          <span className="text-xs font-semibold text-[#6B6B7B] uppercase tracking-wider block">
            Project Phases
          </span>
          <span className="text-2xl sm:text-[2rem] font-bold text-[#7C5CFF] mt-1 block leading-none">
            {totalPhases}
          </span>
        </div>

        <div className="p-4 rounded-xl bg-[#0A0A0F] border border-[#1E1E28] text-center">
          <span className="text-xs font-semibold text-[#6B6B7B] uppercase tracking-wider block">
            Est. Months
          </span>
          <span className="text-2xl sm:text-[2rem] font-bold text-[#00D4FF] mt-1 block leading-none">
            {totalMonths}
          </span>
        </div>

        <div className="p-4 rounded-xl bg-[#0A0A0F] border border-[#1E1E28] text-center">
          <span className="text-xs font-semibold text-[#6B6B7B] uppercase tracking-wider block">
            Total Tasks
          </span>
          <span className="text-2xl sm:text-[2rem] font-bold text-[#10B981] mt-1 block leading-none">
            {totalTaskCount}
          </span>
        </div>
      </div>

      {/* Gantt Chart Section */}
      <div className="space-y-6 pt-2">
        {/* Top Day Scale */}
        <div className="flex justify-between text-xs font-mono text-[#6B6B7B] px-1">
          <span>Day 0</span>
          <span>Day {totalDays}</span>
        </div>

        {/* Phase Gantt Bars */}
        <div className="space-y-5">
          {milestoneList.map((m, index) => {
            const startDay = m.start_day || 0;
            const endDay = m.end_day || totalDays;
            const duration = Math.max(1, endDay - startDay + 1);

            const leftPercent = (startDay / totalDays) * 100;
            const widthPercent = (duration / totalDays) * 100;

            return (
              <div key={m.phase_name || index} className="space-y-1.5">
                {/* Label row */}
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-white">
                    {m.phase_name}
                  </span>
                  <span className="font-mono text-[#A0A0B0]">
                    Day {startDay} → Day {endDay} ({duration} days, {m.total_hours || 0}h)
                  </span>
                </div>

                {/* Track and Bar */}
                <div className="relative w-full h-4 bg-[#1E1E28] rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${widthPercent}%` }}
                    transition={{ duration: 0.8, delay: index * 0.15, ease: 'easeOut' }}
                    style={{ left: `${leftPercent}%` }}
                    className="absolute top-0 bottom-0 rounded-full gradient-bg hover:scale-y-125 transition-transform origin-center cursor-pointer group"
                  >
                    {/* Tooltip */}
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute bottom-6 left-1/2 -translate-x-1/2 px-2.5 py-1 rounded bg-[#0A0A0F] border border-[#7C5CFF] text-[11px] text-white font-mono whitespace-nowrap z-20 pointer-events-none shadow-lg">
                      {m.phase_name}: {duration} days ({m.total_hours || 0}h work)
                    </div>
                  </motion.div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}
