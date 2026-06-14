import { useEffect, useRef } from 'react'
import { ChatInput } from '../components/ChatInput'
import { ChatMessage } from '../components/ChatMessage'
import { useChat } from '../hooks/useChat'

/**
 * Main chat page — composes the chat hook, message list, and input field.
 *
 * Automatically scrolls to the bottom whenever the message list grows or the
 * last assistant message receives new tokens.
 */
export function ChatPage() {
  const { messages, isLoading, sendMessage } = useChat()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="chat-page">
      <header className="chat-page__header">
        <h1>GooseCompass</h1>
        <p>Ask anything about your UWaterloo outbound exchange.</p>
      </header>

      <main className="chat-page__messages">
        {messages.map((message, idx) => (
          <ChatMessage key={idx} paragraphs={message.paragraphs} role={message.role} />
        ))}
        <div ref={bottomRef} />
      </main>

      <footer className="chat-page__input">
        <ChatInput onSubmit={sendMessage} disabled={isLoading} />
      </footer>
    </div>
  )
}
