<template>
  <section class="server-help panel-glass" aria-labelledby="server-help-title">
    <h2 id="server-help-title" class="server-help__title">No server yet? Start the four terminals</h2>
    <p class="server-help__intro">
      This page is a window. The game itself runs in the server you build in the workshop:
      four terminals, four processes. This page only talks to the last one, on port 8009.
    </p>
    <table class="server-help__table">
      <caption class="visually-hidden">The four workshop servers and their ports</caption>
      <thead>
        <tr><th scope="col">Terminal</th><th scope="col">Process</th><th scope="col">Port</th></tr>
      </thead>
      <tbody>
        <tr><td>1</td><td>Rules Agent (rules)</td><td><code>8000</code></td></tr>
        <tr><td>2</td><td>Character Agent (registry)</td><td><code>8001</code></td></tr>
        <tr><td>3</td><td>Dice server (dice)</td><td><code>8002</code></td></tr>
        <tr><td>4</td><td>The game server this page calls (the Narrator job)</td><td><code>8009</code></td></tr>
      </tbody>
    </table>
    <p class="server-help__note">
      Server URL for a local game: <code>http://127.0.0.1:8009</code>, exactly as the fourth
      terminal prints it, with no path after the port. If the browser asks for local network
      permission, allow it.
    </p>
    <ul class="server-help__links">
      <li><a :href="REPO_URL" target="_blank" rel="noopener">The project on GitHub</a></li>
      <li><a :href="FLOOR5_URL" target="_blank" rel="noopener">Floor 5, Part 4: launch all four servers</a></li>
      <li><a :href="FLOOR6_URL" target="_blank" rel="noopener">Floor 6: connect this page to your server</a></li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import { REPO_URL, FLOOR5_URL, FLOOR6_URL } from '@/links'
</script>

<style scoped>
.server-help {
  text-align: left;
  padding: 1rem 1.25rem;
  border-radius: var(--border-radius-panel);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  line-height: 1.55;
}
.server-help__title {
  font-family: var(--font-ui);
  font-size: var(--text-base);
  color: var(--color-ink);
  margin-bottom: 0.4rem;
}
.server-help__intro,
.server-help__note {
  color: var(--color-ink-light);
}
.server-help__table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.6rem 0;
}
.server-help__table th,
.server-help__table td {
  text-align: left;
  padding: 0.3rem 0.5rem;
  border-bottom: 1px solid var(--color-stroke);
  color: var(--color-ink);
}
.server-help__links {
  margin: 0.6rem 0 0;
  padding-left: 1.1rem;
}
.server-help__links a {
  color: var(--color-gold-light);
}
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
}
</style>
