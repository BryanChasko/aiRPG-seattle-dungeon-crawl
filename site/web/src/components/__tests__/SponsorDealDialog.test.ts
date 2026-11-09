import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SponsorDealDialog from '../SponsorDealDialog.vue'
import type { SponsorDeal } from '../../types'

const deal: SponsorDeal = {
  id: 'deal-1',
  name: 'sponsor_deal',
  sponsor: 'The Bellevue Consortium',
  offer: 'Wear the logo for one floor.',
  reward: 'a Silver Box',
  cost: 'your dignity',
}

function mountDialog(props: { deal: SponsorDeal | null; disabled?: boolean }) {
  return mount(SponsorDealDialog, { props })
}

describe('SponsorDealDialog', () => {
  it('renders nothing when no deal is pending', () => {
    const wrapper = mountDialog({ deal: null })
    expect(wrapper.find('.sponsor-deal').exists()).toBe(false)
  })

  it('shows the sponsor and the offer', () => {
    const wrapper = mountDialog({ deal })
    expect(wrapper.find('.sponsor-deal__title').text()).toContain('The Bellevue Consortium')
    expect(wrapper.find('.sponsor-deal__offer').text()).toBe('Wear the logo for one floor.')
  })

  it('shows the reward and the cost when the deal has them', () => {
    const text = mountDialog({ deal }).text()
    expect(text).toContain('a Silver Box')
    expect(text).toContain('your dignity')
  })

  it('leaves out empty reward and cost lines', () => {
    const wrapper = mountDialog({ deal: { ...deal, reward: '', cost: '' } })
    expect(wrapper.findAll('.sponsor-deal__line')).toHaveLength(0)
  })

  it('emits accept when the accept button is clicked', async () => {
    const wrapper = mountDialog({ deal })
    await wrapper.find('.sponsor-deal__btn--accept').trigger('click')
    expect(wrapper.emitted('accept')).toHaveLength(1)
    expect(wrapper.emitted('refuse')).toBeUndefined()
  })

  it('emits refuse when the refuse button is clicked', async () => {
    const wrapper = mountDialog({ deal })
    await wrapper.find('.sponsor-deal__btn--refuse').trigger('click')
    expect(wrapper.emitted('refuse')).toHaveLength(1)
    expect(wrapper.emitted('accept')).toBeUndefined()
  })

  it('disables both buttons while a request is in flight', () => {
    const wrapper = mountDialog({ deal, disabled: true })
    const buttons = wrapper.findAll('button')
    expect(buttons).toHaveLength(2)
    for (const b of buttons) {
      expect((b.element as HTMLButtonElement).disabled).toBe(true)
    }
  })
})
