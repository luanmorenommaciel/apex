import type { ReactNode } from "react";

/** Reasoning text. Sans, never mono — and never used for a number. */
export function Prose({
  children, size = "sm", className = "",
}: {
  children: ReactNode;
  size?: "xs" | "sm" | "base";
  className?: string;
}) {
  const s = { xs: "text-xs", sm: "text-[13px]", base: "text-sm" }[size];
  return <div className={`${s} leading-relaxed text-body ${className}`}>{children}</div>;
}
