ThisBuild / scalaVersion := "2.13.17"
libraryDependencies += "org.apache.spark" %% "spark-catalyst" % "4.0.1"
Compile / run / fork := true
Compile / run / javaOptions ++= Seq("-Xmx1g", "--add-opens=java.base/java.nio=ALL-UNNAMED", "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED")
