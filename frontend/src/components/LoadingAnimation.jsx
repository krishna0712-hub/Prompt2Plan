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
        {/* Outer Ring: 3s rotation, Primary 30% opacity */}
        <div className="absolute inset-0 rounded-full border-4 border-[#7C5CFF]/30 border-t-[#7C5CFF] animate-[spin_3s_linear_infinite]" />

        {/* Middle Ring: 2s reverse rotation, Primary solid top */}
        <div className="absolute inset-3 rounded-full border-4 border-transparent border-t-[#7C5CFF] border-r-[#7C5CFF]/50 animate-[spin_2s_linear_infinite_reverse]" />

        {/* Inner Ring: 1.5s rotation, Primary Light solid top */}
        <div className="absolute inset-6 rounded-full border-4 border-transparent border-t-[#9B7BFF] animate-[spin_1.5s_linear_infinite]" />

        {/* Center Glow Dot */}
        <div className="w-4 h-4 rounded-full bg-[#7C5CFF] shadow-[0_0_15px_#7C5CFF] animate-pulse" />
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
            className="text-xl font-bold text-white text-center"
          >
            {STAGES[stageIndex]}
          </motion.h3>
        </AnimatePresence>
      </div>

      {/* Subtext */}
      <p className="mt-3 text-sm font-medium text-[#6B6B7B] text-center">
        This usually takes 10–30 seconds
      </p>
    </div>
  );
}
