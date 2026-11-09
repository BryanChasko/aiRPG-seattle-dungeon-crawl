<template>
  <div class="new-game-view">
    <div class="terminal" :class="{ 'terminal-revealed': revealed }">
      <div class="form-card paper-sheet">
        <h1 class="form-title">The Party Descends</h1>

        <form class="character-form" @submit.prevent="handleSubmit">
          <div v-if="submitError" class="submit-error" role="alert">
            <p>{{ submitError }}</p>
            <ServerHelp class="submit-error__help" />
          </div>

          <fieldset class="picker">
            <legend class="form-label" id="play-as-label">Play as</legend>
            <div class="party-grid" role="radiogroup" aria-labelledby="play-as-label">
              <label
                v-for="l in PARTY_LEADS"
                :key="l.name"
                class="party-option"
                :class="{ selected: form.name === l.name }"
              >
                <input
                  type="radio"
                  name="party-member"
                  class="party-radio"
                  :value="l.name"
                  v-model="form.name"
                />
                <img :src="`${baseUrl}${l.portrait}`" alt="" class="party-portrait" />
                <span class="party-name">{{ l.name }}: {{ l.shortSpecies }}</span>
                <span class="party-flavor">{{ l.flavor }}</span>
              </label>
            </div>
          </fieldset>

          <dl class="party-sheet" :key="lead.name">
            <div>
              <dt>Pronouns</dt>
              <dd id="lead-pronouns">{{ lead.pronouns }}</dd>
            </div>
            <div>
              <dt>Species</dt>
              <dd id="lead-species">{{ lead.species }}</dd>
            </div>
            <div>
              <dt>Class</dt>
              <dd id="lead-class">{{ lead.characterClass }}</dd>
            </div>
            <div>
              <dt>Role</dt>
              <dd id="lead-role">{{ lead.role }}</dd>
            </div>
          </dl>
          <p class="companions">Companions join the party on later floors.</p>

          <div class="form-group">
            <label for="server-url" class="form-label">Server URL</label>
            <p class="field-help" id="server-help">
              This page is a window. The game runs in the
              <strong>Narrator server you build in the workshop</strong> (Floor 6 starts it on this
              machine at <code>http://127.0.0.1:8009</code>). Paste that address here, or use the
              preset. No server yet?
              <a
                href="https://github.com/BryanChasko/seattle-strands-dungeon-crawl/blob/main/dungeon/workshop/floor-6.md"
                target="_blank"
                rel="noopener"
                >Build it on Floor 6</a
              >.
            </p>
            <input
              id="server-url"
              v-model="form.serverUrl"
              type="text"
              class="form-input"
              :class="{ 'input-error': errors.serverUrl }"
              placeholder="http://127.0.0.1:8009"
              aria-describedby="server-help"
            />
            <span v-if="errors.serverUrl" class="field-error">{{ errors.serverUrl }}</span>
            <button type="button" class="preset-button" @click="form.serverUrl = LOCAL_NARRATOR">
              Use my Floor 6 Narrator (127.0.0.1:8009)
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
import { normalizeServerUrl, friendlyConnectionError } from '@/utils/serverUrl'

const baseUrl = import.meta.env.BASE_URL
const LOCAL_NARRATOR = 'http://127.0.0.1:8009'

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
  }, 600)
})

// The party is set (workshop/world/cast.md): the player picks who they play as.
// Seed the address from a ?server= deep link first, then the saved address.
const queryServer = typeof route.query.server === 'string' ? route.query.server : ''
const form = reactive({
  name: PARTY_LEADS[0].name,
  serverUrl: normalizeServerUrl(queryServer || store.serverUrl || LOCAL_NARRATOR),
})
const lead = computed(() => PARTY_LEADS.find((l) => l.name === form.name) ?? PARTY_LEADS[0])
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
      await new Promise((resolve) => setTimeout(resolve, 1500))
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
  min-height: 100vh;
  padding: 1.5rem 1rem 2.5rem;
}

