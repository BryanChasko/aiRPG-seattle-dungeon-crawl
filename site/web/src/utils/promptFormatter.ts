import type { CharacterForm } from "../types";
import { PARTY_LINE } from "../party";

// The first message of every game; the message list hides it
export const INIT_PROMPT_PREFIX = "We play as the party. The player speaks as ";

// The structured-output retry the Narrator sends itself; it is not a player message
export const RETRY_PROMPT_PREFIX =
  "You must format the previous response as structured output";

export function formatInitPrompt(form: CharacterForm): string {
  return `${INIT_PROMPT_PREFIX}${form.name} (pronouns ${form.pronouns}), a ${form.species} ${form.characterClass}. ${PARTY_LINE} Look up ${form.name} with the Character Agent; if Cordula Vance or Barnaby is not registered yet, register them first with their cast scores. Then welcome the party to the dungeon: they just came through the collapse at Pier 59. Describe the surroundings and create an atmosphere the player can bounce off of. Don't make more than 100 words.`;
}
