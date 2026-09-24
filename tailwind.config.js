/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          DEFAULT: '#d4af37',
          dark: '#82641e',
          soft: '#f3df8a',
        },
        dark: {
          bg: '#080a0f',
          surface: '#101522',
          border: '#222c40',
        },
        cyan: {
          DEFAULT: '#38bdf8',
          glow: '#7dd3fc',
        },
        crimson: '#f87171',
        emerald: '#4ade80',
        purple: '#c084fc',
      },
      fontFamily: {
        serif: ['Georgia', 'Cambria', 'serif'],
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
      boxShadow: {
        'gold-glow': '0 0 25px rgba(212, 175, 55, 0.25)',
        'cyan-glow': '0 0 20px rgba(56, 189, 248, 0.35)',
        'purple-glow': '0 0 20px rgba(192, 132, 252, 0.35)',
      },
    },
  },
  plugins: [],
}
