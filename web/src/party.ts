import type { CharacterForm } from './types'

export type PartyLead = Omit<CharacterForm, 'serverUrl'> & { role: string; pickerLabel: string }

// The set party (workshop/world/cast.md). The player plays as one of the two Crawlers.
export const PARTY_LEADS: PartyLead[] = [
  {
    name: 'Cordula Vance',
    pickerLabel: 'Cordula Vance: Human',
    pronouns: 'she/her',
    species: 'Human (Seattle Native)',
    characterClass: 'Amphibious Breacher',
    role: 'Crawler, party tank, breacher (of doors, never of people)',
  },
  {
    name: 'Barnaby',
    pickerLabel: 'Barnaby: Giant Pacific Octopus',
    pronouns: 'he/him',
    species: 'Uplifted Giant Pacific Octopus',
    characterClass: 'Benthic Dragoon',
    role: 'Party leader',
  },
]

export const COMPANIONS = ['Shelly the geoduck', 'Chonks the spiny lumpsucker']

export const PARTY_LINE =
  'The party: Cordula Vance (she/her), a Human (Seattle Native) Amphibious Breacher; Barnaby (he/him), an Uplifted Giant Pacific Octopus Benthic Dragoon and the party leader; and their companions Shelly the geoduck and Chonks the spiny lumpsucker.'
