import type { ReactNode } from "react";
import { NavBar } from "@/components/molecules";

export function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-canvas">
      <NavBar />
      <main className="flex-1 min-h-0 flex flex-col">{children}</main>
    </div>
  );
}

export function Page({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`flex-1 min-h-0 px-7 py-6 flex flex-col gap-5 ${className}`}>{children}</div>
  );
}
