/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary colors
        primary: {
          dark: '#1A2D42',    // Dark blue
          medium: '#2E4156',   // Medium blue
        },
        // Neutral colors
        neutral: {
          light: '#AAB7B7',    // Light gray
          medium: '#C0C8CA',   // Medium gray
          lighter: '#D4D8DD',  // Lighter gray
        },
        // Theme-specific colors
        light: {
          bg: '#FFFFFF',       // White background
          bgAlt: '#D4D8DD',    // Light gray background
          text: '#1A2D42',     // Dark blue text
          secondary: {
            primary: '#2E4156', // Medium blue
            secondary: '#AAB7B7', // Light gray
          },
        },
        dark: {
          bg: '#1A2D42',       // Dark blue background
          bgAlt: '#2E4156',    // Medium blue background
          text: '#D4D8DD',     // Light gray text
          secondary: {
            primary: '#C0C8CA', // Medium gray
            secondary: '#AAB7B7', // Light gray
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}