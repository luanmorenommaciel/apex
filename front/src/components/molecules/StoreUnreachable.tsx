import { Card, Label, Mono, Prose } from "@/components/atoms";

/**
 * The Apex API gave no HTTP answer at boot.
 *
 * This replaces the app, not a panel inside it: there is no repository to
 * mount the screens on, and the recorded gate run is not a substitute - a
 * production visitor would read it as their cluster. It is served only when
 * asked for by name (DATA_SOURCE=fixtures).
 */
export function StoreUnreachable({ probed }: { probed: { name: string; path: string }[] }) {
  return (
    <main className="min-h-screen bg-canvas flex items-center justify-center p-8">
      <Card accent="withheld" className="max-w-[640px] px-6 py-5 flex flex-col gap-4">
        <Label tone="withheld">NO STORE ANSWERED</Label>
        <Prose size="base">
          The console asked the Apex API at boot and got no answer. Nothing is shown in
          its place: the recorded gate run is served only when a deployment asks for it by
          name.
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
          Start the API this deployment names (<Mono>APEX_API_UPSTREAM</Mono>, or{" "}
          <Mono>APEX_API_URL</Mono> for a cross-origin call), or set{" "}
          <Mono>DATA_SOURCE=fixtures</Mono> for the recording. See the README,
          &ldquo;Configure a deployment&rdquo;.
        </Prose>
      </Card>
    </main>
  );
}
