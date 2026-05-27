/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ember: "#d39b43",
        iron: "#1b1d24",
        parchment: "#e8dec8"
      }
    }
  },
  plugins: []
};