/* Pip-Boy terminal frame: scanlines and a phosphor boot sweep over the house obsidian card */
.terminal {
  position: relative;
  width: 100%;
  max-width: 640px;
  opacity: 0.35;
  transition: opacity 0.5s ease;
}
.terminal-revealed {
  opacity: 1;
}
.terminal::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    0deg,
    rgba(232, 226, 240, 0.045) 0 1px,
    transparent 1px 3px
  );
  border-radius: 4px;
}
.terminal::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 3px;
  background: var(--color-emerald);
  opacity: 0;
  z-index: 2;
}
.terminal-revealed::before {
  animation: bootSweep 0.7s ease-out 1;
}
@keyframes bootSweep {
  0% {
    top: 0;
    opacity: 0.9;
  }
  100% {
    top: 100%;
    opacity: 0;
  }
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

.form-title {
  font-family: var(--font-heading);
  color: var(--color-red-deep);
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 2rem;
}

.character-form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}
.form-label {
  font-family: var(--font-ui);
  font-weight: 600;
  color: var(--color-ink-light);
  font-size: 0.95rem;
}

.picker {
  border: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.party-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.party-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  text-align: center;
  cursor: pointer;
  padding: 0.75rem 0.5rem 0.6rem;
  border: 2px solid var(--color-parchment-dark);
  border-radius: 6px;
  background: rgba(11, 14, 20, 0.55);
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease;
}
.party-option.selected {
  border-color: var(--color-emerald);
  box-shadow:
    0 0 10px rgba(31, 191, 117, 0.45),
    inset 0 0 18px rgba(31, 191, 117, 0.12);
}
.party-option:focus-within {
  outline: 2px solid var(--color-gold);
  outline-offset: 2px;
}
.party-radio {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}
.party-portrait {
  height: 178px;
  max-width: 100%;
  object-fit: contain;
}
.party-name {
  font-family: var(--font-heading);
  color: var(--color-ink);
  font-size: 1.05rem;
}
.party-flavor {
  font-family: var(--font-body);
  color: var(--color-ink-light);
  font-size: 0.85rem;
  line-height: 1.35;
}

.party-sheet {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem 1rem;
  margin: 0;
  animation: sheetIn 0.35s ease-out 1;
}
@keyframes sheetIn {
  0% {
    opacity: 0.2;
  }
  40% {
    opacity: 1;
  }
  60% {
    opacity: 0.55;
  }
  100% {
    opacity: 1;
  }
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
.companion {
  white-space: nowrap;
}
.companion-face {
  width: 26px;
  height: 26px;
  object-fit: cover;
  border-radius: 4px;
  vertical-align: middle;
  margin: 0 0.3rem 0 0.15rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.field-help {
  margin: 0;
  font-family: var(--font-body);
  font-size: 0.88rem;
  color: var(--color-ink-light);
  line-height: 1.45;
}
.field-help a {
  color: var(--color-gold-light);
}
.field-help code {
  color: var(--color-ink);
}
.form-input {
  font-family: var(--font-body);
  font-size: 1rem;
  padding: 0.6rem 0.75rem;
  border: 2px solid var(--color-parchment-dark);
  border-radius: 4px;
  background-color: var(--color-parchment);
  color: var(--color-ink);
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
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
  margin-top: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-family: var(--font-heading);
  font-size: 1.25rem;
  color: var(--color-gold-light);
  background-color: var(--color-wood-medium);
  border: var(--border-gold);
  border-radius: var(--border-radius-panel);
  cursor: pointer;
  box-shadow: var(--shadow-panel);
  transition:
    background-color 0.2s ease,
    box-shadow 0.2s ease;
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

@media (prefers-reduced-motion: reduce) {
  .terminal {
    transition: none;
  }
  .terminal::before {
    display: none;
  }
  .party-sheet {
    animation: none;
  }
  .party-option,
  .form-input,
  .start-button {
    transition: none;
  }
}
</style>
