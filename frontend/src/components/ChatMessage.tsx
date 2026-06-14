import type { CitedParagraph } from '../types'

interface ChatMessageProps {
  paragraphs: CitedParagraph[]
  role: 'user' | 'assistant'
}

/**
 * Renders a single chat message with optional inline citations.
 *
 * For assistant messages, each paragraph is followed by superscript citation
 * links pointing to the source URLs. User messages render plain text only.
 *
 * @param props.paragraphs - Ordered list of paragraphs forming the message body.
 * @param props.role - Whether this message is from the user or the assistant.
 */
export function ChatMessage({ paragraphs, role }: ChatMessageProps) {
  return (
    <div className={`chat-message chat-message--${role}`}>
      {paragraphs.map((paragraph, pIdx) => (
        <p key={pIdx} className="chat-message__paragraph">
          {paragraph.text}
          {role === 'assistant' &&
            paragraph.citations.map((url, cIdx) => (
              <sup key={url} className="chat-message__citation">
                <a href={url} target="_blank" rel="noopener noreferrer">
                  [{pIdx * paragraph.citations.length + cIdx + 1}]
                </a>
              </sup>
            ))}
        </p>
      ))}
    </div>
  )
}
