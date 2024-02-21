/** @type {import('tailwindcss').Config} */
module.exports = {
  // TODO: prefix later if collision
  // prefix: "djw-tw-",
  content: ["./django_web_repl/**/*.{html,js}"],
  theme: {
    extend: {},
  },
  plugins: [
    require("@tailwindcss/typography"),
    require("@tailwindcss/aspect-ratio"),
    require("daisyui"),
  ],

  daisyui: {
    darkTheme: false,
  },
};
