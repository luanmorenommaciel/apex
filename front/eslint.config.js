import eslint from "@eslint/js";
import jsxA11y from "eslint-plugin-jsx-a11y";
import reactHooks from "eslint-plugin-react-hooks";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: ["dist"],
  },
  {
    ...eslint.configs.recommended,
    files: ["**/*.{js,mjs,cjs}"],
  },
  ...tseslint.configs.recommended.map((config) => ({
    ...config,
    files: ["src/**/*.{ts,tsx}"],
  })),
  {
    files: ["src/**/*.{ts,tsx}"],
    plugins: {
      "react-hooks": reactHooks,
    },
    rules: {
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
    },
  },
  // Accessibility, at ERROR level: the lint gate runs with --max-warnings 0,
  // so a warning would already fail it, and an error says what it is. The
  // plugin's recommended set covers what static analysis can see - names on
  // controls, roles, alt text, key handlers beside click handlers. What it
  // cannot see (a status conveyed by colour alone) is pinned by
  // src/screens/a11y.test.tsx.
  {
    ...jsxA11y.flatConfigs.recommended,
    files: ["src/**/*.tsx"],
  },
);
