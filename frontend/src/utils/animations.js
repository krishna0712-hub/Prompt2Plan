export const heroVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.6, ease: 'easeOut' },
  },
};

export const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.05,
    },
  },
};

export const slideUpVariant = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: 'easeOut' },
  },
};

export const cardHoverVariant = {
  rest: { y: 0, borderColor: '#1E1E28', boxShadow: 'none' },
  hover: {
    y: -2,
    borderColor: '#7C5CFF',
    boxShadow: '0 4px 20px rgba(124, 92, 255, 0.25)',
    transition: { duration: 0.2, ease: 'easeOut' },
  },
};

export const buttonMotion = {
  whileHover: { scale: 1.02, boxShadow: '0 0 20px rgba(124, 92, 255, 0.4)' },
  whileTap: { scale: 0.95 },
};

export const taskCardStagger = {
  hidden: { opacity: 0, y: 15 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.05, duration: 0.3, ease: 'easeOut' },
  }),
};
