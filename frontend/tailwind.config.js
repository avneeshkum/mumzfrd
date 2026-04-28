// tailwind.config.js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Mom-focused Premium Palette
        'mom-cream': '#FAF9F8',
        'mom-pink': {
          50: '#FFF5F6',
          100: '#FEDDE1',
          200: '#FECCD3',
          300: '#FCA5B0',
          DEFAULT: '#F472B6', // Main accent
          500: '#E84E8F',
          600: '#C1356F',
        },
        'mom-slate': {
          700: '#475569',
          900: '#1E293B',
        },
      },
      fontFamily: {
        // Yahan unique fonts define karo. generic fonts mat use karo.
        // Example: 'Playfair Display' for serif, 'Outfit' for sans.
        // Google Fonts se import karne ke baad yahan map karo.
        serif: ['"Playfair Display"', 'serif'], 
        sans: ['"Outfit"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}