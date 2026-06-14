import type { GeneratedResponse } from '../types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

/**
 * Send a query and receive the full structured response in one shot.
 *
 * @param query - The user's natural-language question.
 * @returns The complete GeneratedResponse from the backend.
 */
export async function queryNonStreaming(query: string): Promise<GeneratedResponse> {
  const response = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}

/**
 * Send a query and stream the response token-by-token via SSE.
 *
 * Calls `onToken` for each arriving word and `onDone` once with the full
 * deduplicated citation list from the final SSE event.
 *
 * @param query - The user's natural-language question.
 * @param onToken - Called with each text token as it arrives.
 * @param onDone - Called once with all citation URLs when the stream ends.
 */
export async function queryStreaming(
  query: string,
  onToken: (token: string) => void,
  onDone: (citations: string[]) => void,
): Promise<void> {
  const response = await fetch(`${API_URL}/query/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  if (!response.body) throw new Error('No response body')

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''

    for (const part of parts) {
      const line = part.trim()
      if (!line.startsWith('data: ')) continue
      const event = JSON.parse(line.slice(6))
      if (event.type === 'token') onToken(event.text as string)
      else if (event.type === 'citations') onDone(event.citations as string[])
    }
  }
}
