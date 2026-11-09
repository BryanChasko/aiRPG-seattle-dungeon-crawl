import type {
  ContentBlock,
  RawMessage,
  ParsedMessage,
  StoryOutput,
  TextContent,
  ToolUseContent,
} from "../types";
import { INIT_PROMPT_PREFIX, RETRY_PROMPT_PREFIX } from "./promptFormatter";

function isTextContent(block: ContentBlock): block is TextContent {
  return "text" in block;
}

function isToolUseContent(block: ContentBlock): block is ToolUseContent {
  return "toolUse" in block;
}

export function parseMessages(rawMessages: RawMessage[]): ParsedMessage[] {
  const result: ParsedMessage[] = [];
  // After a hidden retry prompt the Narrator restates the same scene; keep only the last answer
  let retrying = false;

  for (const msg of rawMessages) {
    if (msg.role === "user") {
      const text = msg.content
        .filter(isTextContent)
        .map((block) => block.text)
        .join("");

      if (text.startsWith(RETRY_PROMPT_PREFIX)) {
        retrying = true;
      } else if (text && !text.startsWith(INIT_PROMPT_PREFIX)) {
        retrying = false;
        result.push({ role: "user", text });
      }
    } else if (msg.role === "assistant") {
      const storyBlock = msg.content
        .filter(isToolUseContent)
        .find((block) => block.toolUse.name === "StoryOutput");

      if (storyBlock) {
        const entry: ParsedMessage = {
          role: "assistant",
          storyOutput: storyBlock.toolUse.input as unknown as StoryOutput,
        };
        if (
          retrying &&
          result.length > 0 &&
          result[result.length - 1].role === "assistant"
        ) {
          result[result.length - 1] = entry;
        } else {
          result.push(entry);
        }
      }
    }
  }

  return result;
}
