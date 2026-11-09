import { describe, it, expect } from 'vitest'
import { normalizeServerUrl, friendlyConnectionError } from '../serverUrl'

describe('normalizeServerUrl', () => {
  it('trims spaces and trailing slashes', () => {
    expect(normalizeServerUrl('  http://127.0.0.1:8009/// ')).toBe('http://127.0.0.1:8009')
  })

  it('leaves a clean URL alone', () => {
    expect(normalizeServerUrl('http://127.0.0.1:8009')).toBe('http://127.0.0.1:8009')
  })
})

describe('friendlyConnectionError', () => {
  it('never shows a raw Failed to fetch to the player', () => {
    const msg = friendlyConnectionError(new TypeError('Failed to fetch'), 'fallback')
    expect(msg).not.toContain('Failed to fetch')
    expect(msg).toContain('Could not reach the game server')
    expect(msg).toContain('local network')
  })

  it('passes through server status errors', () => {
    expect(friendlyConnectionError(new Error('Request failed with status 500'), 'x')).toBe(
      'Request failed with status 500',
    )
  })

  it('uses the fallback for unknown shapes', () => {
    expect(friendlyConnectionError('odd', 'plain fallback')).toBe('plain fallback')
  })
})
