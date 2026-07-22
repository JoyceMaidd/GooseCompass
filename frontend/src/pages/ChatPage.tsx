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
  const { messages, isLoading, sendMessage, startNewChat } = useChat()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="chat-page">
      <header className="chat-page__header">
        <div className="chat-page__brand">
          <h1 className="chat-page__title">GooseCompass</h1>
          <span className="chat-page__status">
            <span className="chat-page__status-dot" />
            Online
          </span>
        </div>
        <button className="chat-page__new-chat" onClick={startNewChat}>
          New Chat +
        </button>
      </header>

      <main className="chat-page__messages">
        {messages.length === 0 ? (
          <div className="chat-page__empty">
            <p className="chat-page__empty-title">Ask anything about your UWaterloo exchange</p>
            <p className="chat-page__empty-subtitle">
              Start your journey here
            </p>
          </div>
        ) : (
          <div className="chat-page__thread">
            {messages.map((message, idx) => (
              <ChatMessage key={idx} paragraphs={message.paragraphs} role={message.role} />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </main>

      <footer className="chat-page__footer">
        <ChatInput onSubmit={sendMessage} disabled={isLoading} />
        <p className="chat-page__disclaimer">
          GooseCompass may make mistakes. Please verify important information.
        </p>
      </footer>
    </div>
  )
}
