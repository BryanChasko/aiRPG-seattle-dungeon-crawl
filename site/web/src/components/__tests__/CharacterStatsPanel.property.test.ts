import { describe, it, expect } from 'vitest'
import * as fc from 'fast-check'
import { mount } from '@vue/test-utils'
import CharacterStatsPanel from '../CharacterStatsPanel.vue'
import type { CharacterStats } from '@/types'

/**
 * Property 4: Character stats rendering
 * Validates: Requirements 4.2
 *
 * For any valid CharacterStats object, the CharacterStatsPanel component
 * should render output containing the character's name, species, class, and pronouns.
 */

const pronounsArb = fc.constantFrom('she/her', 'he/him', 'they/them', 'any pronouns')

const speciesArb = fc.constantFrom(
  'Human (Seattle Native)',
  'Human (Transplant)',
  'Uplifted Giant Pacific Octopus',
  'Uplifted Crow',
  'Harbor Seal',
  'Sea Otter',
  'Banana Slug',
  'Fremont Troll-kin',
  'Underground Ghost',
)

const classArb = fc.constantFrom(
  'Amphibious Breacher',
  'Benthic Dragoon',
  'Kayak Patrol Ranger',
  'Ferry Engineer',
  'Ballard Brewer',
  'Fish-Toss Striker',
  'Grunge Bard',
  'Coffee Alchemist',
  'Salvage Artificer',
  'Rain Warden',
  'Floating-Bridge Engineer',
  'Startup Necromancer',
)

const abilityScoresArb = fc.record({
  strength: fc.integer({ min: 1, max: 20 }),
  dexterity: fc.integer({ min: 1, max: 20 }),
  constitution: fc.integer({ min: 1, max: 20 }),
  intelligence: fc.integer({ min: 1, max: 20 }),
  wisdom: fc.integer({ min: 1, max: 20 }),
  charisma: fc.integer({ min: 1, max: 20 }),
})

const characterStatsArb: fc.Arbitrary<CharacterStats> = fc.record({
  character_id: fc.uuid(),
  name: fc.string({ minLength: 1, maxLength: 60 }).filter((s) => s.trim().length > 0),
  pronouns: pronounsArb,
  species: speciesArb,
  character_class: classArb,
  level: fc.integer({ min: 1, max: 20 }),
  experience: fc.integer({ min: 0, max: 999999 }),
  stats: abilityScoresArb,
  inventory: fc.constant([]),
  created_at: fc.constant('2026-01-01T00:00:00.000000'),
})

describe('Property 4: Character stats rendering', () => {
  it('renders name, species, class, and pronouns for any valid CharacterStats', { timeout: 30000 }, () => {
    fc.assert(
      fc.property(characterStatsArb, (stats) => {
        const wrapper = mount(CharacterStatsPanel, {
          props: { stats, loading: false, error: null },
        })

        const text = wrapper.text()
        expect(text).toContain(stats.name)
        expect(text).toContain(stats.species)
        expect(text).toContain(stats.character_class)
        expect(text).toContain(stats.pronouns)
      }),
      { numRuns: 100 },
    )
  })
})
