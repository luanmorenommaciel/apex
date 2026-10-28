import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { RepositoryProvider } from "./data/useRepository";
// The three typefaces tailwind.config.js names, bundled rather than fetched
// from Google Fonts: an air-gapped deployment keeps its type, no visitor's
// browser contacts a third party, and the CSP can stay on its own origin.
// Latin subset only, and only the weights the design tokens use.
import "@fontsource/jetbrains-mono/latin-400.css";
import "@fontsource/jetbrains-mono/latin-500.css";
import "@fontsource/jetbrains-mono/latin-600.css";
import "@fontsource/jetbrains-mono/latin-700.css";
import "@fontsource/ibm-plex-sans/latin-400.css";
import "@fontsource/ibm-plex-sans/latin-500.css";
import "@fontsource/ibm-plex-sans/latin-600.css";
import "@fontsource/archivo-black/latin-400.css";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RepositoryProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </RepositoryProvider>
  </React.StrictMode>,
);
