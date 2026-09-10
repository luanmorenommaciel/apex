import type { ReactNode } from "react";

export function ScreenHeader({
  title, subtitle, right,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  right?: ReactNode;
}) {
  return (
    <div className="flex items-end justify-between gap-6">
      <div className="flex flex-col gap-1.5 min-w-0">
        <h1 className="font-mono text-[22px] font-semibold text-bright m-0">{title}</h1>
        {subtitle && <div className="text-[13px] text-sub">{subtitle}</div>}
      </div>
      {right && <div className="flex gap-2 shrink-0">{right}</div>}
    </div>
  );
}

export function Button({
  children, onClick, variant = "ghost",
}: {
  children: ReactNode;
  onClick?: () => void;
  variant?: "ghost" | "outline" | "primary";
}) {
  const cls = {
    ghost: "bg-raised border-edge text-body hover:text-bright hover:border-edge2",
    outline: "bg-raised border-edge2 text-bright hover:bg-edge",
    primary: "bg-spark border-spark text-surface font-semibold hover:bg-spark-light",
  }[variant];
  return (
    <button
      type="button"
      onClick={onClick}
      className={`font-mono text-xs px-3 py-2 border rounded-sm transition-colors ${cls}`}
    >
      {children}
    </button>
  );
}
