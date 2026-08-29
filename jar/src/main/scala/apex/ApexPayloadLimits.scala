package apex

import java.nio.charset.StandardCharsets

/** Final egress bounds for variable-size OTLP attributes. */
private[apex] object ApexPayloadLimits {
  val MaxPlanJsonUtf8Bytes: Int = 64 * 1024
  private val TruncatedMarker = "\n<apex:truncated>"

  def planJson(value: String): String = truncateUtf8(Option(value).getOrElse(""), MaxPlanJsonUtf8Bytes)

  private def truncateUtf8(value: String, maxBytes: Int): String = {
    if (value.getBytes(StandardCharsets.UTF_8).length <= maxBytes) value
    else {
      val markerBytes = TruncatedMarker.getBytes(StandardCharsets.UTF_8).length
      val prefixBudget = math.max(0, maxBytes - markerBytes)
      val prefix = new java.lang.StringBuilder
      var usedBytes = 0
      var offset = 0
      while (offset < value.length) {
        val codePoint = value.codePointAt(offset)
        val encodedBytes =
          if (codePoint <= 0x7f) 1
          else if (codePoint <= 0x7ff) 2
          else if (codePoint <= 0xffff) 3
          else 4
        if (usedBytes + encodedBytes > prefixBudget) {
          offset = value.length
        } else {
          prefix.appendCodePoint(codePoint)
          usedBytes += encodedBytes
          offset += Character.charCount(codePoint)
        }
      }
      prefix.toString + TruncatedMarker
    }
  }
}
