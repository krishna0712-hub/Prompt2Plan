import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    darkMode: true,
    background: '#13131A',
    primaryColor: '#7C5CFF',
    primaryTextColor: '#FFFFFF',
    primaryBorderColor: '#1E1E28',
    lineColor: '#6B6B7B',
    secondaryColor: '#10B981',
    tertiaryColor: '#F59E0B',
  },
  securityLevel: 'loose',
});

const TYPE_COLORS = {
  frontend: '#7C5CFF',
  backend: '#10B981',
  database: '#F59E0B',
  integration: '#00D4FF',
  storage: '#6B6B7B',
  cache: '#EC4899',
};

export default function ArchitectureDiagram({ architecture }) {
  const containerRef = useRef(null);
  const [layoutDirection, setLayoutDirection] = useState('TD'); // 'TD' or 'LR'
  const [renderError, setRenderError] = useState(false);
  const [svgContent, setSvgContent] = useState('');

  const buildMermaidString = (arch, direction) => {
    if (!arch || !arch.components || arch.components.length === 0) {
      return '';
    }

    let code = `graph ${direction}\n`;

    // Define nodes
    arch.components.forEach((comp) => {
      const cleanId = comp.id.replace(/[^a-zA-Z0-9_]/g, '_');
      const cleanName = comp.name.replace(/"/g, "'");
      const compType = (comp.type || 'backend').toLowerCase();
      code += `  ${cleanId}["${cleanName}<br/><sub style='font-size:10px;color:#A0A0B0;'>[${compType}]</sub>"]\n`;
    });

    // Define connections
    (arch.connections || []).forEach((conn) => {
      const fromId = conn.from.replace(/[^a-zA-Z0-9_]/g, '_');
      const toId = conn.to.replace(/[^a-zA-Z0-9_]/g, '_');
      const label = (conn.label || '').replace(/"/g, "'");
      if (label) {
        code += `  ${fromId} -->|"${label}"| ${toId}\n`;
      } else {
        code += `  ${fromId} --> ${toId}\n`;
      }
    });

    // Node style definitions according to specs
    arch.components.forEach((comp) => {
      const cleanId = comp.id.replace(/[^a-zA-Z0-9_]/g, '_');
      const type = (comp.type || 'backend').toLowerCase();
      const color = TYPE_COLORS[type] || '#7C5CFF';
      code += `  style ${cleanId} fill:#13131A,stroke:${color},stroke-width:2px,color:#FFFFFF\n`;
    });

    return code;
  };

  useEffect(() => {
    let isMounted = true;
    setRenderError(false);

    if (!architecture || !architecture.components || architecture.components.length === 0) {
      return;
    }

    const renderDiagram = async () => {
      try {
        const mCode = buildMermaidString(architecture, layoutDirection);
        if (!mCode) return;

        const uniqueId = `mermaid-svg-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
        const { svg } = await mermaid.render(uniqueId, mCode);

        if (isMounted) {
          setSvgContent(svg);
        }
      } catch (err) {
        console.error('Mermaid render error:', err);
        if (isMounted) {
          setRenderError(true);
        }
      }
    };

    renderDiagram();

    return () => {
      isMounted = false;
    };
  }, [architecture, layoutDirection]);

  if (!architecture || !architecture.components || architecture.components.length === 0) {
    return (
      <div className="w-full bg-[#13131A] border border-[#1E1E28] rounded-2xl p-12 text-center text-[#6B6B7B]">
        <span className="text-3xl block mb-2">🏗️</span>
        <p className="text-sm font-medium">No architecture data available</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full bg-[#13131A] border border-[#1E1E28] rounded-2xl p-6 shadow-xl mb-8"
    >
      {/* Header & Control Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-[#1E1E28]">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <span>🏗️</span> System Architecture
          </h3>
          <p className="text-xs text-[#A0A0B0] mt-0.5">
            Auto-generated interactive component relationship diagram
          </p>
        </div>

        {/* Layout & Control Buttons */}
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => setLayoutDirection('TD')}
            className={`text-xs px-3 py-1.5 rounded-lg font-mono font-medium transition-all ${
              layoutDirection === 'TD'
                ? 'bg-[#7C5CFF] text-white'
                : 'bg-[#1E1E28] text-[#A0A0B0] hover:text-white'
            }`}
          >
            Top-Down (TD)
          </button>
          <button
            onClick={() => setLayoutDirection('LR')}
            className={`text-xs px-3 py-1.5 rounded-lg font-mono font-medium transition-all ${
              layoutDirection === 'LR'
                ? 'bg-[#7C5CFF] text-white'
                : 'bg-[#1E1E28] text-[#A0A0B0] hover:text-white'
            }`}
          >
            Left-Right (LR)
          </button>
        </div>
      </div>

      {/* Color Legend */}
      <div className="flex flex-wrap items-center gap-4 mb-6 px-4 py-2.5 rounded-xl bg-[#0A0A0F] border border-[#1E1E28]">
        <span className="text-xs font-semibold text-[#6B6B7B] uppercase tracking-wider">Legend:</span>
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-xs text-[#A0A0B0] capitalize font-mono">{type}</span>
          </div>
        ))}
      </div>

      {/* Render Area */}
      {renderError ? (
        <div className="p-8 text-center text-red-400 bg-red-500/10 rounded-xl border border-red-500/30 text-sm">
          ⚠️ Failed to render architecture diagram. Check component schema.
        </div>
      ) : (
        <div
          ref={containerRef}
          className="w-full overflow-x-auto p-4 flex justify-center items-center min-h-[300px]"
          dangerouslySetInnerHTML={{ __html: svgContent }}
        />
      )}
    </motion.div>
  );
}
