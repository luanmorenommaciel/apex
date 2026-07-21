// Cross-build the plugin across (Spark, Scala) cells that a single crossScalaVersions
// cannot express: Spark 4.0 dropped Scala 2.12, so the Spark dependency must vary per row.
// sbt-projectmatrix (as Delta Lake uses) gives one row per (sparkVersion, scalaVersion) cell.
addSbtPlugin("com.eed3si9n" % "sbt-projectmatrix" % "0.10.0")
