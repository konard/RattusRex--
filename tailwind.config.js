/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ember: "#d5a449",
        ink: "#0f1115",
        panel: "#181b22",
      },
    },
  },
  plugins: [],
};
