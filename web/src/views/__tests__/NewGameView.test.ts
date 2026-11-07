import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import NewGameView from '../NewGameView.vue'

const pushMock = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: pushMock }),
}))

function mockFetchFailure(status = 500) {
  return vi.fn().mockResolvedValue({
    ok: false,
    status,
    json: () => Promise.resolve({}),
  })
}

function mountComponent() {
  return mount(NewGameView, {
    global: {
      plugins: [createPinia()],
    },
  })
}

describe('NewGameView', () => {
  const originalFetch = globalThis.fetch

  beforeEach(() => {
    setActivePinia(createPinia())
    pushMock.mockClear()
  })

  afterEach(() => {
    globalThis.fetch = originalFetch
  })

  describe('form rendering', () => {
    it('renders the party picker, the server URL field and an Enter button', () => {
      const wrapper = mountComponent()

      expect(wrapper.find('#party-member').exists()).toBe(true)
      expect(wrapper.find('#server-url').exists()).toBe(true)
      expect(wrapper.find('#character-name').exists()).toBe(false)

      const startButton = wrapper.find('button[type="submit"]')
      expect(startButton.exists()).toBe(true)
      expect(startButton.text()).toBe('Enter the Dungeon')
    })
  })

  describe('the set party', () => {
    it('offers exactly the two party leads, Cordula Vance first and selected', () => {
      const wrapper = mountComponent()
      const select = wrapper.find('#party-member')
      const options = select.findAll('option')

      expect(options.map(o => o.text())).toEqual(['Cordula Vance', 'Barnaby'])
      expect((select.element as HTMLSelectElement).value).toBe('Cordula Vance')
      expect(wrapper.find('#lead-pronouns').text()).toBe('she/her')
      expect(wrapper.find('#lead-species').text()).toBe('Human (Seattle Native)')
      expect(wrapper.find('#lead-class').text()).toBe('Amphibious Breacher')
    })

    it('shows Barnaby\'s sheet when he speaks for the party', async () => {
      const wrapper = mountComponent()
      await wrapper.find('#party-member').setValue('Barnaby')

      expect(wrapper.find('#lead-pronouns').text()).toBe('he/him')
      expect(wrapper.find('#lead-species').text()).toBe('Uplifted Giant Pacific Octopus')
      expect(wrapper.find('#lead-class').text()).toBe('Benthic Dragoon')
      expect(wrapper.find('#lead-role').text()).toBe('Party leader')
    })

    it('lists Shelly and Chonks as companions', () => {
      const wrapper = mountComponent()
      const companions = wrapper.find('.companions').text()

      expect(companions).toContain('Shelly the geoduck')
      expect(companions).toContain('Chonks the spiny lumpsucker')
    })
  })

  describe('validation', () => {
    it('only asks for the server URL: the party is already filled in', async () => {
      const wrapper = mountComponent()

      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      const fieldErrors = wrapper.findAll('.field-error')
      expect(fieldErrors).toHaveLength(1)
      expect(fieldErrors[0].text()).toContain('Server URL is required')
    })
  })

  describe('loading state', () => {
    it('disables the button and shows "Descending..." during submission', async () => {
      // Use a fetch that never resolves to keep loading state active
      globalThis.fetch = vi.fn().mockReturnValue(new Promise(() => {}))

      const wrapper = mountComponent()
      await wrapper.find('#server-url').setValue('https://example.com')

      await wrapper.find('form').trigger('submit.prevent')
      await wrapper.vm.$nextTick()

      const button = wrapper.find('button[type="submit"]')
      expect(button.attributes('disabled')).toBeDefined()
      expect(button.text()).toBe('Descending...')
    })

    it('sends the party prompt for the selected lead', async () => {
      const fetchMock = vi.fn().mockReturnValue(new Promise(() => {}))
      globalThis.fetch = fetchMock

      const wrapper = mountComponent()
      await wrapper.find('#party-member').setValue('Barnaby')
      await wrapper.find('#server-url').setValue('https://example.com')

      await wrapper.find('form').trigger('submit.prevent')
      await wrapper.vm.$nextTick()

      const body = JSON.parse(fetchMock.mock.calls[0][1].body)
      expect(body.question).toContain('The player speaks as Barnaby (pronouns he/him)')
      expect(body.question).toContain('Shelly the geoduck')
    })
  })

  describe('error handling', () => {
    it('displays error message when server returns an error', async () => {
      globalThis.fetch = mockFetchFailure(500)

      const wrapper = mountComponent()
      await wrapper.find('#server-url').setValue('https://example.com')

      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      const errorEl = wrapper.find('.submit-error')
      expect(errorEl.exists()).toBe(true)
      expect(errorEl.text()).toContain('Request failed with status 500')
    })
  })
})
