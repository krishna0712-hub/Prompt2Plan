/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#7C5CFF', light: '#9B7BFF', dark: '#5C3CEF' },
        background: { DEFAULT: '#0A0A0F', card: '#13131A', hover: '#1A1A24' },
        border: { DEFAULT: '#1E1E28' },
        text: { primary: '#FFFFFF', secondary: '#A0A0B0', muted: '#6B6B7B' },
        success: { DEFAULT: '#10B981' },
        amber: { DEFAULT: '#F59E0B' },
        cyan: { DEFAULT: '#00D4FF' },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'monospace'],
      },
      animation: {
        'pulse-ring': 'pulse-ring 2s ease-in-out infinite',
        'slide-up': 'slide-up 0.5s ease-out forwards',
      },
      keyframes: {
        'pulse-ring': {
          '0%, 100%': { transform: 'scale(0.95)', opacity: '0.7' },
          '50%': { transform: 'scale(1.05)', opacity: '1' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
