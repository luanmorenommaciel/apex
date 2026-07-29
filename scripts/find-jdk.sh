#!/usr/bin/env bash
# Print the path of a JDK suitable for building Apex's jar lane, or exit 1.
#
#   scripts/find-jdk.sh [min-major]     # default min-major = 17
#
# WHY THIS EXISTS
# build.sbt publishes four (Spark, Scala) cells. apex_40 and apex_41 need JDK 17+
# because Spark 4 dropped Java 11. sbt's forked test JVM inherits sbt's OWN JVM —
# `Test / javaHome` defaults to None and $JAVA_HOME does NOT override it — so on a
# JDK 11 sbt those two cells abort with UnsupportedClassVersionError. They were
# silently unverified for the entire build, because only the Spark 3.5 cells ran
# and the suite still reported green.
#
# The fix is `sbt -java-home <path>`, which needs a path. Hardcoding one into a
# committed file is not portable, and requiring a global machine change (PATH
# edits, sudo-symlinking into /Library/Java) is worse. So: discover it.
#
# Two traps this script exists to avoid, both of which actually bit this project:
#
#   1. A Homebrew `openjdk@17` is KEG-ONLY — not linked onto PATH and invisible to
#      /usr/libexec/java_home. A perfectly good JDK 17 sat installed and
#      undiscoverable while two published cells went unverified.
#   2. `/usr/libexec/java_home -v 21` is a MINIMUM-version matcher, not an exact
#      one: with only a JDK 24 installed it happily returns 24. Selecting on what
#      was requested rather than on what was returned silently hands Spark an
#      unsupported JDK. So every candidate is probed for its ACTUAL major version.

set -euo pipefail

REQUIRED="${1:-17}"

# Preference order, deliberately NOT "newest first". Spark 4.x supports Java 17
# and 21 and does not claim support for 22+. Handing Spark a Java 24 buys
# reflection and module-access failures that look exactly like Apex bugs.
PREFERRED=(21 17)
FALLBACK=(24 23 22 20 19 18)

# Major version of the JDK rooted at $1, or empty if it isn't a usable JDK.
major_of() {
    local home="$1"
    [[ -n "$home" && -x "$home/bin/java" ]] || return 0
    "$home/bin/java" -version 2>&1 | sed -nE '1s/.*version "([0-9]+).*/\1/p'
}

# --- gather every candidate JDK home on this machine -----------------------
candidates=()
add() { [[ -n "${1:-}" && -d "${1:-}" ]] && candidates+=("$1") || true; }

add "${APEX_JDK_HOME:-}"
add "${JAVA_HOME:-}"

if [[ -x /usr/libexec/java_home ]]; then
    # -V lists every installed JVM; parse the paths directly rather than trusting
    # -v's minimum-match semantics.
    while IFS= read -r line; do
        add "$line"
    done < <(/usr/libexec/java_home -V 2>&1 | sed -nE 's|.* (/.*/Contents/Home)$|\1|p')
fi

if command -v brew >/dev/null 2>&1; then
    for v in "${PREFERRED[@]}" "${FALLBACK[@]}"; do
        prefix="$(brew --prefix "openjdk@${v}" 2>/dev/null || true)"
        [[ -n "$prefix" ]] || continue
        add "$prefix/libexec/openjdk.jdk/Contents/Home"
        add "$prefix"
    done
    prefix="$(brew --prefix openjdk 2>/dev/null || true)"
    if [[ -n "$prefix" ]]; then
        add "$prefix/libexec/openjdk.jdk/Contents/Home"
        add "$prefix"
    fi
fi

for home in /usr/lib/jvm/*; do add "$home"; done

# --- select by ACTUAL major version, in preference order -------------------
# APEX_JDK_HOME is an explicit operator override and bypasses preference entirely
# (but is still checked against the minimum, so a bad override fails loudly).
if [[ -n "${APEX_JDK_HOME:-}" ]]; then
    m="$(major_of "$APEX_JDK_HOME")"
    if [[ -n "$m" ]] && (( m >= REQUIRED )); then
        echo "$APEX_JDK_HOME"
        exit 0
    fi
    echo "APEX_JDK_HOME=$APEX_JDK_HOME is not a JDK >= $REQUIRED" >&2
    exit 1
fi

for want in "${PREFERRED[@]}" "${FALLBACK[@]}"; do
    (( want >= REQUIRED )) || continue
    for home in "${candidates[@]}"; do
        [[ "$(major_of "$home")" == "$want" ]] || continue
        echo "$home"
        exit 0
    done
done

cat >&2 <<EOF
No JDK >= ${REQUIRED} found.

Apex needs JDK 17+ to build the Spark 4.x cross-build cells (apex_40, apex_41).
The Spark 3.5 cells run on Java 11, which is why this can go unnoticed.

    macOS:  brew install openjdk@21
    Debian: apt-get install -y openjdk-21-jdk

A Homebrew openjdk is keg-only, so it will NOT appear on PATH or in
/usr/libexec/java_home — this script finds it anyway. To force a specific JDK:

    export APEX_JDK_HOME=/path/to/jdk
EOF
exit 1
