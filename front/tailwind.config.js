/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Surfaces — gruvbox dark, darkest first
        canvas: "#131516",
        surface: "#1d2021",
        raised: "#282828",
        edge: "#3c3836",
        edge2: "#504945",
        muted: "#665c54",
        dim: "#7c6f64",
        sub: "#928374",
        body: "#a89984",
        body2: "#d5c4a1",
        bright: "#ebdbb2",

        // Brand — Spark ecosystem orange
        spark: "#e25a1c",
        "spark-light": "#fc9236",
        "spark-dark": "#a23e12",

        // Semantic. These are NOT decorative; each one is a claim.
        finding: "#fb4934",   // a finding Apex will defend
        withheld: "#fabd2f",  // withheld / unresolved — never "warning"
        certified: "#8ec07c", // certified / passed
        info: "#83a598",
        memory: "#d3869b",
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
        sans: ["'IBM Plex Sans'", "system-ui", "sans-serif"],
        display: ["'Archivo Black'", "system-ui", "sans-serif"],
      },
      letterSpacing: {
        label: "0.16em",
        wordmark: "0.07em",
      },
    },
  },
  plugins: [],
};
