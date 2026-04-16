/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-primary': '#0a0a0a',
        'bg-secondary': '#121212',
        'bg-tertiary': '#1e1e1e',
        'bg-elevated': '#2a2a2a',
        'accent': '#1DB954',
        'accent-yellow': '#FACC15',
        'purple-accent': '#8b5cf6',
        'blue-accent': '#3b82f6',
        'danger': '#ef4444',
      },
      fontFamily: {
        'sans': ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      backdropBlur: {
        'glass': '20px',
        'glass-strong': '40px',
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'fade-in': 'fadeIn 0.2s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(29, 185, 84, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(29, 185, 84, 0.5)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: 0 },
          '100%': { transform: 'scale(1)', opacity: 1 },
        },
      },
    },
  },
  plugins: [],
}