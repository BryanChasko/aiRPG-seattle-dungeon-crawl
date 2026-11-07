import { describe, it, expect } from 'vitest'
import * as fc from 'fast-check'
import { formatInitPrompt } from '../promptFormatter'
import type { CharacterForm } from '../../types'

/**
 * Property 3: Inquiry prompt formatting
 * Validates: Requirements 3.1
 *
 * For any valid CharacterForm (with non-empty name, pronouns, species, and class),
 * the generated prompt should contain the character's name, pronouns, species, and class
 * interpolated into the expected template string.
 */

const pronounsArb = fc.constantFrom('she/her', 'he/him', 'they/them', 'any pronouns') as fc.Arbitrary<
  CharacterForm['pronouns']
>

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
) as fc.Arbitrary<CharacterForm['species']>

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
) as fc.Arbitrary<CharacterForm['characterClass']>

const nonEmptyNameArb = fc
  .string({ minLength: 1, maxLength: 60 })
  .filter((s) => s.trim().length > 0)

const validUrlArb = fc
  .string({ minLength: 1, maxLength: 50 })
  .map((s) => 'https://' + s)

const validFormArb: fc.Arbitrary<CharacterForm> = fc.record({
  name: nonEmptyNameArb,
  pronouns: pronounsArb,
  species: speciesArb,
  characterClass: classArb,
  serverUrl: validUrlArb,
})

describe('Property 3: Inquiry prompt formatting', () => {
  it('contains the character name, pronouns, species, and class in the prompt', () => {
    fc.assert(
      fc.property(validFormArb, (form) => {
        const prompt = formatInitPrompt(form)

        expect(prompt).toContain(form.name)
        expect(prompt).toContain(form.pronouns)
        expect(prompt).toContain(form.species)
        expect(prompt).toContain(form.characterClass)
      }),
      { numRuns: 100 },
    )
  })

  it('matches the expected template format', () => {
    fc.assert(
      fc.property(validFormArb, (form) => {
        const prompt = formatInitPrompt(form)
        const expected = `Create a new player named ${form.name} (pronouns ${form.pronouns}), a ${form.species} ${form.characterClass}. You can then welcome them to the dungeon: they just came through the collapse at Pier 59. Describe the surroundings of the player and create an atmosphere that the player can bounce off of. Don't make more than 100 words.`

        expect(prompt).toBe(expected)
      }),
      { numRuns: 100 },
    )
  })
})
