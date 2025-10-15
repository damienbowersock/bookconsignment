/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './**/*.py'
  ],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#0D9488', 700: '#0F766E' },
        accent: '#F97316',
        background: '#F8FAFC',
        surface: '#FFFFFF',
        text: '#0B1220',
        muted: '#CBD5E1',
        success: '#16A34A',
        warn: '#D97706',
        error: '#E11D48',
      },
      container: { center: true, padding: '1rem' }
    },
  },
  plugins: [],
}
