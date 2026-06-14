/** A single response paragraph with its supporting source URLs. */
export interface CitedParagraph {
  text: string
  citations: string[]
}

/** Structured LLM response with paragraph-level citations. */
export interface GeneratedResponse {
  paragraphs: CitedParagraph[]
  insufficient_context: boolean
}

/** A single message in the chat session. */
export interface Message {
  role: 'user' | 'assistant'
  paragraphs: CitedParagraph[]
}
