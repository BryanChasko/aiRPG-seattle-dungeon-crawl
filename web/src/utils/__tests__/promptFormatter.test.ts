import { describe, it, expect } from 'vitest'
import { formatInitPrompt } from '../promptFormatter'
import type { CharacterForm } from '../../types'

describe('formatInitPrompt', () => {
  it('interpolates all character fields into the prompt template', () => {
    const form: CharacterForm = {
      name: 'Cordula Vance',
      pronouns: 'she/her',
      species: 'Human (Seattle Native)',
      characterClass: 'Amphibious Breacher',
      serverUrl: 'http://localhost:3000',
    }

    const result = formatInitPrompt(form)

    expect(result).toBe(
      "Create a new player named Cordula Vance (pronouns she/her), a Human (Seattle Native) Amphibious Breacher. You can then welcome them to the dungeon: they just came through the collapse at Pier 59. Describe the surroundings of the player and create an atmosphere that the player can bounce off of. Don't make more than 100 words.",
    )
  })

  it('works with different character combinations', () => {
    const form: CharacterForm = {
      name: 'Barnaby',
      pronouns: 'he/him',
      species: 'Uplifted Giant Pacific Octopus',
      characterClass: 'Rain Warden',
      serverUrl: 'https://example.com',
    }

    const result = formatInitPrompt(form)

    expect(result).toContain('Barnaby')
    expect(result).toContain('he/him')
    expect(result).toContain('Uplifted Giant Pacific Octopus')
    expect(result).toContain('Rain Warden')
  })
})
