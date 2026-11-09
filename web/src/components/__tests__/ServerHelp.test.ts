import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ServerHelp from '../ServerHelp.vue'

describe('ServerHelp', () => {
  it('teaches the four-terminal launch at a glance', () => {
    const wrapper = mount(ServerHelp)
    const text = wrapper.text()

    expect(text).toContain('8000')
    expect(text).toContain('rules')
    expect(text).toContain('8001')
    expect(text).toContain('registry')
    expect(text).toContain('8002')
    expect(text).toContain('dice')
    expect(text).toContain('8009')
    expect(text).toContain('http://127.0.0.1:8009')
  })

  it('links the repo, the Floor 5 launch and Floor 6 as blob/main URLs', () => {
    const wrapper = mount(ServerHelp)
    const hrefs = wrapper.findAll('a').map((a) => a.attributes('href') ?? '')

    expect(hrefs).toContain('https://github.com/BryanChasko/aiRPG-seattle-dungeon-crawl')
    expect(hrefs).toContain(
      'https://github.com/BryanChasko/aiRPG-seattle-dungeon-crawl/blob/main/workshop/floor-5.md',
    )
    expect(hrefs).toContain(
      'https://github.com/BryanChasko/aiRPG-seattle-dungeon-crawl/blob/main/workshop/floor-6.md',
    )
  })
})
