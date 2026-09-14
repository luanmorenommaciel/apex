/** A unified-diff line. Config diffs are the only "fix" Apex ever emits. */
export function DiffLine({ text }: { text: string }) {
  const tone = text.startsWith("+")
    ? "text-certified bg-certified/10"
    : text.startsWith("-")
      ? "text-finding bg-finding/10"
      : text.startsWith("@@")
        ? "text-info"
        : "text-muted";
  return <div className={`font-mono text-[11.5px] leading-[1.75] px-2 -mx-2 ${tone}`}>{text}</div>;
}

export function Diff({ text }: { text: string }) {
  return (
    <div className="bg-surface border border-edge rounded-sm p-3">
      {text.split("\n").map((line, i) => (
        <DiffLine key={i} text={line} />
      ))}
    </div>
  );
}
