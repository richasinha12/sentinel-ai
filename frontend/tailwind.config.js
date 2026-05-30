/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        sentinel: { 900: '#0a0f1e', 800: '#0f172a', 700: '#1e293b', accent: '#6366f1' },
      },
    },
  },
  plugins: [],
}
