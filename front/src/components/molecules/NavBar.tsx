import { NavLink } from "react-router-dom";
import { useRepository } from "@/data/useRepository";
import { CONTRACT_VERSION } from "@/contract/types";

const TABS = [
  { to: "/runs", label: "Runs" },
  { to: "/ask", label: "Ask" },
  { to: "/compare", label: "Compare" },
  { to: "/memory", label: "Memory" },
  { to: "/verify", label: "Verify" },
];

export function NavBar() {
  const repo = useRepository();
  return (
    <header className="flex items-center justify-between h-12 px-4 bg-surface border-b border-edge shrink-0">
      <div className="flex items-center gap-6">
        <img src="/apex-lockup.png" alt="APEX" className="h-[30px] w-auto object-contain" />
        <nav className="flex items-center gap-0.5 font-mono text-xs">
          {TABS.map((t) => (
            <NavLink
              key={t.to}
              to={t.to}
              className={({ isActive }) =>
                `px-[11px] py-[14px] transition-colors ${
                  isActive
                    ? "text-bright shadow-[inset_0_-2px_0_#e25a1c]"
                    : "text-sub hover:text-body2"
                }`
              }
            >
              {t.label}
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="flex items-center gap-2.5 font-mono text-[11px] text-sub">
        <span>
          {repo.kind === "clickhouse" ? (
            <>clickhouse <span className="text-certified">●</span> apex</>
          ) : (
            <>source <span className="text-withheld">◐</span> fixtures</>
          )}
        </span>
        <span className="text-dim">|</span>
        <span>
          contract <span className="text-body2">v{CONTRACT_VERSION}</span>
        </span>
        <span className="px-2 py-1 border border-edge rounded-sm text-body">read-only</span>
      </div>
    </header>
  );
}
