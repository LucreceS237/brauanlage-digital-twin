/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Industrial dark dashboard palette.
        panel: "#11161d",
        panel2: "#1a212b",
        edge: "#2a323d",
        accent: "#39d0d8",
        brew: "#f0a500",
      },
    },
  },
  plugins: [],
};
