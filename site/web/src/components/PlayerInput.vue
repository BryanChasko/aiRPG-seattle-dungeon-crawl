<template>
  <form class="player-input" @submit.prevent="handleSubmit">
    <input
      id="player-action"
      v-model="message"
      name="action"
      type="text"
      aria-label="Type your action here"
      data-testid="player-action"
      class="player-input-field"
      placeholder="Tell the System AI what you do, Crawler..."
      :disabled="disabled"
    />
    <button type="submit" class="player-input-btn" :disabled="disabled">
      Do It
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  disabled: boolean
}>()

const emit = defineEmits<{
  submit: [message: string]
}>()

const message = ref('')

function handleSubmit() {
  const trimmed = message.value.trim()
  if (!trimmed) return
  emit('submit', trimmed)
  message.value = ''
}
</script>

<style scoped>
.player-input {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  background-color: #1a2030;
  padding: 0.75rem 1rem;
  border-radius: 12px;
}

.player-input-field {
  flex: 1;
  font-family: var(--font-body);
  font-size: 1rem;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--color-stroke);
  border-radius: 8px;
  background-color: var(--color-bg-card);
  color: var(--color-ink);
  transition: border-color 0.2s ease;
}

.player-input-field:focus {
  border-color: var(--color-gold);
}

.player-input-field::placeholder {
  color: #8a8399;
}

.player-input-field:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.player-input-btn {
  padding: 0.6rem 1.25rem;
  font-family: var(--font-ui);
  font-size: 1rem;
  color: #fff;
  background-color: var(--color-emerald-dark);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.player-input-btn:hover:not(:disabled) {
  background-color: #0b6b42;
}

.player-input-btn:active:not(:disabled) {
  background-color: #084f30;
}

.player-input-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
