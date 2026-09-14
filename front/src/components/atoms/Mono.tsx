import type { ReactNode } from "react";

/**
 * Every measurement, identifier, plan fragment and config key.
 * Never wraps prose — that is what the sans face is for.
 */
export function Mono({
  children, className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <span className={`font-mono ${className}`}>{children}</span>;
}
