/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0c3d6b', // Warna biru khas KPPN
        secondary: '#1e5fa3'
      }
    },
  },
  plugins: [],
}