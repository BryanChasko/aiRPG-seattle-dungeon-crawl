import type { CharacterForm, ValidationErrors } from '../types'

export function validateForm(form: CharacterForm): ValidationErrors {
  const errors: ValidationErrors = {}

  if (!form.name) {
    errors.name = 'Character name is required'
  }

  if (!form.pronouns) {
    errors.pronouns = 'Pronouns are required'
  }

  if (!form.species) {
    errors.species = 'Species is required'
  }

  if (!form.characterClass) {
    errors.characterClass = 'Class is required'
  }

  if (!form.serverUrl) {
    errors.serverUrl = 'Server URL is required'
  } else if (!form.serverUrl.startsWith('http://') && !form.serverUrl.startsWith('https://')) {
    errors.serverUrl = 'Server URL must start with http:// or https://'
  }

  return errors
}
