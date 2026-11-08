import { ref } from 'vue'
import type {
  StoryOutput,
  CharacterStats,
  ParsedMessage,
  RawMessage,
  HypeSnapshot,
  SponsorDeal,
  InquiryResult,
} from '../types'
import { parseMessages } from '../utils/messageParser'

export function useGameApi(serverUrl: string) {
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function sendInquiry(question: string): Promise<StoryOutput> {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`${serverUrl}/inquire`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })
      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`)
      }
      const data = await res.json()
      return data.response as StoryOutput
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Unknown error'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchUser(userName: string): Promise<CharacterStats> {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`${serverUrl}/user/${userName}`)
      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`)
      }
      return (await res.json()) as CharacterStats
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Unknown error'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchMessages(): Promise<ParsedMessage[]> {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`${serverUrl}/messages`)
      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`)
      }
      const raw: RawMessage[] = await res.json()
      return parseMessages(raw)
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Unknown error'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  // Floor 6 encounters. Both are optional: a plain Floor 5 Narrator has no /hype, no /respond and
  // no "interrupt" field, and every function here treats that as "nothing to show", never an error.

  async function postForResult(path: string, body: unknown): Promise<InquiryResult> {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`${serverUrl}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`)
      }
      const data = await res.json()
      return { story: data.response as StoryOutput, deal: parseSponsorDeal(data.interrupt) }
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Unknown error'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /** Like sendInquiry, but also returns the sponsor deal the turn paused on, or null. */
  function sendInquiryWithDeal(question: string): Promise<InquiryResult> {
    return postForResult('/inquire', { question })
  }

  /** Answer the paused turn; the Narrator resumes it and may pause again on a new deal. */
  function respondToDeal(interruptId: string, accepted: boolean): Promise<InquiryResult> {
    return postForResult('/respond', { interrupt_id: interruptId, accepted })
  }

  /** GET /hype, or null when the Narrator does not serve it or sends something unexpected. */
  async function fetchHype(): Promise<HypeSnapshot | null> {
    try {
      const res = await fetch(`${serverUrl}/hype`)
      if (!res.ok) return null
      return parseHype(await res.json())
    } catch {
      return null
    }
  }

  return {
    loading,
    error,
    sendInquiry,
    fetchUser,
    fetchMessages,
    sendInquiryWithDeal,
    respondToDeal,
    fetchHype,
  }
}

/** Accept a Hype payload only when it has the shape the HUD can draw. */
export function parseHype(raw: unknown): HypeSnapshot | null {
  if (typeof raw !== 'object' || raw === null) return null
  const r = raw as Record<string, unknown>
  if (typeof r.hype !== 'number' || !Number.isFinite(r.hype)) return null
  return {
    hype: r.hype,
    sponsor_tiers: Array.isArray(r.sponsor_tiers)
      ? r.sponsor_tiers.filter((t): t is number => typeof t === 'number')
      : [],
    next_sponsor_at: typeof r.next_sponsor_at === 'number' ? r.next_sponsor_at : null,
    last_event: typeof r.last_event === 'string' ? r.last_event : '',
  }
}

/** Accept an interrupt only when it has an id; missing deal details fall back to plain words. */
export function parseSponsorDeal(raw: unknown): SponsorDeal | null {
  if (typeof raw !== 'object' || raw === null) return null
  const r = raw as Record<string, unknown>
  if (typeof r.id !== 'string' || r.id === '') return null
  const reason =
    typeof r.reason === 'object' && r.reason !== null ? (r.reason as Record<string, unknown>) : {}
  const text = (v: unknown, fallback: string) => (typeof v === 'string' && v !== '' ? v : fallback)
  return {
    id: r.id,
    name: text(r.name, 'sponsor_deal'),
    sponsor: text(reason.sponsor, 'A sponsor'),
    offer: text(reason.offer, typeof r.reason === 'string' ? r.reason : 'A sponsor has an offer.'),
    reward: text(reason.reward, ''),
    cost: text(reason.cost, ''),
  }
}
