import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';

const STAGES = [
  { text: "Reading your idea", icon: "📖" },
  { text: "Extracting requirements", icon: "🔍" },
  { text: "Finding similar projects", icon: "🗂️" },
  { text: "Mapping dependencies", icon: "🔗" },
  { text: "Generating architecture", icon: "🏗️" },
  { text: "Breaking down tasks", icon: "📋" },
  { text: "Estimating effort", icon: "⏱️" },
  { text: "Scheduling milestones", icon: "📅" },
];

export default function LoadingSequence() {
  const [currentStage, setCurrentStage] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStage((prev) => (prev + 1) % STAGES.length);
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className="w-full max-w-lg mx-auto py-16"
    >
      {/* Central spinner area */}
      <div className="flex flex-col items-center gap-8">
        {/* Animated orb */}
        <div className="relative w-20 h-20">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 rounded-full"
            style={{
              border: '2px solid transparent',
              borderTop: '2px solid var(--accent)',
              borderRight: '2px solid var(--accent)',
            }}
          />
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="absolute inset-2 rounded-full"
            style={{
              border: '2px solid transparent',
              borderBottom: '2px solid var(--accent-hover)',
              borderLeft: '2px solid var(--accent-hover)',
            }}
          />
          <div className="absolute inset-0 flex items-center justify-center text-2xl">
            <AnimatePresence mode="wait">
              <motion.span
                key={currentStage}
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.5, opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                {STAGES[currentStage].icon}
              </motion.span>
            </AnimatePresence>
          </div>
        </div>

        {/* Stage text */}
        <div className="text-center">
          <AnimatePresence mode="wait">
            <motion.p
              key={currentStage}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="text-lg font-medium"
              style={{ color: 'var(--text-primary)' }}
            >
              {STAGES[currentStage].text}
              <motion.span
                animate={{ opacity: [1, 0, 1] }}
                transition={{ duration: 1.2, repeat: Infinity }}
              >
                ...
              </motion.span>
            </motion.p>
          </AnimatePresence>

          <p className="text-sm mt-2" style={{ color: 'var(--text-muted)' }}>
            This usually takes 10-30 seconds
          </p>
        </div>

        {/* Progress dots */}
        <div className="flex gap-2">
          {STAGES.map((_, index) => (
            <motion.div
              key={index}
              className="rounded-full"
              animate={{
                width: index === currentStage ? 24 : 8,
                height: 8,
                backgroundColor: index === currentStage
                  ? 'var(--accent)'
                  : index < currentStage
                    ? 'var(--accent-hover)'
                    : 'var(--border-medium)',
              }}
              transition={{ duration: 0.3 }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
}
