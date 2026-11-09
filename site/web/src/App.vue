<template>
  <div class="site">
    <header class="site-header panel-glass">
      <RouterLink class="site-header__brand" to="/">aiRPG Seattle Dungeon Crawl</RouterLink>
      <nav class="site-header__nav" aria-label="Site">
        <RouterLink to="/">Play</RouterLink>
        <a :href="REPO_URL" target="_blank" rel="noopener">GitHub</a>
        <a :href="WORKSHOP_URL" target="_blank" rel="noopener">Workshop</a>
        <a :href="FLOOR5_URL" target="_blank" rel="noopener">Floor 5 servers</a>
        <a :href="FLOOR6_URL" target="_blank" rel="noopener">Floor 6: play in the browser</a>
        <button
          v-if="store.isInitialized"
          type="button"
          class="site-header__leave"
          @click="leaveDungeon"
        >
          Leave the dungeon
        </button>
      </nav>
    </header>

    <RouterView />

    <footer class="site-footer">
      <p>
        One System AI runs this crawl; conflict is dance-offs and nobody is hurt.
        Built floor by floor in the open.
      </p>
      <nav class="site-footer__nav" aria-label="Footer">
        <a :href="REPO_URL" target="_blank" rel="noopener">Source on GitHub</a>
        <a :href="WORKSHOP_URL" target="_blank" rel="noopener">The workshop</a>
        <a :href="FLOOR5_URL" target="_blank" rel="noopener">Floor 5: start the four servers</a>
        <a :href="FLOOR6_URL" target="_blank" rel="noopener">Floor 6: connect this page</a>
      </nav>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { RouterView, RouterLink, useRouter } from 'vue-router'
import { REPO_URL, WORKSHOP_URL, FLOOR5_URL, FLOOR6_URL } from '@/links'
import { useGameStore } from '@/stores/gameStore'

const store = useGameStore()
const router = useRouter()

function leaveDungeon() {
  store.reset()
  router.push('/')
}
</script>

<style scoped>
.site {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.site-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 1.25rem;
  padding: 0.65rem 1rem;
  margin-top: 0.75rem;
  border-radius: var(--border-radius-panel);
  position: relative;
  z-index: 5;
}
.site-header__brand {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  line-height: var(--leading-tight);
  color: var(--color-ink);
  text-decoration: none;
}
.site-header__nav,
.site-footer__nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 1rem;
  align-items: center;
  font-family: var(--font-ui);
  font-size: var(--text-sm);
}
.site-header__leave {
  font-family: var(--font-ui);
  font-size: var(--text-sm);
  color: var(--color-ink);
  background: transparent;
  border: var(--border-panel);
  border-radius: var(--border-radius-chip);
  padding: 0.3rem 0.7rem;
  cursor: pointer;
}
.site-header__leave:hover {
  color: var(--color-gold-light);
}
.site-footer {
  margin-top: auto;
  padding: 1.25rem 0.25rem 1.5rem;
  color: var(--color-ink-light);
  font-size: var(--text-sm);
}
.site-footer__nav {
  margin-top: 0.4rem;
}
</style>
