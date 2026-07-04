import { useState } from 'react'
import { queryStreaming } from '../api/client'
import type { Message } from '../types'

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
      (token) => {
        setMessages(prev => {
          const updated = [...prev]
          const last = updated[updated.length - 1]
          updated[updated.length - 1] = {
            ...last,
            paragraphs: [{ ...last.paragraphs[0], text: last.paragraphs[0].text + token }],
          }
          return updated
        })
      },
      (citations) => {
        setMessages(prev => {
          const updated = [...prev]
          const last = updated[updated.length - 1]
          updated[updated.length - 1] = {
            ...last,
            paragraphs: [{ ...last.paragraphs[0], citations }],
          }
          return updated
        })
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
