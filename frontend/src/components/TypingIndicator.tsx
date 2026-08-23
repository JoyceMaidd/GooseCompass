/**
 * Animated three-dot bubble shown while waiting for the assistant's first
 * streamed token, styled to match the assistant chat bubble.
 */
export function TypingIndicator() {
  return (
    <div
      className="chat-message chat-message--assistant chat-message--typing"
      role="status"
      aria-label="GooseCompass is typing"
    >
      <span className="typing-indicator__dot" />
      <span className="typing-indicator__dot" />
      <span className="typing-indicator__dot" />
    </div>
  )
}
