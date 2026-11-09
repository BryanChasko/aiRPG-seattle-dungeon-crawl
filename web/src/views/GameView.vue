<template>
  <div class="game-view">
    <aside class="game-view__sidebar">
      <CharacterStatsPanel
        :stats="stats"
        :loading="statsLoading"
        :error="statsError"
      />
      <HypeMeter :hype="store.hype" />
    </aside>

    <main class="game-view__main">
      <MessageList
        :messages="messages"
        :loading="messagesLoading"
        :error="messagesError"
        :typing="sending"
      />

      <div v-if="sendError" class="game-view__send-error">
        {{ sendError }}
      </div>

      <SponsorDealDialog
        :deal="store.pendingDeal"
        :disabled="sending"
        @accept="handleDeal(true)"
        @refuse="handleDeal(false)"
      />

      <ActionSuggestions
        v-if="!sending && !store.pendingDeal"
        :suggestions="latestSuggestions"
        :disabled="sending"
        @select="handleAction"
      />

      <PlayerInput
        :disabled="sending || !!store.pendingDeal"
        @submit="handleAction"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useGameStore } from '@/stores/gameStore'
import { useGameApi } from '@/composables/useGameApi'
import CharacterStatsPanel from '@/components/CharacterStatsPanel.vue'
import MessageList from '@/components/MessageList.vue'
import ActionSuggestions from '@/components/ActionSuggestions.vue'
import PlayerInput from '@/components/PlayerInput.vue'
import HypeMeter from '@/components/HypeMeter.vue'
import SponsorDealDialog from '@/components/SponsorDealDialog.vue'
import type { CharacterStats, ParsedMessage } from '@/types'

const route = useRoute()
const store = useGameStore()

const stats = ref<CharacterStats | null>(null)
const statsLoading = ref(false)
const statsError = ref<string | null>(null)

const messages = ref<ParsedMessage[]>([])
const messagesLoading = ref(false)
const messagesError = ref<string | null>(null)

const sending = ref(false)
const sendError = ref<string | null>(null)

const latestSuggestions = computed<string[]>(() => {
  for (let i = messages.value.length - 1; i >= 0; i--) {
    const msg = messages.value[i]
    if (msg.role === 'assistant' && msg.storyOutput?.actions_suggestions?.length) {
      return msg.storyOutput.actions_suggestions
    }
  }
  return []
})

async function handleAction(text: string) {
  const api = useGameApi(store.serverUrl)
  sending.value = true
  sendError.value = null
  // Show user message immediately
  messages.value = [...messages.value, { role: 'user', text }]
  try {
    const { story, deal } = await api.sendInquiryWithDeal(text)
    messages.value = [...messages.value, { role: 'assistant', storyOutput: story }]
    store.setPendingDeal(deal)
  } catch (e) {
    sendError.value = e instanceof Error ? e.message : 'Failed to send message'
  } finally {
    sending.value = false
  }
  await Promise.all([refreshHype(), refreshStats()])
}

// Only reachable when the Narrator paused the turn on a sponsor deal (Sponsor Interrupt)
async function handleDeal(accepted: boolean) {
  const deal = store.pendingDeal
  if (!deal) return
  const api = useGameApi(store.serverUrl)
  sending.value = true
  sendError.value = null
  try {
    const { story, deal: nextDeal } = await api.respondToDeal(deal.id, accepted)
    messages.value = [...messages.value, { role: 'assistant', storyOutput: story }]
    store.setPendingDeal(nextDeal)
  } catch (e) {
    sendError.value = e instanceof Error ? e.message : 'Failed to answer the sponsor'
  } finally {
    sending.value = false
  }
  await Promise.all([refreshHype(), refreshStats()])
}

// Only reachable with a Hype Meter Narrator; a plain Narrator answers null and the panel stays hidden
async function refreshHype() {
  const api = useGameApi(store.serverUrl)
  store.setHype(await api.fetchHype())
}

// Groove, mana and xp change during a turn: re-read them quietly (no loading flash, keep the old card on error)
async function refreshStats() {
  const characterName = route.params.characterName as string
  if (!characterName) return
  try {
    stats.value = await useGameApi(store.serverUrl).fetchUser(characterName)
  } catch {
    // keep the last good stats
  }
}

onMounted(async () => {
  const characterName = route.params.characterName as string
  const api = useGameApi(store.serverUrl)

  statsLoading.value = true
  try {
    stats.value = await api.fetchUser(characterName)
  } catch (e) {
    statsError.value = e instanceof Error ? e.message : 'Failed to load character stats'
  } finally {
    statsLoading.value = false
  }

  messagesLoading.value = true
  try {
    messages.value = await api.fetchMessages()
  } catch (e) {
    messagesError.value = e instanceof Error ? e.message : 'Failed to load message history'
  } finally {
    messagesLoading.value = false
  }

  await refreshHype()
})
</script>

<style scoped>
.game-view {
  display: flex;
  gap: 2rem;
  padding: 1rem;
  min-height: 100vh;
  align-items: flex-start;
  background-color: var(--color-bg-page);
}

.game-view__sidebar {
  flex: 0 0 260px;
  position: sticky;
  top: 1rem;
}

.game-view__main {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 0;
  background-color: #161b26;
  background-image: url('/textures/obsidian-512x512.webp');
  background-size: cover;
  border: 1px solid #3a3550;
  border-radius: 4px;
  padding: 1rem;
  box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.08);
  z-index: 1;
}

/* Stacked paper sheets behind the main area */
.game-view__main::before,
.game-view__main::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #161b26;
  background-image: url('/textures/obsidian-512x512.webp');
  background-size: cover;
  border: 1px solid #3a3550;
  border-radius: 4px;
  z-index: -1;
}

.game-view__main::before {
  transform: rotate(0.8deg);
  box-shadow: 1px 2px 4px rgba(0, 0, 0, 0.06);
}

.game-view__main::after {
  background-color: #1a2030;
  background-image: url('/textures/obsidian-512x512.webp');
  background-size: cover;
  box-shadow: 1px 2px 4px rgba(0, 0, 0, 0.04);
}

.game-view__send-error {
  font-family: var(--font-body);
  color: var(--color-red-accent);
  background-color: rgba(183, 28, 28, 0.08);
  border: 1px solid var(--color-red-accent);
  border-radius: 8px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .game-view {
    flex-direction: column;
  }

  .game-view__sidebar {
    flex: none;
    width: 100%;
    position: static;
  }
}
</style>
