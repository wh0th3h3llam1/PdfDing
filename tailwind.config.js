/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'selector',
  content: ["**/pdfding/**/templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        primary: "var(--color-primary)",
        secondary: "var(--color-secondary)",
        tertiary1: "var(--color-tertiary1)",
        tertiary2: "var(--color-tertiary2)",
      },
    },
  },
  plugins: [],
}
