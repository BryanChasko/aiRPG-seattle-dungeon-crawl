<template>
  <div v-if="deal" class="sponsor-deal" role="alertdialog" aria-labelledby="sponsor-deal-title" aria-describedby="sponsor-deal-offer">
    <h3 id="sponsor-deal-title" class="sponsor-deal__title">{{ deal.sponsor }} wants a word</h3>
    <p id="sponsor-deal-offer" class="sponsor-deal__offer">{{ deal.offer }}</p>
    <p v-if="deal.reward" class="sponsor-deal__line"><span class="sponsor-deal__tag">YOU GET:</span> {{ deal.reward }}</p>
    <p v-if="deal.cost" class="sponsor-deal__line"><span class="sponsor-deal__tag">YOU OWE:</span> {{ deal.cost }}</p>
    <div class="sponsor-deal__buttons">
      <button type="button" class="sponsor-deal__btn sponsor-deal__btn--accept" :disabled="disabled" @click="emit('accept')">
        Accept the deal
      </button>
      <button type="button" class="sponsor-deal__btn sponsor-deal__btn--refuse" :disabled="disabled" @click="emit('refuse')">
        Refuse the deal
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SponsorDeal } from '../types'

defineProps<{
  deal: SponsorDeal | null
  disabled?: boolean
}>()

const emit = defineEmits<{
  accept: []
  refuse: []
}>()
</script>

<style scoped>
.sponsor-deal {
  font-family: var(--font-ui);
  color: var(--color-ink);
  background-color: var(--color-bg-card);
  border: 2px solid #e67e22;
  border-radius: 8px;
  padding: 0.75rem 1rem;
}

.sponsor-deal__title {
  margin: 0 0 0.5rem;
  font-size: 1rem;
}

.sponsor-deal__offer,
.sponsor-deal__line {
  margin: 0.25rem 0;
}

.sponsor-deal__tag {
  font-weight: 700;
  letter-spacing: 0.05em;
}

.sponsor-deal__buttons {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.sponsor-deal__btn {
  font-family: var(--font-ui);
  padding: 0.5rem 1rem;
  color: var(--color-ink);
  background-color: #1a2030;
  border: 1px solid #6c6585;
  border-radius: 1rem;
  cursor: pointer;
}

.sponsor-deal__btn:hover:not(:disabled) {
  border-color: #e67e22;
}

.sponsor-deal__btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
