<template>
  <div v-if="hype" class="hype-meter panel-parchment border-gold" role="status" aria-label="Hype meter">
    <div class="hype-row">
      <span class="hype-label">HYPE</span>
      <span class="hype-value">{{ hype.hype }}</span>
    </div>
    <div
      class="hype-bar"
      role="progressbar"
      aria-label="Progress to the next sponsor box"
      :aria-valuenow="percent"
      aria-valuemin="0"
      aria-valuemax="100"
    >
      <div class="hype-bar__fill" :style="{ width: percent + '%' }"></div>
    </div>
    <div class="hype-next">{{ nextText }}</div>
    <div v-if="hype.last_event" class="hype-event">{{ hype.last_event }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { HypeSnapshot } from '../types'

const props = defineProps<{
  hype: HypeSnapshot | null
}>()

const percent = computed(() => {
  const h = props.hype
  if (!h) return 0
  if (h.next_sponsor_at === null) return 100
  return Math.max(0, Math.min(100, Math.round((h.hype / h.next_sponsor_at) * 100)))
})

const nextText = computed(() => {
  const h = props.hype
  if (!h) return ''
  if (h.next_sponsor_at === null) return 'Every sponsor box has been sent'
  return `Next sponsor box at ${h.next_sponsor_at} Hype`
})
</script>

<style scoped>
.hype-meter {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  font-family: var(--font-ui);
  color: var(--color-ink);
}

.hype-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.hype-label {
  letter-spacing: 0.08em;
  font-size: 0.8rem;
}

.hype-value {
  font-size: 1.6rem;
  font-weight: 900;
}

.hype-bar {
  height: 8px;
  margin: 0.4rem 0;
  background-color: #1a2030;
  border: 1px solid var(--color-stroke);
  border-radius: 4px;
  overflow: hidden;
}

.hype-bar__fill {
  height: 100%;
  background-color: #e67e22;
  transition: width 0.4s ease;
}

.hype-next,
.hype-event {
  font-size: 0.8rem;
  color: var(--color-ink-light);
}

.hype-event {
  margin-top: 0.25rem;
  font-style: italic;
}
</style>
