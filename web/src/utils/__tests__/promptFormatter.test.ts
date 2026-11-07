import { describe, it, expect } from 'vitest'
import { formatInitPrompt, INIT_PROMPT_PREFIX } from '../promptFormatter'
import { PARTY_LINE } from '../../party'
import type { CharacterForm } from '../../types'

describe('formatInitPrompt', () => {
  it('opens the crawl for the party, speaking as Cordula', () => {
    const form: CharacterForm = {
      name: 'Cordula Vance',
      pronouns: 'she/her',
      species: 'Human (Seattle Native)',
      characterClass: 'Amphibious Breacher',
      serverUrl: 'http://localhost:3000',
    }

    const result = formatInitPrompt(form)

    expect(result).toBe(
      `We play as the party. The player speaks as Cordula Vance (pronouns she/her), a Human (Seattle Native) Amphibious Breacher. ${PARTY_LINE} Look up Cordula Vance with the Character Agent; if Cordula Vance or Barnaby is not registered yet, register them first with their cast scores. Then welcome the party to the dungeon: they just came through the collapse at Pier 59. Describe the surroundings and create an atmosphere the player can bounce off of. Don't make more than 100 words.`,
    )
  })

  it('speaks as Barnaby and still names the whole party', () => {
    const form: CharacterForm = {
      name: 'Barnaby',
      pronouns: 'he/him',
      species: 'Uplifted Giant Pacific Octopus',
      characterClass: 'Benthic Dragoon',
      serverUrl: 'https://example.com',
    }

    const result = formatInitPrompt(form)

    expect(result.startsWith(INIT_PROMPT_PREFIX)).toBe(true)
    expect(result).toContain('speaks as Barnaby (pronouns he/him)')
    expect(result).toContain('Cordula Vance (she/her)')
    expect(result).toContain('Shelly the geoduck')
    expect(result).toContain('Chonks the spiny lumpsucker')
  })
})
