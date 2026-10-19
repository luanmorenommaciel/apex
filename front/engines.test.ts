import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import semver from "semver";
import { describe, expect, it } from "vitest";

/**
 * One Node major, everywhere it is named: package.json engines, .nvmrc, both
 * Dockerfile stages and CI. The image built on 20, CI tested on 22 and the
 * host ran 25 while jsdom refused two of the three; each environment found
 * out on its own. Every range below is READ from its owner, never restated.
 */
const here = (rel: string) => fileURLToPath(new URL(rel, import.meta.url));
const read = (rel: string) => readFileSync(here(rel), "utf8");

const pkg = JSON.parse(read("./package.json")) as {
  engines?: { node?: string };
  devDependencies: Record<string, string>;
};
const engines = pkg.engines?.node ?? "";

describe("Node engines", () => {
  it("declares a range", () => {
    expect(semver.validRange(engines), "package.json engines.node").not.toBeNull();
  });

  it("is accepted by every devDependency that declares its own engines", () => {
    // The lower bound of each comparator set in OUR range must satisfy THEIR
    // range: a range of majors they refuse is not a range we can promise.
    const lowerBounds = new semver.Range(engines).set.map((set) => set[0].semver.version);
    expect(lowerBounds.length).toBeGreaterThan(0);
    for (const name of Object.keys(pkg.devDependencies)) {
      const theirs = (JSON.parse(read(`./node_modules/${name}/package.json`)) as { engines?: { node?: string } })
        .engines?.node;
      if (!theirs) continue;
      for (const bound of lowerBounds) {
        expect(semver.satisfies(bound, theirs), `${name} (${theirs}) refuses ${bound}`).toBe(true);
      }
    }
  });

  it("excludes Node 20, which jsdom refuses", () => {
    expect(semver.satisfies("20.19.0", engines)).toBe(false);
  });

  it("names one major in .nvmrc, both Dockerfile stages and CI", () => {
    const nvmrc = read("./.nvmrc").trim();
    const docker = [...read("./Dockerfile").matchAll(/^FROM node:(\d+)-alpine AS (dev|build)$/gm)].map((m) => m[1]);
    const ci = /node-version:\s*"(\d+)"/.exec(read("../.github/workflows/ci.yml"))?.[1];
    expect(docker, "dev and build stages").toHaveLength(2);
    expect(new Set([nvmrc, ...docker, ci])).toEqual(new Set([nvmrc]));
    expect(semver.satisfies(`${nvmrc}.99.0`, engines), `${nvmrc}.x inside engines`).toBe(true);
  });
});
