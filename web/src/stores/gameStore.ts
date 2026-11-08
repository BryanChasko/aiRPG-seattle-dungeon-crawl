import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { HypeSnapshot, SponsorDeal } from '../types'

const STORAGE_KEY = 'rpg-gm-server-url'

export const useGameStore = defineStore('game', () => {
  const serverUrl = ref(localStorage.getItem(STORAGE_KEY) ?? '')
  const characterName = ref('')
  // Floor 6 encounters: stay null until a Narrator that serves them answers
  const hype = ref<HypeSnapshot | null>(null)
  const pendingDeal = ref<SponsorDeal | null>(null)

  const isInitialized = computed(() => serverUrl.value !== '' && characterName.value !== '')

  function setConnection(url: string, name: string) {
    serverUrl.value = url
    characterName.value = name
    localStorage.setItem(STORAGE_KEY, url)
  }

  function setHype(snapshot: HypeSnapshot | null) {
    hype.value = snapshot
  }

  function setPendingDeal(deal: SponsorDeal | null) {
    pendingDeal.value = deal
  }

  function reset() {
    serverUrl.value = ''
    characterName.value = ''
    hype.value = null
    pendingDeal.value = null
    localStorage.removeItem(STORAGE_KEY)
  }

  return {
    serverUrl,
    characterName,
    hype,
    pendingDeal,
    isInitialized,
    setConnection,
    setHype,
    setPendingDeal,
    reset,
  }
})
