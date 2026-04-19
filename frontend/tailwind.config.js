/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        'pure-black': '#000000',
        'near-black': '#262626',
        'darkest': '#090909',
        'pure-white': '#ffffff',
        'snow': '#fafafa',
        'light-gray': '#e5e5e5',
        'stone': '#737373',
        'mid-gray': '#525252',
        'silver': '#a3a3a3',
        'button-text-dark': '#404040',
        'border-light': '#d4d4d4',
      },
      borderRadius: {
        'container': '12px',
        'pill': '9999px',
      },
      fontFamily: {
        'display': ['SF Pro Rounded', 'system-ui', '-apple-system', 'system-ui'],
        'body': ['ui-sans-serif', 'system-ui', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji'],
        'mono': ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New'],
      }
    },
  },
  plugins: [],
}
