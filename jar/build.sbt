// ─────────────────────────────────────────────────────────────────────────────
// Apex — the "jar" stage: a self-contained Scala Spark plugin that captures
// per-stage TaskMetrics + a normalized LOGICAL plan fingerprint and ships each
// completed stage as one OTLP span through a BOUNDED BatchSpanProcessor.
//
// Cross-build via sbt-projectmatrix (4 cells). A single crossScalaVersions can't
// vary the Spark dependency per Scala version, but Spark 4.0 dropped Scala 2.12
// and requires Java 17 — so each (Spark, Scala) pair needs its own row:
//   apex_3.5_2.12  · apex_3.5_2.13  · apex_4.0_2.13  · apex_4.1_2.13
// ─────────────────────────────────────────────────────────────────────────────

import sbt.VirtualAxis
import sbtassembly.AssemblyPlugin.autoImport._
import sbtassembly.MergeStrategy

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
val Spark41 = SparkAxis("_41", "spark41")

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

// ── JDK gate for the Spark 4.x cells ──────────────────────────────────────────
// Spark 4 dropped Java 11 (its jars are class-file v61). sbt's FORKED test JVM
// inherits sbt's OWN JVM — Test/javaHome is unset and $JAVA_HOME does NOT
// override it — so on a JDK 11 sbt the 4.x cells used to abort with a 40-line
// UnsupportedClassVersionError, and a lane that only ran the 3.5 cells reported
// green while half the published matrix was never verified. Fail fast with ONE
// readable line instead.
val spark4JdkGate = taskKey[Unit]("Fail fast if sbt's JVM is older than the Spark 4.x minimum")

lazy val sbtJdkMajor: Int = {
  val v = sys.props("java.specification.version")
  val core = if (v.startsWith("1.")) v.drop(2) else v
  core.takeWhile(_.isDigit).toInt
}

def jdkGateSettings(minJdk: Int): Seq[Setting[_]] = Seq(
  spark4JdkGate := {
    if (sbtJdkMajor < minJdk)
      sys.error(
        s"this cell (Spark 4.x) requires JDK $minJdk+, but sbt is running on Java $sbtJdkMajor " +
        "and its forked test JVM inherits that (JAVA_HOME does not override it). " +
        "Run sbt itself on a newer JDK — e.g. `sbt -java-home \"$(../scripts/find-jdk.sh 17)\" test` " +
        "(find-jdk.sh also finds keg-only Homebrew JDKs; override with APEX_JDK_HOME) — " +
        "or export JAVA_HOME to a JDK 17/21 first.")
  },
  Test / test     := (Test / test).dependsOn(spark4JdkGate).value,
  Test / testOnly := (Test / testOnly).dependsOn(spark4JdkGate).evaluated
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
def sparkCell(
  sparkVersion: String,
  jacksonVersion: String,
  jacksonAnnotationsVersion: String,
): Seq[Setting[_]] = Seq(
  libraryDependencies ++= Seq(
    "org.apache.spark"             %% "spark-core"          % sparkVersion   % Provided,
    "org.apache.spark"             %% "spark-sql"           % sparkVersion   % Provided,
    "com.fasterxml.jackson.module" %% "jackson-module-scala" % jacksonVersion % Provided,
    "org.scalatest"                %% "scalatest"           % "3.2.19"       % Test
  ) ++ otelDeps,
  dependencyOverrides ++= Seq(
    "com.fasterxml.jackson.core" % "jackson-core"        % jacksonVersion,
    "com.fasterxml.jackson.core" % "jackson-databind"    % jacksonVersion,
    "com.fasterxml.jackson.core" % "jackson-annotations" % jacksonAnnotationsVersion
  ),
  // Carry the Spark version into the published artifact so a cluster picks the right cell.
  moduleName := s"apex${sparkSuffix.value}",
  Compile / scalacOptions ++= Seq("-deprecation", "-feature", "-unchecked"),
  // Tests spin up a real local SparkSession → fork with the JDK 17 module opens.
  Test / fork := true,
  Test / javaOptions ++= sparkJdk17Opens,
  // Keep Spark/Jackson `Provided` in the PUBLISHED POM, but put them on the TEST
  // classpath (the compile classpath includes provided deps) so tests can run Spark.
  Test / dependencyClasspath := (Test / dependencyClasspath).value ++ (Compile / dependencyClasspath).value,
  // Spark already supplies its Scala runtime. The assembly bundles the OTel SDK and
  // project classes only, preventing a Scala version from being injected into Spark.
  assembly / assemblyOption ~= { _.withIncludeScala(false) },
  assembly / assemblyJarName := s"${moduleName.value}-${version.value}-assembly.jar",
  // Kotlin/Okio ship duplicate module metadata. It is not bytecode used by the
  // plugin, so discard only that metadata and keep strict deduplication elsewhere.
  assembly / assemblyMergeStrategy := {
    case PathList("META-INF", "MANIFEST.MF") => MergeStrategy.discard
    case PathList("META-INF", _ @ "okio.kotlin_module") => MergeStrategy.discard
    case PathList("META-INF", "versions", "9", "module-info.class") => MergeStrategy.discard
    case path => MergeStrategy.deduplicate
  }
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
    _.settings(sparkSuffix := "_3.5").settings(sparkCell("3.5.3", "2.15.2", "2.15.2"))
  )
  // Spark 3.5 · Scala 2.13  (Java 8/11/17) — Jackson 2.15.x
  .customRow(
    scalaVersions = Seq("2.13.14"),
    axisValues    = Seq(Spark35, VirtualAxis.jvm),
    _.settings(sparkSuffix := "_3.5").settings(sparkCell("3.5.3", "2.15.2", "2.15.2"))
  )
  // Spark 4.0 · Scala 2.13  (Java 17/21) — Jackson 2.18.x
  .customRow(
    scalaVersions = Seq("2.13.14"),
    axisValues    = Seq(Spark40, VirtualAxis.jvm),
    _.settings(sparkSuffix := "_4.0").settings(sparkCell("4.0.0", "2.18.2", "2.18.2")).settings(jdkGateSettings(17))
  )
  // Spark 4.1 · Scala 2.13 (Java 17/21) — additive compatibility cell.
  .customRow(
    scalaVersions = Seq("2.13.17"),
    axisValues    = Seq(Spark41, VirtualAxis.jvm),
    _.settings(sparkSuffix := "_4.1").settings(sparkCell("4.1.2", "2.21.2", "2.21")).settings(jdkGateSettings(17))
  )
