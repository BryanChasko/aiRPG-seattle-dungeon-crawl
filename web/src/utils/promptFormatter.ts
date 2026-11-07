import type { CharacterForm } from '../types'

// The first message of every game; the message list hides it
export const INIT_PROMPT_PREFIX = 'Create a new player named '

export function formatInitPrompt(form: CharacterForm): string {
  return `${INIT_PROMPT_PREFIX}${form.name} who is a ${form.gender} ${form.race} ${form.characterClass}. You can then welcome them to the dungeon: they just fell through the floor with no shoes on. Describe the surroundings of the player and create an atmosphere that the player can bounce off of. Don't make more than 100 words.`
}
