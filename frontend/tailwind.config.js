/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta corporativa (azul marino). Para ajustar al azul exacto de la empresa,
        // basta con cambiar estos valores: toda la UI usa `brand-*`.
        // Tono principal: brand-700 (#1f3a68). Botones: brand-600. Sidebar: brand-900.
        brand: {
          50:  '#f1f5fa',
          100: '#dfe7f3',
          200: '#bfcfe6',
          300: '#8eaad3',
          400: '#5a82bb',
          500: '#35609f',
          600: '#28497f',
          700: '#1f3a68',
          800: '#1a3156',
          900: '#172a49',
          950: '#0f1c31',
        },
        primary: {
          50:  '#f1f5fa',
          100: '#dfe7f3',
          500: '#35609f',
          600: '#28497f',
          700: '#1f3a68',
        },
      }
    },
  },
  plugins: [],
}
