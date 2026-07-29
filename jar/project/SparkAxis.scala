import sbt.VirtualAxis

/**
 * A weak projectmatrix axis distinguishing the two Spark generations.
 *
 * Needed because Scala 2.13 appears in BOTH the Spark 3.5 and 4.0 rows —
 * projectmatrix must tell those rows apart. `idSuffix` lands in the artifact id
 * (→ apex_3.5_2.13 / apex_4.0_2.13); `directorySuffix` keeps their target/ trees
 * separate. Lives here (not in build.sbt) because .sbt files cannot define a
 * class that top-level vals then reference.
 */
final case class SparkAxis(idSuffix: String, directorySuffix: String) extends VirtualAxis.WeakAxis
