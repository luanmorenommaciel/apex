import { Card, Label, Mono, Prose } from "@/components/atoms";

/**
 * DATA_SOURCE=auto asked every store it knows and none answered.
 *
 * This replaces the app, not a panel inside it: there is no repository to
 * mount the screens on, and the one that used to fill the gap - the recorded
 * gate run - is a recording, which a production visitor would read as their
 * cluster. It is served only when asked for by name.
 */
export function StoreUnreachable({ probed }: { probed: { name: string; path: string }[] }) {
  return (
    <main className="min-h-screen bg-canvas flex items-center justify-center p-8">
      <Card accent="withheld" className="max-w-[640px] px-6 py-5 flex flex-col gap-4">
        <Label tone="withheld">NO STORE ANSWERED</Label>
        <Prose size="base">
          <Mono className="text-body2">DATA_SOURCE=auto</Mono> probed every store this
          console can read from, and none answered. Nothing is shown in their place: the
          recorded gate run is served only when a deployment asks for it by name.
        </Prose>
        <ul className="flex flex-col gap-1.5 font-mono text-xs text-body2" aria-label="What was probed">
          {probed.map((p) => (
            <li key={p.path} className="flex items-center gap-2.5">
              <span className="text-withheld" aria-hidden="true">x</span>
              <span>{p.name}</span>
              <Mono className="text-sub">{p.path}</Mono>
              <span className="text-dim">no answer</span>
            </li>
          ))}
        </ul>
        <Prose size="sm" className="text-dim">
          Start the API (<Mono>APEX_API_UPSTREAM</Mono>) or the store
          (<Mono>CLICKHOUSE_UPSTREAM</Mono>) this deployment names, or pin{" "}
          <Mono>DATA_SOURCE</Mono> to <Mono>http</Mono>, <Mono>clickhouse</Mono> or, for the
          recording, <Mono>fixtures</Mono>. See the README, &ldquo;Configure a deployment&rdquo;.
        </Prose>
      </Card>
    </main>
  );
}
