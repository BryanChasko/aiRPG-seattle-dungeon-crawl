import type { CharacterForm } from './types'

export type PartyLead = Omit<CharacterForm, 'serverUrl'> & {
  role: string
  shortSpecies: string
  flavor: string
  portrait: string
}

// The set party (workshop/world/cast.md). The player plays as one of the two Crawlers.
export const PARTY_LEADS: PartyLead[] = [
  {
    name: 'Cordula Vance',
    pronouns: 'she/her',
    species: 'Human (Seattle Native)',
    shortSpecies: 'Human',
    characterClass: 'Amphibious Breacher',
    role: 'Crawler, tank',
    flavor: 'Drill-cadence dancer. Takes Power, Footwork and the Final Beat.',
    portrait: 'portraits/cordula.webp',
  },
  {
    name: 'Barnaby',
    pronouns: 'he/him',
    species: 'Uplifted Giant Pacific Octopus',
    shortSpecies: 'Giant Pacific Octopus',
    characterClass: 'Benthic Dragoon',
    role: 'Party leader',
    flavor: 'Kraken-scale, about 22 feet across. Takes Choreography and Presence.',
    portrait: 'portraits/barnaby.webp',
  },
]

export const COMPANIONS = [
  { name: 'Shelly the geoduck', portrait: 'portraits/shelly.webp' },
  { name: 'Chonks the spiny lumpsucker', portrait: 'portraits/chonks.webp' },
]

export const PARTY_LINE =
  'The party: Cordula Vance (she/her), a Human (Seattle Native) Amphibious Breacher; Barnaby (he/him), an Uplifted Giant Pacific Octopus Benthic Dragoon and the party leader; and their companions Shelly the geoduck and Chonks the spiny lumpsucker.'
