/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-primary': '#fff5f7',
        'bg-secondary': '#ffeef2',
        'bg-tertiary': '#ffe4ec',
        'bg-elevated': '#ffd0dd',
        'accent': '#ff9ebb',
        'accent-light': '#ffb7c5',
        'accent-dark': '#ff7ba3',
        'accent-yellow': '#ffd700',
        'purple-accent': '#b19cd9',
        'blue-accent': '#87ceeb',
        'mint-accent': '#98fb98',
        'danger': '#ff6b8a',
      },
      fontFamily: {
        'sans': ['Nunito', 'Mochiy Pop P One', 'Yomogi', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        'display': ['Mochiy Pop P One', 'Nunito', 'sans-serif'],
        'cute': ['Yomogi', 'Nunito', 'cursive'],
      },
      backdropBlur: {
        'glass': '20px',
        'glass-strong': '40px',
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'slide-up': 'slideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'slide-down': 'slideDown 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'fade-in': 'fadeIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'scale-in': 'scaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'bouncy': 'bouncy 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'sakura-fall': 'sakura-fall var(--duration, 10s) linear infinite',
        'float-up': 'floatUp 1s ease-out forwards',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(255, 158, 187, 0.4)' },
          '50%': { boxShadow: '0 0 30px 8px rgba(255, 158, 187, 0.6)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(15px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        slideDown: {
          '0%': { transform: 'translateY(-15px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: 0 },
          '100%': { transform: 'scale(1)', opacity: 1 },
        },
        bouncy: {
          '0%, 100%': { transform: 'scale(1)' },
          '25%': { transform: 'scale(1.08)' },
          '50%': { transform: 'scale(0.95)' },
          '75%': { transform: 'scale(1.03)' },
        },
      },
    },
  },
  plugins: [],
}
