import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useGameStore } from '../gameStore'
import type { HypeSnapshot, SponsorDeal } from '../../types'

const snapshot: HypeSnapshot = { hype: 12, sponsor_tiers: [10], next_sponsor_at: 25, last_event: '' }
const deal: SponsorDeal = {
  id: 'deal-1',
  name: 'sponsor_deal',
  sponsor: 'The Bellevue Consortium',
  offer: 'Wear the logo.',
  reward: 'a Silver Box',
  cost: '',
}

describe('useGameStore Floor 6 encounters', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('starts with no hype and no pending deal', () => {
    const store = useGameStore()
    expect(store.hype).toBeNull()
    expect(store.pendingDeal).toBeNull()
  })

  it('setHype stores the snapshot and accepts null', () => {
    const store = useGameStore()
    store.setHype(snapshot)
    expect(store.hype).toEqual(snapshot)
    store.setHype(null)
    expect(store.hype).toBeNull()
  })

  it('setPendingDeal stores the deal and accepts null', () => {
    const store = useGameStore()
    store.setPendingDeal(deal)
    expect(store.pendingDeal).toEqual(deal)
    store.setPendingDeal(null)
    expect(store.pendingDeal).toBeNull()
  })

  it('reset clears hype and the pending deal', () => {
    const store = useGameStore()
    store.setHype(snapshot)
    store.setPendingDeal(deal)
    store.reset()
    expect(store.hype).toBeNull()
    expect(store.pendingDeal).toBeNull()
  })

  it('does not change isInitialized', () => {
    const store = useGameStore()
    store.setHype(snapshot)
    store.setPendingDeal(deal)
    expect(store.isInitialized).toBe(false)
  })
})
