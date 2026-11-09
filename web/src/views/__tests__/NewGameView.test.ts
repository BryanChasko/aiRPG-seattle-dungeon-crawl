import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import NewGameView from '../NewGameView.vue'

const pushMock = vi.fn()

const routeQuery = vi.hoisted(() => ({ value: {} as Record<string, string> }))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: pushMock }),
  useRoute: () => ({ query: routeQuery.value }),
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
    routeQuery.value = {}
    localStorage.clear()
  })

  afterEach(() => {
    globalThis.fetch = originalFetch
  })

  describe('form rendering', () => {
    it('renders the party picker, the server URL field and an Enter button', () => {
      const wrapper = mountComponent()

      expect(wrapper.findAll('input[name="party-member"]')).toHaveLength(2)
      expect(wrapper.text()).toContain('Play as')
      expect(wrapper.text()).not.toContain('Speak as')
      expect(wrapper.find('#server-url').exists()).toBe(true)
      expect(wrapper.find('#character-name').exists()).toBe(false)

      const startButton = wrapper.find('button[type="submit"]')
      expect(startButton.exists()).toBe(true)
      expect(startButton.text()).toBe('Enter the Dungeon')
    })
  })

  describe('the set party', () => {
    it('offers exactly the two party leads with species, Cordula Vance first and selected', () => {
      const wrapper = mountComponent()
      const radios = wrapper.findAll('input[name="party-member"]')
      const names = wrapper.findAll('.party-name').map((o) => o.text())

      expect(names).toEqual(['Cordula Vance: Human', 'Barnaby: Giant Pacific Octopus'])
      expect(radios.map((r) => (r.element as HTMLInputElement).value)).toEqual([
        'Cordula Vance',
        'Barnaby',
      ])
      expect((radios[0].element as HTMLInputElement).checked).toBe(true)
      expect(wrapper.findAll('.party-portrait')).toHaveLength(2)
      expect(wrapper.find('#lead-pronouns').text()).toBe('she/her')
      expect(wrapper.find('#lead-species').text()).toBe('Human (Seattle Native)')
      expect(wrapper.find('#lead-class').text()).toBe('Amphibious Breacher')
    })

    it("shows Barnaby's sheet when the player plays as him", async () => {
      const wrapper = mountComponent()
      await wrapper.findAll('input[name="party-member"]')[1].setValue()

      expect(wrapper.find('#lead-pronouns').text()).toBe('he/him')
      expect(wrapper.find('#lead-species').text()).toBe('Uplifted Giant Pacific Octopus')
      expect(wrapper.find('#lead-class').text()).toBe('Benthic Dragoon')
      expect(wrapper.find('#lead-role').text()).toBe('Party leader')
    })

    it('names no later-floor companions on the entry surface', () => {
      const wrapper = mountComponent()

      expect(wrapper.text()).not.toContain('Shelly')
      expect(wrapper.text()).not.toContain('Chonks')
      expect(wrapper.find('.companions').text()).toContain('later floors')
    })

    it('labels the picker Play as and seeds the server from a deep link', () => {
      routeQuery.value = { server: 'http://127.0.0.1:8009/' }
      const wrapper = mountComponent()

      expect(wrapper.text()).toContain('Play as')
      expect((wrapper.find('#server-url').element as HTMLInputElement).value).toBe(
        'http://127.0.0.1:8009',
      )
    })

    it('teaches the four-terminal launch under the server field', () => {
      const wrapper = mountComponent()
      const text = wrapper.text()

      expect(text).toContain('8000')
      expect(text).toContain('8001')
      expect(text).toContain('8002')
      expect(text).toContain('8009')
      const hrefs = wrapper.findAll('a').map((a) => a.attributes('href') ?? '')
      expect(hrefs.some((h) => h.endsWith('/workshop/floor-5.md'))).toBe(true)
      expect(hrefs.some((h) => h.endsWith('/workshop/floor-6.md'))).toBe(true)
      expect(
        hrefs.some((h) => h === 'https://github.com/BryanChasko/aiRPG-seattle-dungeon-crawl'),
      ).toBe(true)
    })
  })

  describe('validation', () => {
    it('prefills the Floor 6 local Narrator and explains the field', () => {
      const wrapper = mountComponent()
      expect((wrapper.find('#server-url').element as HTMLInputElement).value).toBe(
        'http://127.0.0.1:8009',
      )
      expect(wrapper.find('#server-help').text()).toContain('Narrator server you build')
    })

    it('only asks for the server URL: the party is already filled in', async () => {
      const wrapper = mountComponent()
      await wrapper.find('#server-url').setValue('')

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
      await wrapper.findAll('input[name="party-member"]')[1].setValue()
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
      expect(errorEl.text()).toContain('8009')
    })

    it('maps a failed fetch to the four-terminal recovery words', async () => {
      globalThis.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'))

      const wrapper = mountComponent()
      await wrapper.find('#server-url').setValue('http://127.0.0.1:8009')

      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      const errorEl = wrapper.find('.submit-error')
      expect(errorEl.text()).toContain('Could not reach the game server')
      expect(errorEl.text()).not.toContain('Failed to fetch')
      expect(errorEl.text()).toContain('8000')
      expect(errorEl.text()).toContain('8001')
      expect(errorEl.text()).toContain('8002')
    })
  })
})
