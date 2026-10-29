import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const STAGES = [
  'Reading your idea...',
  'Extracting requirements...',
  'Finding similar projects...',
  'Mapping dependencies...',
  'Generating architecture...',
  'Creating task breakdown...',
  'Finalizing plan...',
];

export default function LoadingAnimation() {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setStageIndex((prev) => (prev + 1) % STAGES.length);
    }, 1500);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center py-20 px-4">
      {/* Concentric 3-Ring Spinner (128px diameter) */}
      <div className="relative w-32 h-32 flex items-center justify-center mb-8">
        {/* Outer Ring: 3s rotation */}
        <div
          className="absolute inset-0 rounded-full border-4 animate-[spin_3s_linear_infinite]"
          style={{
            borderColor: 'var(--border-subtle)',
            borderTopColor: 'var(--accent-color)',
          }}
        />

        {/* Middle Ring: 2s reverse rotation */}
        <div
          className="absolute inset-3 rounded-full border-4 border-transparent animate-[spin_2s_linear_infinite_reverse]"
          style={{
            borderTopColor: 'var(--accent-color)',
            borderRightColor: 'var(--accent-color)',
            opacity: 0.7,
          }}
        />

        {/* Inner Ring: 1.5s rotation */}
        <div
          className="absolute inset-6 rounded-full border-4 border-transparent animate-[spin_1.5s_linear_infinite]"
          style={{
            borderTopColor: 'var(--accent-color)',
          }}
        />

        {/* Center Glow Dot */}
        <div
          className="w-4 h-4 rounded-full animate-pulse shadow-lg"
          style={{
            backgroundColor: 'var(--accent-color)',
            boxShadow: 'var(--glow)',
          }}
        />
      </div>

      {/* Stage Name with Crossfade Animation */}
      <div className="h-8 flex items-center justify-center">
        <AnimatePresence mode="wait">
          <motion.h3
            key={STAGES[stageIndex]}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="text-xl font-bold text-center"
            style={{ color: 'var(--text-primary)' }}
          >
            {STAGES[stageIndex]}
          </motion.h3>
        </AnimatePresence>
      </div>

      {/* Subtext */}
      <p className="mt-3 text-sm font-medium text-center" style={{ color: 'var(--text-muted)' }}>
        This usually takes 10–30 seconds
      </p>
    </div>
  );
}

