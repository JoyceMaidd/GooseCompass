import { CitationBubble } from './CitationBubble'
import type { CitedParagraph } from '../types'

interface ChatMessageProps {
  paragraphs: CitedParagraph[]
  role: 'user' | 'assistant'
}

/**
 * Renders a single chat message with optional inline citations.
 *
 * For assistant messages, each paragraph is followed by a compact citation
 * bubble linking to its supporting sources. User messages render plain text only.
 *
 * @param props.paragraphs - Ordered list of paragraphs forming the message body.
 * @param props.role - Whether this message is from the user or the assistant.
 */
export function ChatMessage({ paragraphs, role }: ChatMessageProps) {
  return (
    <div className={`chat-message chat-message--${role}`}>
      {paragraphs.map((paragraph, pIdx) => {
        if (paragraph.text === '') return null
        return (
          <p key={pIdx} className="chat-message__paragraph">
            {paragraph.text}
            {role === 'assistant' && <CitationBubble citations={paragraph.citations} />}
          </p>
        )
      })}
    </div>
  )
}
