/** A single structured citation supporting a paragraph's claims. */
export interface Citation {
  id: string
  title: string
  url?: string
  snippet?: string
  source_type?: string
}

/** A single response paragraph with its supporting citations. */
export interface CitedParagraph {
  text: string
  citations: Citation[]
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
