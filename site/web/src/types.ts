// ---- Form Data ----

export interface CharacterForm {
  name: string
  pronouns: 'she/her' | 'he/him' | 'they/them' | 'any pronouns'
  species:
    | 'Human (Seattle Native)'
    | 'Human (Transplant)'
    | 'Uplifted Giant Pacific Octopus'
    | 'Uplifted Crow'
    | 'Harbor Seal'
    | 'Sea Otter'
    | 'Banana Slug'
    | 'Fremont Troll-kin'
    | 'Underground Ghost'
  characterClass:
    | 'Amphibious Breacher'
    | 'Benthic Dragoon'
    | 'Kayak Patrol Ranger'
    | 'Ferry Engineer'
    | 'Ballard Brewer'
    | 'Fish-Toss Striker'
    | 'Grunge Bard'
    | 'Coffee Alchemist'
    | 'Salvage Artificer'
    | 'Rain Warden'
    | 'Floating-Bridge Engineer'
    | 'Startup Necromancer'
  serverUrl: string
}

// ---- Validation ----

export interface ValidationErrors {
  name?: string
  pronouns?: string
  species?: string
  characterClass?: string
  serverUrl?: string
}

// ---- Raw API types (from GET /messages) ----

export interface TextContent {
  text: string
}

export interface ToolUseContent {
  toolUse: {
    toolUseId: string
    name: string
    input: Record<string, unknown>
  }
}

export interface ToolResultContent {
  toolResult: {
    toolUseId: string
    status: string
    content: TextContent[]
  }
}

export type ContentBlock = TextContent | ToolUseContent | ToolResultContent

export interface RawMessage {
  role: 'user' | 'assistant'
  content: ContentBlock[]
}

// ---- Parsed / display-ready types ----

export interface DiceRoll {
  dice_type: string
  result: string
  reason: string
}

export interface StoryOutput {
  response: string
  actions_suggestions: string[]
  details: string
  dice_rolls: DiceRoll[]
}

export interface ParsedMessage {
  role: 'user' | 'assistant'
  text?: string
  storyOutput?: StoryOutput
}

// ---- Character Stats ----

export interface AbilityScores {
  strength: number
  dexterity: number
  constitution: number
  intelligence: number
  wisdom: number
  charisma: number
}

export interface InventoryItem {
  item_name: string
  quantity: number
}

export interface CharacterStats {
  character_id: string
  name: string
  character_class: string
  species: string
  pronouns: string
  level: number
  experience: number
  stats: AbilityScores
  derived?: { groove: number; mana: number }
  inventory: InventoryItem[]
  created_at: string
}

// ---- Floor 6 encounters (optional: only a Narrator that serves them sends these) ----

/** GET /hype from The Hype Meter side passage. */
export interface HypeSnapshot {
  hype: number
  sponsor_tiers: number[]
  next_sponsor_at: number | null
  last_event: string
}

/** The interrupt a Sponsor Interrupt Narrator returns from POST /inquire and POST /respond. */
export interface SponsorDeal {
  id: string
  name: string
  sponsor: string
  offer: string
  reward: string
  cost: string
}

export interface InquiryResult {
  story: StoryOutput
  deal: SponsorDeal | null
}

// ---- Inquiry Request / Response ----

export interface InquiryRequest {
  question: string
}

export interface InquiryResponse {
  response: StoryOutput
}
