import type { ReactNode } from "react";

export type CardAccent = "none" | "finding" | "withheld" | "certified" | "spark" | "memory" | "edge";

const accents: Record<CardAccent, string> = {
  none: "border-edge",
  edge: "border-edge border-l-2 border-l-edge2",
  finding: "border-edge2 border-l-2 border-l-finding",
  withheld: "border-edge2 border-l-2 border-l-withheld",
  certified: "border-edge2 border-l-2 border-l-certified",
  spark: "border-edge2 border-l-2 border-l-spark",
  memory: "border-edge2 border-l-2 border-l-memory",
};

export function Card({
  children, accent = "none", className = "", onClick,
}: {
  children: ReactNode;
  accent?: CardAccent;
  className?: string;
  onClick?: () => void;
}) {
  const interactive = onClick
    ? "cursor-pointer transition-colors hover:bg-edge/40"
    : "";
  return (
    <div
      onClick={onClick}
      className={`bg-raised border rounded-sm ${accents[accent]} ${interactive} ${className}`}
    >
      {children}
    </div>
  );
}
