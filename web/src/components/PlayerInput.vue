<template>
  <form class="player-input" @submit.prevent="handleSubmit">
    <input
      v-model="message"
      type="text"
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
  border: 1px solid #3a3550;
  border-radius: 8px;
  background-color: var(--color-bg-card);
  color: var(--color-ink);
  transition: border-color 0.2s ease;
}

.player-input-field:focus {
  outline: none;
  border-color: #6c6585;
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
  background-color: #1fbf75;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.player-input-btn:hover:not(:disabled) {
  background-color: #18a865;
}

.player-input-btn:active:not(:disabled) {
  background-color: #128a52;
}

.player-input-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
