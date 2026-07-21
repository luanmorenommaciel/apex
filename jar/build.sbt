// ─────────────────────────────────────────────────────────────────────────────
// Apex — the "jar" stage: a self-contained Scala Spark plugin that captures
// per-stage TaskMetrics + a normalized LOGICAL plan fingerprint and ships each
// completed stage as one OTLP span through a BOUNDED BatchSpanProcessor.
//
// Cross-build via sbt-projectmatrix (3 cells). A single crossScalaVersions can't
// vary the Spark dependency per Scala version, but Spark 4.0 dropped Scala 2.12
// and requires Java 17 — so each (Spark, Scala) pair needs its own row:
//   apex_3.5_2.12  · apex_3.5_2.13  · apex_4.0_2.13
// ─────────────────────────────────────────────────────────────────────────────

import sbt.VirtualAxis

// The implicit build-root project shares this baseDirectory and would otherwise
// compile src/main/scala WITHOUT any cell's Spark/OTel classpath (failing on the
// OTel imports). Neutralize it — all real compilation happens in the matrix rows.
Compile / sources := Nil
Test / sources    := Nil
publish / skip    := true

ThisBuild / organization := "io.dataship"
ThisBuild / version      := "0.1.0"
ThisBuild / licenses     := Seq("Apache-2.0" -> url("https://www.apache.org/licenses/LICENSE-2.0"))
ThisBuild / homepage     := Some(url("https://github.com/dataship/apex"))
ThisBuild / description  := "Apex Spark plugin: per-stage metrics + logical-plan fingerprint over OTLP."

// SparkAxis is defined in project/SparkAxis.scala (a .sbt file cannot define a
// class that top-level vals reference). idSuffix must be a valid sbt project-ID
// token — no dots — so the dotted "_3.5" published name lives in `moduleName`
// (set per-cell below), while the axis carries an ID-safe token.
val Spark35 = SparkAxis("_35", "spark35")
val Spark40 = SparkAxis("_40", "spark40")

// Spark on JDK 17 requires these module opens or it throws InaccessibleObjectException
// (Tungsten/unsafe, Kryo, network). Applied to forked test JVMs only.
val sparkJdk17Opens = Seq(
  "--add-opens=java.base/java.lang=ALL-UNNAMED",
  "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED",
  "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED",
  "--add-opens=java.base/java.io=ALL-UNNAMED",
  "--add-opens=java.base/java.net=ALL-UNNAMED",
  "--add-opens=java.base/java.nio=ALL-UNNAMED",
  "--add-opens=java.base/java.util=ALL-UNNAMED",
  "--add-opens=java.base/java.util.concurrent=ALL-UNNAMED",
  "--add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED",
  "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED",
  "--add-opens=java.base/sun.nio.cs=ALL-UNNAMED",
  "--add-opens=java.base/sun.security.action=ALL-UNNAMED",
  "--add-opens=java.base/sun.util.calendar=ALL-UNNAMED",
  "--add-opens=java.base/jdk.internal.ref=ALL-UNNAMED"
)

// OTel Java SDK — pin every component to one version (BOM-equivalent) so the
// exporter, sdk, and api never skew. These are BUNDLED (Spark does not ship them).
val otelVersion = "1.43.0"
val otelDeps = Seq(
  "io.opentelemetry" % "opentelemetry-api"          % otelVersion,
  "io.opentelemetry" % "opentelemetry-sdk"          % otelVersion,
  "io.opentelemetry" % "opentelemetry-exporter-otlp" % otelVersion
)

// Spark + Jackson are Provided (the host cluster supplies them). Jackson is pinned
// and overridden to the version Spark ships — bundling a mismatched Jackson causes
// NoSuchMethodError deep inside Spark (sparkMeasure marks jackson-module-scala Provided).
def sparkCell(sparkVersion: String, jacksonVersion: String): Seq[Setting[_]] = Seq(
  libraryDependencies ++= Seq(
    // "provided,test": provided in the published POM (the cluster supplies Spark),
    // but also on the forked test classpath so the fingerprint test can run Spark.
    "org.apache.spark"             %% "spark-core"          % sparkVersion   % "provided,test",
    "org.apache.spark"             %% "spark-sql"           % sparkVersion   % "provided,test",
    "com.fasterxml.jackson.module" %% "jackson-module-scala" % jacksonVersion % "provided,test",
    "org.scalatest"                %% "scalatest"           % "3.2.19"       % Test
  ) ++ otelDeps,
  dependencyOverrides ++= Seq(
    "com.fasterxml.jackson.core" % "jackson-core"        % jacksonVersion,
    "com.fasterxml.jackson.core" % "jackson-databind"    % jacksonVersion,
    "com.fasterxml.jackson.core" % "jackson-annotations" % jacksonVersion
  ),
  // Carry the Spark version into the published artifact so a cluster picks the right cell.
  moduleName := s"apex${sparkSuffix.value}",
  Compile / scalacOptions ++= Seq("-deprecation", "-feature", "-unchecked"),
  // Tests spin up a real local SparkSession → fork with the JDK 17 module opens.
  Test / fork := true,
  Test / javaOptions ++= sparkJdk17Opens
)

// Derived per-row from the SparkAxis in scope (used to suffix the module name).
val sparkSuffix = settingKey[String]("Spark-generation suffix for the module name")

lazy val apex = (projectMatrix in file("."))
  .settings(
    name := "apex",
    Test / fork := true
  )
  // Spark 3.5 · Scala 2.12  (Java 8/11/17) — Jackson 2.15.x
  .customRow(
    scalaVersions = Seq("2.12.18"),
    axisValues    = Seq(Spark35, VirtualAxis.jvm),
    _.settings(sparkSuffix := "_3.5").settings(sparkCell("3.5.3", "2.15.2"))
  )
  // Spark 3.5 · Scala 2.13  (Java 8/11/17) — Jackson 2.15.x
  .customRow(
    scalaVersions = Seq("2.13.14"),
    axisValues    = Seq(Spark35, VirtualAxis.jvm),
    _.settings(sparkSuffix := "_3.5").settings(sparkCell("3.5.3", "2.15.2"))
  )
  // Spark 4.0 · Scala 2.13  (Java 17/21) — Jackson 2.18.x
  .customRow(
    scalaVersions = Seq("2.13.14"),
    axisValues    = Seq(Spark40, VirtualAxis.jvm),
    _.settings(sparkSuffix := "_4.0").settings(sparkCell("4.0.0", "2.18.2"))
  )
