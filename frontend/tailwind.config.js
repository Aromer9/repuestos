/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta Subaru — nombres simples sin guiones problemáticos
        subaru: {
          blue:  '#003087',
          mid:   '#0055A5',
          light: '#009FDA',
          pale:  '#E8F2FB',
        },
      },
      boxShadow: {
        card:       '0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.06)',
        'card-hover': '0 4px 6px rgba(0,0,0,0.05), 0 12px 30px rgba(0,48,135,0.10)',
        btn:        '0 2px 8px rgba(0,85,165,0.25)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
