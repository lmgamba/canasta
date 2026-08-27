// Approximate, client-side tracking of Gemini free-tier usage for
// gemini-3.6-flash. This is an advisory heuristic based on this browser's
// own record of scan attempts — not real-time enforcement of Google's
// actual quota (which resets daily at midnight Pacific, not on a rolling
// window). See spec/features/007-receipt-upload-ui/plan.md for rationale.

// Confirmed free-tier limits for gemini-3.6-flash — one-line change if the
// tier or model changes.
export const GEMINI_FREE_TIER_RPM = 5
export const GEMINI_FREE_TIER_RPD = 20

const STORAGE_KEY = 'canasta-scan-timestamps'
const MINUTE_MS = 60_000
const DAY_MS = 24 * 60 * 60 * 1000

function readTimestamps(): number[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed.filter((n) => typeof n === 'number') : []
  } catch {
    return []
  }
}

function writeTimestamps(timestamps: number[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(timestamps))
  } catch {
    // localStorage unavailable (private browsing, quota) — the warning
    // silently becomes a no-op rather than breaking the upload flow.
  }
}

// Record that a scan request is about to be sent to Gemini. Call this right
// before each actual API call — not on file selection, which never reaches
// Gemini if the user cancels or the client-side type check rejects it.
export function recordScanAttempt(): void {
  const now = Date.now()
  const recent = readTimestamps().filter((t) => now - t < DAY_MS)
  recent.push(now)
  writeTimestamps(recent)
}

// Returns a warning message if recent scan attempts are one away from
// either free-tier limit (5 RPM or 20 RPD), or null if there's nothing to
// warn about. The per-minute check takes priority when both apply, since
// it's the more actionable one ("wait a moment" vs. "wait until tomorrow").
export function getRateLimitWarning(): string | null {
  const now = Date.now()
  const timestamps = readTimestamps().filter((t) => now - t < DAY_MS)

  const lastMinute = timestamps.filter((t) => now - t < MINUTE_MS).length
  if (lastMinute >= GEMINI_FREE_TIER_RPM - 1) {
    return `You've scanned ${lastMinute} receipts in the last minute — the free Gemini tier allows ${GEMINI_FREE_TIER_RPM} requests per minute. Wait a moment before scanning another.`
  }

  const lastDay = timestamps.length
  if (lastDay >= GEMINI_FREE_TIER_RPD - 1) {
    return `You've scanned ${lastDay} receipts today — the free Gemini tier allows ${GEMINI_FREE_TIER_RPD} requests per day. This may be your last successful scan today.`
  }

  return null
}
