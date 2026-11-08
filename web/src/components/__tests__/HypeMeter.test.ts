import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HypeMeter from '../HypeMeter.vue'
import type { HypeSnapshot } from '../../types'

function mountMeter(hype: HypeSnapshot | null) {
  return mount(HypeMeter, { props: { hype } })
}

const base: HypeSnapshot = { hype: 12, sponsor_tiers: [10], next_sponsor_at: 25, last_event: '' }

describe('HypeMeter', () => {
  it('renders nothing when the Narrator serves no Hype', () => {
    const wrapper = mountMeter(null)
    expect(wrapper.find('.hype-meter').exists()).toBe(false)
  })

  it('shows the Hype number', () => {
    const wrapper = mountMeter(base)
    expect(wrapper.find('.hype-value').text()).toBe('12')
  })

  it('shows how far it is to the next sponsor box', () => {
    const wrapper = mountMeter(base)
    expect(wrapper.find('.hype-next').text()).toBe('Next sponsor box at 25 Hype')
    expect(wrapper.find('[role="progressbar"]').attributes('aria-valuenow')).toBe('48')
  })

  it('fills the bar and says so once every sponsor tier is reached', () => {
    const wrapper = mountMeter({ hype: 60, sponsor_tiers: [10, 25, 50], next_sponsor_at: null, last_event: '' })
    expect(wrapper.find('.hype-next').text()).toBe('Every sponsor box has been sent')
    expect(wrapper.find('[role="progressbar"]').attributes('aria-valuenow')).toBe('100')
  })

  it('shows the last event only when there is one', () => {
    expect(mountMeter(base).find('.hype-event').exists()).toBe(false)
    const wrapper = mountMeter({ ...base, last_event: 'achievement +5' })
    expect(wrapper.find('.hype-event').text()).toBe('achievement +5')
  })

  it('clamps the bar at zero for negative Hype', () => {
    const wrapper = mountMeter({ ...base, hype: -3 })
    expect(wrapper.find('[role="progressbar"]').attributes('aria-valuenow')).toBe('0')
  })
})
