/** @type {import('tailwindcss').Config} */

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    container: {
      center: true,
    },
    extend: {
      colors: {
        base: {
          900: "#0a0a0f",
          800: "#12121a",
          700: "#1a1a25",
          600: "#22222e",
        },
        accent: {
          DEFAULT: "#8b5cf6",
          light: "#a78bfa",
          dark: "#7c3aed",
        },
        glow: {
          blue: "#3b82f6",
          purple: "#8b5cf6",
        },
      },
      backdropBlur: {
        xs: "2px",
      },
      animation: {
        "breathe": "breathe 2s ease-in-out infinite",
        "fade-in": "fade-in 0.3s ease-out",
        "slide-up": "slide-up 0.4s ease-out",
      },
      keyframes: {
        breathe: {
          "0%, 100%": { opacity: "1", boxShadow: "0 0 8px rgba(139, 92, 246, 0.6)" },
          "50%": { opacity: "0.6", boxShadow: "0 0 16px rgba(139, 92, 246, 0.9)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-up": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
