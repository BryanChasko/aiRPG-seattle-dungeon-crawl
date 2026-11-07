<template>
  <div class="new-game-view">
    <div class="scroll-wrapper" :class="{ 'scroll-revealed': revealed }">
      <!-- Top scroll rod -->
      <div class="scroll-rod scroll-rod--top"></div>
      <!-- Bottom scroll rod -->
      <div class="scroll-rod scroll-rod--bottom"></div>

      <div class="form-card paper-sheet">
        <h1 class="form-title">Register Your Crawler</h1>

        <form class="character-form" @submit.prevent="handleSubmit">
          <div v-if="submitError" class="submit-error">{{ submitError }}</div>

          <div class="form-group">
            <label for="character-name" class="form-label">Crawler Name</label>
            <input
              id="character-name"
              v-model="form.name"
              type="text"
              class="form-input"
              :class="{ 'input-error': errors.name }"
              placeholder="Enter your Crawler's name"
            />
            <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
          </div>

          <div class="form-group">
            <label for="pronouns" class="form-label">Pronouns</label>
            <select id="pronouns" v-model="form.pronouns" class="form-input" :class="{ 'input-error': errors.pronouns }">
              <option value="" disabled>Select pronouns</option>
              <option v-for="g in pronounsOptions" :key="g" :value="g">{{ g }}</option>
            </select>
            <span v-if="errors.pronouns" class="field-error">{{ errors.pronouns }}</span>
          </div>

          <div class="form-group">
            <label for="species" class="form-label">Species</label>
            <select id="species" v-model="form.species" class="form-input" :class="{ 'input-error': errors.species }">
              <option value="" disabled>Select species</option>
              <option v-for="r in speciesOptions" :key="r" :value="r">{{ r }}</option>
            </select>
            <span v-if="errors.species" class="field-error">{{ errors.species }}</span>
          </div>

          <div class="form-group">
            <label for="character-class" class="form-label">Class</label>
            <select id="character-class" v-model="form.characterClass" class="form-input" :class="{ 'input-error': errors.characterClass }">
              <option value="" disabled>Select class</option>
              <option v-for="c in classOptions" :key="c" :value="c">{{ c }}</option>
            </select>
            <span v-if="errors.characterClass" class="field-error">{{ errors.characterClass }}</span>
          </div>

          <div class="form-group">
            <label for="server-url" class="form-label">Server URL</label>
            <input
              id="server-url"
              v-model="form.serverUrl"
              type="text"
              class="form-input"
              :class="{ 'input-error': errors.serverUrl }"
              placeholder="https://your-server.example.com"
            />
            <span v-if="errors.serverUrl" class="field-error">{{ errors.serverUrl }}</span>
          </div>

          <button type="submit" class="start-button" :disabled="loading">
            {{ loading ? 'Descending...' : 'Enter the Dungeon' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { CharacterForm, ValidationErrors } from '@/types'
import { validateForm } from '@/utils/validation'
import { formatInitPrompt } from '@/utils/promptFormatter'
import { useGameApi } from '@/composables/useGameApi'
import { useGameStore } from '@/stores/gameStore'

const router = useRouter()
const store = useGameStore()
const revealed = ref(false)

onMounted(() => {
  setTimeout(() => {
    revealed.value = true
  }, 1000)
})

const pronounsOptions: CharacterForm['pronouns'][] = ['she/her', 'he/him', 'they/them', 'any pronouns']

const speciesOptions: CharacterForm['species'][] = [
  'Human (Seattle Native)',
  'Human (Transplant)',
  'Uplifted Giant Pacific Octopus',
  'Uplifted Crow',
  'Harbor Seal',
  'Sea Otter',
  'Banana Slug',
  'Fremont Troll-kin',
  'Underground Ghost',
]

const classOptions: CharacterForm['characterClass'][] = [
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
]

const form = reactive<CharacterForm>({
  name: '',
  pronouns: '' as CharacterForm['pronouns'],
  species: '' as CharacterForm['species'],
  characterClass: '' as CharacterForm['characterClass'],
  serverUrl: '',
})

const errors = ref<ValidationErrors>({})
const loading = ref(false)
const submitError = ref<string | null>(null)

async function handleSubmit() {
  const validationErrors = validateForm(form)
  if (Object.keys(validationErrors).length > 0) {
    errors.value = validationErrors
    return
  }

  errors.value = {}
  submitError.value = null
  loading.value = true

  try {
    const prompt = formatInitPrompt(form)
    const { sendInquiry } = useGameApi(form.serverUrl)
    await sendInquiry(prompt)
    store.setConnection(form.serverUrl, form.name)

    // Roll the scroll closed, then navigate
    revealed.value = false
    await new Promise(resolve => setTimeout(resolve, 1500))
    router.push({ name: 'game', params: { characterName: form.name } })
  } catch (e) {
    submitError.value = e instanceof Error ? e.message : 'Failed to connect to server'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.new-game-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
}

.form-card {
  position: relative;
  width: 100%;
  max-width: 480px;
  padding: 2.5rem;
  background-color: #161b26;
  background-image: url('/textures/obsidian-512x512.webp');
  background-size: cover;
  border: 1px solid #3a3550;
  box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.08);
  border-radius: 4px;
}

/* --- Scroll unroll wrapper --- */
.scroll-wrapper {
  position: relative;
  width: 100%;
  max-width: 480px;
}

.scroll-wrapper .form-card {
  clip-path: inset(50% 0 50% 0);
  transition: clip-path 1.4s cubic-bezier(0.22, 1, 0.36, 1);
}

.scroll-wrapper.scroll-revealed .form-card {
  clip-path: inset(0 0 0 0);
}

/* Wooden scroll rods */
.scroll-rod {
  position: absolute;
  left: -8px;
  right: -8px;
  height: 14px;
  background: linear-gradient(180deg, #8e3bbf 0%, #6a2c91 40%, #3d1f5c 100%);
  border-radius: 7px;
  z-index: 2;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.scroll-rod::before,
.scroll-rod::after {
  content: '';
  position: absolute;
  top: -4px;
  width: 18px;
  height: 22px;
  background: linear-gradient(180deg, #b04ce0, #6a2c91);
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.scroll-rod::before { left: -6px; }
.scroll-rod::after { right: -6px; }

.scroll-rod--top {
  top: 50%;
  transition: top 1.4s cubic-bezier(0.22, 1, 0.36, 1);
}

.scroll-rod--bottom {
  top: 50%;
  transition: top 1.4s cubic-bezier(0.22, 1, 0.36, 1);
}

.scroll-revealed .scroll-rod--top {
  top: -7px;
}

.scroll-revealed .scroll-rod--bottom {
  top: calc(100% - 7px);
}

.form-title {
  font-family: var(--font-heading);
  color: var(--color-red-deep);
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
}

.character-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-family: var(--font-ui);
  font-weight: 600;
  color: var(--color-ink-light);
  font-size: 0.95rem;
}

.form-input {
  font-family: var(--font-body);
  font-size: 1rem;
  padding: 0.6rem 0.75rem;
  border: 2px solid var(--color-parchment-dark);
  border-radius: 4px;
  background-color: var(--color-parchment);
  color: var(--color-ink);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-gold);
  box-shadow: var(--shadow-glow);
}

.form-input::placeholder {
  color: var(--color-ink-light);
  opacity: 0.6;
}

.start-button {
  margin-top: 0.75rem;
  padding: 0.75rem 1.5rem;
  font-family: var(--font-heading);
  font-size: 1.25rem;
  color: var(--color-gold-light);
  background-color: var(--color-wood-medium);
  border: var(--border-gold);
  border-radius: var(--border-radius-panel);
  cursor: pointer;
  box-shadow: var(--shadow-panel);
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

.start-button:hover {
  background-color: var(--color-wood-dark);
  box-shadow: var(--shadow-glow);
}

.start-button:active {
  transform: translateY(1px);
}

.start-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: var(--color-wood-light);
  box-shadow: none;
}

.start-button:disabled:hover {
  background-color: var(--color-wood-light);
  box-shadow: none;
}

.field-error {
  font-family: var(--font-body);
  font-size: 0.85rem;
  color: var(--color-red-accent);
}

.input-error {
  border-color: var(--color-red-accent);
}

.submit-error {
  font-family: var(--font-body);
  font-size: 0.9rem;
  color: var(--color-parchment);
  background-color: var(--color-red-deep);
  padding: 0.6rem 0.75rem;
  border-radius: 4px;
  text-align: center;
}
</style>
