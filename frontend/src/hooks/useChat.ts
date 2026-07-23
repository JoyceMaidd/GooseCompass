import { useState } from 'react'
import { queryStreaming } from '../api/client'
import type { Citation, Message } from '../types'

/**
 * Append a text token to the last paragraph of the most recent message.
 *
 * @param prev - Current message list.
 * @param token - Text fragment to append.
 * @returns A new message list with the token appended.
 */
function appendToken(prev: Message[], token: string): Message[] {
  const updated = [...prev]
  const last = updated[updated.length - 1]
  const paragraphs = [...last.paragraphs]
  const i = paragraphs.length - 1
  paragraphs[i] = { ...paragraphs[i], text: paragraphs[i].text + token }
  updated[updated.length - 1] = { ...last, paragraphs }
  return updated
}

/**
 * Finalize the last paragraph's citations and open a fresh empty paragraph
 * to receive tokens for the next section of the answer.
 *
 * @param prev - Current message list.
 * @param citations - Citations for the paragraph that just finished.
 * @returns A new message list with citations set and a new empty paragraph appended.
 */
function finalizeParagraph(prev: Message[], citations: Citation[]): Message[] {
  const updated = [...prev]
  const last = updated[updated.length - 1]
  const paragraphs = [...last.paragraphs]
  const i = paragraphs.length - 1
  paragraphs[i] = { ...paragraphs[i], citations }
  paragraphs.push({ text: '', citations: [] })
  updated[updated.length - 1] = { ...last, paragraphs }
  return updated
}

/**
 * Drop a trailing empty paragraph left over from anticipatory appending.
 *
 * @param prev - Current message list.
 * @returns A new message list with any dangling empty trailing paragraph removed.
 */
function trimTrailingEmptyParagraph(prev: Message[]): Message[] {
  const updated = [...prev]
  const last = updated[updated.length - 1]
  const paragraphs = [...last.paragraphs]
  const tail = paragraphs[paragraphs.length - 1]
  if (paragraphs.length > 1 && tail.text === '' && tail.citations.length === 0) {
    paragraphs.pop()
  }
  updated[updated.length - 1] = { ...last, paragraphs }
  return updated
}

/**
 * Manages chat session state and streaming message delivery.
 *
 * @returns messages - Full chat history for this session.
 * @returns isLoading - True while a streaming response is in flight.
 * @returns sendMessage - Submit a query; streams the assistant reply token by token.
 * @returns startNewChat - Clears the session, discarding all messages.
 */
export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)

  function sendMessage(query: string) {
    setMessages(prev => [
      ...prev,
      { role: 'user', paragraphs: [{ text: query, citations: [] }] },
      { role: 'assistant', paragraphs: [{ text: '', citations: [] }] },
    ])
    setIsLoading(true)

    void queryStreaming(
      query,
      (token) => setMessages(prev => appendToken(prev, token)),
      (citations) => setMessages(prev => finalizeParagraph(prev, citations)),
      () => {
        setMessages(prev => trimTrailingEmptyParagraph(prev))
        setIsLoading(false)
      },
    ).catch(() => {
      setIsLoading(false)
    })
  }

  function startNewChat() {
    setMessages([])
    setIsLoading(false)
  }

  return { messages, isLoading, sendMessage, startNewChat }
}
