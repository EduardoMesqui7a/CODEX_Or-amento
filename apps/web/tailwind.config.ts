import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0e1218",
        cyanGlow: "#6be8ff",
        coral: "#ff8a66",
        mist: "#ecf7ff"
      },
      boxShadow: {
        premium: "0 18px 60px rgba(14, 18, 24, 0.18)"
      }
    }
  },
  plugins: []
};

export default config;

