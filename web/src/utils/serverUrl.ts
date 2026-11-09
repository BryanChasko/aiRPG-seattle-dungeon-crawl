// The one address this page talks to: the player's own game server,
// the job code-named the Narrator, built across the workshop floors.
export const LOCAL_NARRATOR_URL = 'http://127.0.0.1:8009'

/** Drop trailing slashes so `${base}/inquire` never becomes `//inquire`. */
export function normalizeServerUrl(raw: string): string {
  return raw.trim().replace(/\/+$/, '')
}

/**
 * Turn a raw fetch failure into the Floor 6 recovery words.
 * A TypeError from fetch means the request never landed: the server is
 * not running, the address is wrong, or the browser blocked local access.
 */
export function friendlyConnectionError(e: unknown, fallback: string): string {
  if (e instanceof Error) {
    if (e.name === 'TimeoutError' || e.name === 'AbortError') {
      return 'The server took too long to answer. Check the four terminals below, then try again.'
    }
    if (e instanceof TypeError || /failed to fetch|networkerror|load failed/i.test(e.message)) {
      return 'Could not reach the game server. It may not be running yet, the Server URL may have a typo, or Chrome or Edge may be waiting for local network permission (allow it, or open the site settings icon left of the address bar, allow local network access, then reload).'
    }
    return e.message
  }
  return fallback
}
