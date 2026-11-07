import { describe, it, expect } from 'vitest'
import * as fc from 'fast-check'
import { formatInitPrompt, INIT_PROMPT_PREFIX } from '../promptFormatter'
import { PARTY_LEADS, PARTY_LINE } from '../../party'
import type { CharacterForm } from '../../types'

/**
 * Property 3: Inquiry prompt formatting
 *
 * For either party lead and any server URL, the opening prompt names the lead
 * (name, pronouns, species, class), carries the whole party line, and starts with
 * the prefix the message list uses to hide it.
 */

const leadArb = fc.constantFrom(...PARTY_LEADS)

const validUrlArb = fc
  .string({ minLength: 1, maxLength: 50 })
  .map((s) => 'https://' + s)

const validFormArb: fc.Arbitrary<CharacterForm> = fc
  .tuple(leadArb, validUrlArb)
  .map(([lead, serverUrl]) => ({
    name: lead.name,
    pronouns: lead.pronouns,
    species: lead.species,
    characterClass: lead.characterClass,
    serverUrl,
  }))

describe('Property 3: Inquiry prompt formatting', () => {
  it('contains the lead name, pronouns, species, and class in the prompt', () => {
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

  it('always opens with the hidden prefix and the whole party', () => {
    fc.assert(
      fc.property(validFormArb, (form) => {
        const prompt = formatInitPrompt(form)

        expect(prompt.startsWith(INIT_PROMPT_PREFIX)).toBe(true)
        expect(prompt).toContain(PARTY_LINE)
        expect(prompt).not.toContain(form.serverUrl)
      }),
      { numRuns: 100 },
    )
  })
})
