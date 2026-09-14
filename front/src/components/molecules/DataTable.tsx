import type { ReactNode } from "react";

export interface Column<T> {
  key: string;
  header: string;
  width: string;
  align?: "left" | "right" | "center";
  render: (row: T) => ReactNode;
}

export function DataTable<T>({
  columns, rows, rowKey, onRowClick, isHighlighted, footer,
}: {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string;
  onRowClick?: (row: T) => void;
  isHighlighted?: (row: T) => boolean;
  footer?: ReactNode;
}) {
  const template = columns.map((c) => c.width).join(" ");
  const align = (a?: string) =>
    a === "right" ? "text-right" : a === "center" ? "text-center" : "";

  return (
    <div className="bg-raised border border-edge rounded-sm overflow-hidden flex flex-col min-h-0">
      <div
        className="grid px-4 py-2.5 bg-surface border-b border-edge font-mono text-[10px] tracking-[.14em] text-dim"
        style={{ gridTemplateColumns: template }}
      >
        {columns.map((c) => (
          <span key={c.key} className={align(c.align)}>
            {c.header}
          </span>
        ))}
      </div>

      <div className="overflow-auto min-h-0">
        {rows.length === 0 && (
          <div className="px-4 py-8 text-center text-[13px] text-dim">
            No rows match this filter.
          </div>
        )}
        {rows.map((row) => (
          <div
            key={rowKey(row)}
            onClick={() => onRowClick?.(row)}
            className={`grid px-4 py-3 border-b border-edge last:border-b-0 items-center font-mono text-xs text-body2 ${
              onRowClick ? "cursor-pointer hover:bg-edge/40" : ""
            } ${isHighlighted?.(row) ? "bg-spark/[0.06] shadow-[inset_2px_0_0_#e25a1c] text-bright" : ""}`}
            style={{ gridTemplateColumns: template }}
          >
            {columns.map((c) => (
              <span key={c.key} className={`${align(c.align)} truncate`}>
                {c.render(row)}
              </span>
            ))}
          </div>
        ))}
      </div>

      {footer && <div className="px-4 py-2.5 border-t border-edge text-xs text-dim">{footer}</div>}
    </div>
  );
}
