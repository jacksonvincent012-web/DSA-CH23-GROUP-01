/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#0a0e1a',
        'dark-card': '#111827',
        'dark-border': '#1f2937',
        'text': '#f1f5f9',
        'muted': '#94a3b8',
        'dim': '#64748b',
        'gain': '#00c896',
        'loss': '#ff4d6a',
        'accent': '#fbbf24',
        'primary': '#3b82f6',
        'purple': '#8b5cf6',
        'cyan': '#06b6d4',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['SF Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
