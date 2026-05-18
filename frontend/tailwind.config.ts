import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#09111F",
        panel: "#101A2D",
        panelSoft: "#13213A",
        line: "#25314A",
        accent: "#79E2A0",
        accentWarm: "#F4C96D",
        text: "#EAF2FF",
        muted: "#9BA8C7"
      },
      boxShadow: {
        glow: "0 20px 80px rgba(121, 226, 160, 0.12)"
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "sans-serif"]
      }
    },
  },
  plugins: [],
} satisfies Config;

