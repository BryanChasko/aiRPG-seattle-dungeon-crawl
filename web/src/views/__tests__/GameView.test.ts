import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import GameView from "../GameView.vue";

vi.mock("vue-router", () => ({
  useRoute: () => ({ params: { characterName: "Cordula Vance" } }),
}));

function statsWithGroove(groove: number) {
  return {
    name: "Cordula Vance",
    pronouns: "she/her",
    species: "Human (Seattle Native)",
    character_class: "Amphibious Breacher",
    level: 1,
    experience: 0,
    stats: {
      strength: 16,
      dexterity: 13,
      constitution: 16,
      intelligence: 12,
      wisdom: 14,
      charisma: 10,
    },
    derived: { groove, mana: 8 },
  };
}

describe("GameView HUD refresh", () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    setActivePinia(createPinia());
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it("re-reads the character after a turn so Groove is not stale", async () => {
    let userCalls = 0;
    globalThis.fetch = vi.fn(async (url: string) => {
      const u = String(url);
      if (u.includes("/user/")) {
        userCalls += 1;
        return {
          ok: true,
          status: 200,
          json: async () => statsWithGroove(userCalls === 1 ? 17 : 15),
        };
      }
      if (u.endsWith("/messages"))
        return { ok: true, status: 200, json: async () => [] };
      if (u.endsWith("/inquire")) {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            response: {
              response: "Groove dropped.",
              actions_suggestions: [],
              details: "",
              dice_rolls: [],
            },
          }),
        };
      }
      return { ok: false, status: 404, json: async () => ({}) };
    }) as unknown as typeof fetch;

    const wrapper = mount(GameView, { global: { plugins: [createPinia()] } });
    await flushPromises();
    expect(wrapper.text()).toContain("17");

    await wrapper.find("input").setValue("Start a dance-off");
    await wrapper.find("form").trigger("submit");
    await flushPromises();

    expect(userCalls).toBe(2);
    const groove = wrapper
      .findAll(".stat-row")
      .find((r) => r.text().includes("GROOVE"));
    expect(groove?.text()).toContain("15");
  });
});
