<template>
  <div class="new-game-view">
    <div class="scroll-wrapper" :class="{ 'scroll-revealed': revealed }">
      <!-- Top scroll rod -->
      <div class="scroll-rod scroll-rod--top"></div>
      <!-- Bottom scroll rod -->
      <div class="scroll-rod scroll-rod--bottom"></div>

      <div class="form-card paper-sheet">
        <h1 class="form-title">The Party Descends</h1>

        <form class="character-form" @submit.prevent="handleSubmit">
          <div v-if="submitError" class="submit-error" role="alert">
            <p>{{ submitError }}</p>
            <ServerHelp class="submit-error__help" />
          </div>

          <div class="form-group">
            <label for="party-member" class="form-label">Play as</label>
            <select id="party-member" v-model="form.name" class="form-input">
              <option v-for="l in PARTY_LEADS" :key="l.name" :value="l.name">{{ l.pickerLabel }}</option>
            </select>
          </div>

          <dl class="party-sheet">
            <div><dt>Pronouns</dt><dd id="lead-pronouns">{{ lead.pronouns }}</dd></div>
            <div><dt>Species</dt><dd id="lead-species">{{ lead.species }}</dd></div>
            <div><dt>Class</dt><dd id="lead-class">{{ lead.characterClass }}</dd></div>
            <div><dt>Role</dt><dd id="lead-role">{{ lead.role }}</dd></div>
          </dl>
          <p class="companions">Companions join the party on later floors.</p>

          <div class="form-group">
            <label for="server-url" class="form-label">Server URL</label>
            <p class="field-help" id="server-url-help">
              The address of the game server you build in the workshop (the job code-named
              the Narrator). This page is only a window onto it. For a local game that is
              the address the fourth terminal prints.
            </p>
            <input
              id="server-url"
              v-model="form.serverUrl"
              type="text"
              class="form-input"
              :class="{ 'input-error': errors.serverUrl }"
              placeholder="http://127.0.0.1:8009"
              aria-describedby="server-url-help"
            />
            <span v-if="errors.serverUrl" class="field-error">{{ errors.serverUrl }}</span>
            <button type="button" class="preset-button" @click="useLocalServer">
              Use my local server: http://127.0.0.1:8009
            </button>
          </div>

          <ServerHelp v-if="!submitError" />

          <button type="submit" class="start-button" :disabled="loading">
            {{ loading ? 'Descending...' : 'Enter the Dungeon' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { CharacterForm, ValidationErrors } from '@/types'
import { validateForm } from '@/utils/validation'
import { formatInitPrompt } from '@/utils/promptFormatter'
import { useGameApi } from '@/composables/useGameApi'
import { useGameStore } from '@/stores/gameStore'
import { PARTY_LEADS } from '@/party'
import ServerHelp from '@/components/ServerHelp.vue'
import { LOCAL_NARRATOR_URL, normalizeServerUrl, friendlyConnectionError } from '@/utils/serverUrl'

const router = useRouter()
const route = useRoute()
const store = useGameStore()
const revealed = ref(false)

onMounted(() => {
  const reduceMotion =
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduceMotion) {
    revealed.value = true
    return
  }
  setTimeout(() => {
    revealed.value = true
  }, 1000)
})

// The party is set (workshop/world/cast.md): the player picks who they play as.
// Seed the address from a ?server= deep link first, then the saved address.
const queryServer = typeof route.query.server === 'string' ? route.query.server : ''
const form = reactive({
  name: PARTY_LEADS[0].name,
  serverUrl: normalizeServerUrl(queryServer || store.serverUrl || ''),
})

function useLocalServer() {
  form.serverUrl = LOCAL_NARRATOR_URL
}
const lead = computed(() => PARTY_LEADS.find(l => l.name === form.name) ?? PARTY_LEADS[0])
const characterForm = computed<CharacterForm>(() => ({
  name: lead.value.name,
  pronouns: lead.value.pronouns,
  species: lead.value.species,
  characterClass: lead.value.characterClass,
  serverUrl: form.serverUrl,
}))

const errors = ref<ValidationErrors>({})
const loading = ref(false)
const submitError = ref<string | null>(null)

async function handleSubmit() {
  const validationErrors = validateForm(characterForm.value)
  if (Object.keys(validationErrors).length > 0) {
    errors.value = validationErrors
    return
  }

  errors.value = {}
  submitError.value = null
  loading.value = true

  try {
    form.serverUrl = normalizeServerUrl(form.serverUrl)
    const prompt = formatInitPrompt(characterForm.value)
    const { sendInquiry } = useGameApi(form.serverUrl)
    await sendInquiry(prompt)
    store.setConnection(form.serverUrl, lead.value.name)

    // Roll the scroll closed, then navigate (instant under reduced motion)
    revealed.value = false
    const reduceMotion =
      typeof window !== 'undefined' &&
      typeof window.matchMedia === 'function' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (!reduceMotion) {
      await new Promise(resolve => setTimeout(resolve, 1500))
    }
    router.push({ name: 'game', params: { characterName: lead.value.name } })
  } catch (e) {
    submitError.value = friendlyConnectionError(e, 'Failed to connect to server')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.new-game-view {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 2rem 1rem;
}

.form-card {
  position: relative;
  width: 100%;
  max-width: 640px;
  padding: 2.5rem;
  background-color: var(--color-bg-card);
  background-image: var(--panel-scrim), var(--texture-parchment);
  background-size: cover;
  border: var(--border-panel);
  box-shadow: var(--shadow-raised);
  border-radius: var(--border-radius-panel);
}

/* --- Scroll unroll wrapper --- */
.scroll-wrapper {
  position: relative;
  width: 100%;
  max-width: 640px;
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
  font-size: var(--text-3xl);
  line-height: var(--leading-tight);
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
  border-color: var(--color-gold);
  box-shadow: var(--shadow-glow);
}

.form-input::placeholder {
  color: var(--color-ink-light);
  opacity: 1;
}

.field-help {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--color-ink-light);
}

.preset-button {
  align-self: flex-start;
  font-family: var(--font-ui);
  font-size: var(--text-sm);
  color: var(--color-ink);
  background: transparent;
  border: var(--border-panel);
  border-radius: var(--border-radius-chip);
  padding: 0.4rem 0.75rem;
  cursor: pointer;
}

.preset-button:hover {
  color: var(--color-gold-light);
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

.party-sheet {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem 1rem;
  margin: 0;
}

.party-sheet dt {
  font-family: var(--font-ui);
  font-weight: 600;
  font-size: 0.8rem;
  color: var(--color-ink-light);
}

.party-sheet dd {
  margin: 0;
  font-family: var(--font-body);
  color: var(--color-ink);
}

.companions {
  margin: 0;
  font-family: var(--font-body);
  font-size: 0.9rem;
  color: var(--color-ink-light);
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
  font-size: var(--text-sm);
  color: var(--color-ink);
  background-color: #4a1220;
  border: 1px solid var(--color-red-deep);
  padding: 0.75rem;
  border-radius: var(--border-radius-chip);
  text-align: left;
}

.submit-error__help {
  margin-top: 0.75rem;
}

@media (prefers-reduced-motion: reduce) {
  .scroll-wrapper .form-card {
    clip-path: inset(0 0 0 0);
  }
  .scroll-rod--top {
    top: -7px;
  }
  .scroll-rod--bottom {
    top: calc(100% - 7px);
  }
}
</style>
