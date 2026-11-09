import { describe, it, expect, vi, afterEach } from 'vitest'
import { useGameApi, parseHype, parseSponsorDeal } from '../useGameApi'

const SERVER_URL = 'http://127.0.0.1:8009'

function mockFetch(response: unknown, ok = true, status = 200) {
  return vi.fn().mockResolvedValue({
    ok,
    status,
    json: () => Promise.resolve(response),
  })
}

const story = {
  response: 'SYSTEM: a sponsor is on line one.',
  actions_suggestions: ['Listen', 'Hang up', 'Sign everything'],
  details: 'interrupt',
  dice_rolls: [],
}

const interrupt = {
  id: 'v1:tool_call:abc:123',
  name: 'sponsor_deal',
  reason: {
    sponsor: 'The Bellevue Consortium',
    offer: 'Wear the logo for one floor.',
    reward: 'a Silver Box',
    cost: 'ten Hype if you refuse later',
  },
}

describe('Floor 6 encounters in useGameApi', () => {
  const originalFetch = globalThis.fetch

  afterEach(() => {
    globalThis.fetch = originalFetch
  })

  describe('fetchHype', () => {
    it('sends GET to /hype and returns the snapshot', async () => {
      const snapshot = {
        hype: 12,
        sponsor_tiers: [10],
        next_sponsor_at: 25,
        last_event: 'achievement +5',
      }
      globalThis.fetch = mockFetch(snapshot)

      const { fetchHype, error } = useGameApi(SERVER_URL)
      const result = await fetchHype()

      expect(globalThis.fetch).toHaveBeenCalledWith(`${SERVER_URL}/hype`, {
        signal: expect.any(AbortSignal),
      })
      expect(result).toEqual(snapshot)
      expect(error.value).toBeNull()
    })

    it('returns null without an error when the Narrator has no /hype route', async () => {
      globalThis.fetch = mockFetch({ detail: 'Not Found' }, false, 404)

      const { fetchHype, error } = useGameApi(SERVER_URL)

      expect(await fetchHype()).toBeNull()
      expect(error.value).toBeNull()
    })

    it('returns null without an error when the request fails', async () => {
      globalThis.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'))

      const { fetchHype, error } = useGameApi(SERVER_URL)

      expect(await fetchHype()).toBeNull()
      expect(error.value).toBeNull()
    })

    it('returns null when the body has no numeric hype', async () => {
      globalThis.fetch = mockFetch({ hype: 'lots' })

      const { fetchHype } = useGameApi(SERVER_URL)

      expect(await fetchHype()).toBeNull()
    })
  })

  describe('parseHype', () => {
    it('fills the optional fields with safe defaults', () => {
      expect(parseHype({ hype: 3 })).toEqual({
        hype: 3,
        sponsor_tiers: [],
        next_sponsor_at: null,
        last_event: '',
      })
    })

    it('rejects values that are not objects', () => {
      expect(parseHype(null)).toBeNull()
      expect(parseHype('hype')).toBeNull()
      expect(parseHype(42)).toBeNull()
    })

    it('keeps only numeric sponsor tiers', () => {
      expect(parseHype({ hype: 1, sponsor_tiers: [10, 'x', 25] })?.sponsor_tiers).toEqual([10, 25])
    })
  })

  describe('parseSponsorDeal', () => {
    it('reads the sponsor, offer, reward and cost from the reason', () => {
      expect(parseSponsorDeal(interrupt)).toEqual({
        id: 'v1:tool_call:abc:123',
        name: 'sponsor_deal',
        sponsor: 'The Bellevue Consortium',
        offer: 'Wear the logo for one floor.',
        reward: 'a Silver Box',
        cost: 'ten Hype if you refuse later',
      })
    })

    it('uses a string reason as the offer', () => {
      const deal = parseSponsorDeal({ id: 'x', name: 'sponsor_deal', reason: 'Take the box?' })
      expect(deal?.offer).toBe('Take the box?')
      expect(deal?.sponsor).toBe('A sponsor')
    })

    it('returns null when there is no id', () => {
      expect(parseSponsorDeal(undefined)).toBeNull()
      expect(parseSponsorDeal(null)).toBeNull()
      expect(parseSponsorDeal({ name: 'sponsor_deal' })).toBeNull()
      expect(parseSponsorDeal({ id: '' })).toBeNull()
    })
  })

  describe('sendInquiryWithDeal', () => {
    it('sends POST to /inquire exactly as sendInquiry does', async () => {
      globalThis.fetch = mockFetch({ response: story })

      const { sendInquiryWithDeal } = useGameApi(SERVER_URL)
      await sendInquiryWithDeal('Hello')

      expect(globalThis.fetch).toHaveBeenCalledWith(
        `${SERVER_URL}/inquire`,
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: 'Hello' }),
          signal: expect.any(AbortSignal),
        }),
      )
    })

    it('returns the story and no deal from a plain Floor 5 Narrator', async () => {
      globalThis.fetch = mockFetch({ response: story })

      const { sendInquiryWithDeal } = useGameApi(SERVER_URL)
      const result = await sendInquiryWithDeal('Hello')

      expect(result.story).toEqual(story)
      expect(result.deal).toBeNull()
    })

    it('returns the deal when the turn paused on an interrupt', async () => {
      globalThis.fetch = mockFetch({ response: story, interrupt })

      const { sendInquiryWithDeal } = useGameApi(SERVER_URL)
      const result = await sendInquiryWithDeal('Hello')

      expect(result.story).toEqual(story)
      expect(result.deal?.id).toBe('v1:tool_call:abc:123')
      expect(result.deal?.sponsor).toBe('The Bellevue Consortium')
    })

    it('sets error on failure and throws', async () => {
      globalThis.fetch = mockFetch({}, false, 500)

      const { sendInquiryWithDeal, error, loading } = useGameApi(SERVER_URL)

      await expect(sendInquiryWithDeal('Hello')).rejects.toThrow('Request failed with status 500')
      expect(error.value).toBe('Request failed with status 500')
      expect(loading.value).toBe(false)
    })
  })

  describe('respondToDeal', () => {
    it('sends POST to /respond with the interrupt id and the answer', async () => {
      globalThis.fetch = mockFetch({ response: story })

      const { respondToDeal } = useGameApi(SERVER_URL)
      await respondToDeal('v1:tool_call:abc:123', true)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        `${SERVER_URL}/respond`,
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ interrupt_id: 'v1:tool_call:abc:123', accepted: true }),
          signal: expect.any(AbortSignal),
        }),
      )
    })

    it('sends a refusal as accepted false', async () => {
      globalThis.fetch = mockFetch({ response: story })

      const { respondToDeal } = useGameApi(SERVER_URL)
      await respondToDeal('id-1', false)

      const body = JSON.parse((globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0][1].body)
      expect(body).toEqual({ interrupt_id: 'id-1', accepted: false })
    })

    it('returns the resumed story, with a new deal when the Narrator pauses again', async () => {
      globalThis.fetch = mockFetch({ response: story, interrupt: { ...interrupt, id: 'second' } })

      const { respondToDeal } = useGameApi(SERVER_URL)
      const result = await respondToDeal('first', true)

      expect(result.story).toEqual(story)
      expect(result.deal?.id).toBe('second')
    })

    it('sets error on failure and throws', async () => {
      globalThis.fetch = mockFetch({}, false, 404)

      const { respondToDeal, error } = useGameApi(SERVER_URL)

      await expect(respondToDeal('gone', true)).rejects.toThrow('Request failed with status 404')
      expect(error.value).toBe('Request failed with status 404')
    })
  })
})
