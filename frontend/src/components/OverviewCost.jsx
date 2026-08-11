import { motion } from 'motion/react';

export default function OverviewCost({ result }) {
  if (!result) return null;

  const cost = result.cost_estimate || {
    starter_tier_monthly: 35,
    growth_tier_monthly: 140,
    scale_tier_monthly: 450,
    breakdown: [],
  };

  const risk = result.risk_analysis || {
    complexity_score: 6.5,
    complexity_level: 'Moderate',
    estimated_total_hours: 120,
    risks: [],
  };

  const getComplexityColor = (level) => {
    switch (level) {
      case 'Low': return '#34D399';
      case 'Moderate': return '#60A5FA';
      case 'High': return '#FBBF24';
      case 'Very High': return '#F87171';
      default: return '#7C5CFF';
    }
  };

  const complexityColor = getComplexityColor(risk.complexity_level);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8 w-full"
    >
      {/* Metric Cards Grid — Spacious Padding & Modern Badges */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 w-full">
        <div className="card p-6 flex flex-col justify-between" style={{ background: 'var(--bg-surface)' }}>
          <div className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--text-muted)' }}>
            Complexity Rating
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold tracking-tight" style={{ color: complexityColor }}>
              {risk.complexity_score} <span className="text-sm font-normal text-gray-400">/ 10</span>
            </span>
            <span
              className="text-xs px-3 py-1 rounded-full font-semibold"
              style={{
                background: `${complexityColor}20`,
                color: complexityColor,
                border: `1px solid ${complexityColor}40`,
              }}
            >
              {risk.complexity_level}
            </span>
          </div>
        </div>

        <div className="card p-6 flex flex-col justify-between" style={{ background: 'var(--bg-surface)' }}>
          <div className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--text-muted)' }}>
            Estimated Total Effort
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold tracking-tight" style={{ color: 'var(--text-primary)' }}>
              {risk.estimated_total_hours || result.tasks?.reduce((a, b) => a + (b.estimated_hours || 0), 0)}
              <span className="text-sm font-normal text-gray-400"> hrs</span>
            </span>
            <span className="text-xs text-gray-400 font-mono">
              ~{Math.ceil((risk.estimated_total_hours || 120) / 6)} days
            </span>
          </div>
        </div>

        <div className="card p-6 flex flex-col justify-between" style={{ background: 'var(--bg-surface)' }}>
          <div className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--text-muted)' }}>
            Starter Monthly Infrastructure
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold tracking-tight text-emerald-400">
              ${cost.starter_tier_monthly} <span className="text-xs font-normal text-gray-400">/ mo</span>
            </span>
            <span className="text-xs text-gray-400 font-mono">Minimum</span>
          </div>
        </div>

        <div className="card p-6 flex flex-col justify-between" style={{ background: 'var(--bg-surface)' }}>
          <div className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--text-muted)' }}>
            Growth Monthly Infrastructure
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-extrabold tracking-tight text-blue-400">
              ${cost.growth_tier_monthly} <span className="text-xs font-normal text-gray-400">/ mo</span>
            </span>
            <span className="text-xs text-gray-400 font-mono">Production</span>
          </div>
        </div>
      </div>

      {/* Cloud Infrastructure Cost Breakdown */}
      <div className="card p-6 md:p-8 w-full">
        <div className="flex items-center justify-between mb-6 flex-wrap gap-2">
          <h4 className="text-lg font-bold flex items-center gap-2.5" style={{ color: 'var(--text-primary)' }}>
            <span>☁️</span> Estimated Monthly Cloud Infrastructure & Service Costs
          </h4>
          <span className="text-xs px-3 py-1 rounded-full font-mono bg-purple-950/60 text-purple-300 border border-purple-800">
            Automated Cost Model
          </span>
        </div>

        {cost.breakdown?.length > 0 ? (
          <div className="overflow-x-auto w-full">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="border-b" style={{ borderColor: 'var(--border-subtle)', color: 'var(--text-muted)' }}>
                  <th className="py-3.5 px-4 font-semibold">Component</th>
                  <th className="py-3.5 px-4 font-semibold">Type</th>
                  <th className="py-3.5 px-4 font-semibold">Starter Tier</th>
                  <th className="py-3.5 px-4 font-semibold">Growth Tier</th>
                  <th className="py-3.5 px-4 font-semibold">Scale Tier</th>
                  <th className="py-3.5 px-4 font-semibold">Infrastructure Detail</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-subtle)]">
                {cost.breakdown.map((item, idx) => (
                  <tr key={idx} className="hover:bg-[var(--bg-elevated)] transition-colors">
                    <td className="py-4 px-4 font-semibold" style={{ color: 'var(--text-primary)' }}>
                      {item.component}
                    </td>
                    <td className="py-4 px-4">
                      <span className="px-2.5 py-1 rounded text-xs font-mono bg-gray-800/80 text-gray-300 border border-gray-700">
                        {item.type}
                      </span>
                    </td>
                    <td className="py-4 px-4 font-mono font-semibold text-emerald-400">${item.starter_monthly_usd}</td>
                    <td className="py-4 px-4 font-mono font-semibold text-blue-400">${item.growth_monthly_usd}</td>
                    <td className="py-4 px-4 font-mono font-semibold text-purple-400">${item.scale_monthly_usd}</td>
                    <td className="py-4 px-4 text-gray-400 text-xs">{item.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-gray-400 py-4">Standard cloud infrastructure allocation (~$30/mo base hosting & database).</p>
        )}
      </div>

      {/* Technical Risk Assessment Table */}
      {risk.risks?.length > 0 && (
        <div className="card p-6 md:p-8 w-full">
          <h4 className="text-lg font-bold mb-6 flex items-center gap-2.5" style={{ color: 'var(--text-primary)' }}>
            <span>⚠️</span> Technical Risk Assessment & Mitigation Strategies
          </h4>

          <div className="space-y-4 w-full">
            {risk.risks.map((r, i) => (
              <div
                key={i}
                className="p-5 rounded-xl border transition-colors space-y-3"
                style={{
                  background: 'var(--bg-surface)',
                  borderColor: 'var(--border-subtle)',
                }}
              >
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <span className="font-bold text-xs uppercase tracking-wider text-purple-400">
                    {r.category}
                  </span>
                  <span
                    className="text-xs uppercase font-extrabold px-3 py-1 rounded-full"
                    style={{
                      background: r.impact === 'High' ? 'rgba(248, 113, 113, 0.2)' : 'rgba(96, 165, 250, 0.2)',
                      color: r.impact === 'High' ? '#F87171' : '#60A5FA',
                      border: `1px solid ${r.impact === 'High' ? 'rgba(248, 113, 113, 0.4)' : 'rgba(96, 165, 250, 0.4)'}`,
                    }}
                  >
                    {r.impact} Impact
                  </span>
                </div>
                <div className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {r.risk}
                </div>
                <div className="text-xs text-gray-300 bg-[var(--bg-elevated)] p-4 rounded-lg border border-gray-800 leading-relaxed">
                  <span className="font-bold text-emerald-400">Recommended Mitigation: </span>
                  {r.mitigation}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
