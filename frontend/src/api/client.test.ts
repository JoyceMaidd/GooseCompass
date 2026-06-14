import { describe, it, expect, vi, beforeEach } from 'vitest'
import { queryNonStreaming, queryStreaming } from './client'

const MOCK_RESPONSE = {
  paragraphs: [{ text: 'You need a 70% GPA.', citations: ['https://uwaterloo.ca/gpa'] }],
  insufficient_context: false,
}

const SSE_EVENTS = [
  'data: {"type":"token","text":"You "}\n\n',
  'data: {"type":"token","text":"need "}\n\n',
  'data: {"type":"token","text":"70%"}\n\n',
  'data: {"type":"citations","citations":["https://uwaterloo.ca/gpa"]}\n\n',
].join('')

function makeStreamResponse(sseData: string): Response {
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(new TextEncoder().encode(sseData))
      controller.close()
    },
  })
  return { ok: true, body: stream, json: () => Promise.resolve(MOCK_RESPONSE) } as unknown as Response
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('queryNonStreaming', () => {
  it('calls /query and returns parsed JSON', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE),
    })
    vi.stubGlobal('fetch', mockFetch)

    const result = await queryNonStreaming('What GPA do I need?')

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/query'),
      expect.objectContaining({ method: 'POST' }),
    )
    expect(result).toEqual(MOCK_RESPONSE)
  })

  it('throws on non-ok response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 500 }))
    await expect(queryNonStreaming('test')).rejects.toThrow('HTTP 500')
  })
})

describe('queryStreaming', () => {
  it('calls onToken for each token event', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(makeStreamResponse(SSE_EVENTS)))
    const onToken = vi.fn()
    const onDone = vi.fn()

    await queryStreaming('What GPA?', onToken, onDone)

    expect(onToken).toHaveBeenCalledTimes(3)
    expect(onToken).toHaveBeenNthCalledWith(1, 'You ')
    expect(onToken).toHaveBeenNthCalledWith(2, 'need ')
    expect(onToken).toHaveBeenNthCalledWith(3, '70%')
  })

  it('calls onDone with citations as the final event', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(makeStreamResponse(SSE_EVENTS)))
    const onToken = vi.fn()
    const onDone = vi.fn()

    await queryStreaming('What GPA?', onToken, onDone)

    expect(onDone).toHaveBeenCalledTimes(1)
    expect(onDone).toHaveBeenCalledWith(['https://uwaterloo.ca/gpa'])
  })

  it('calls onDone after all onToken calls', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(makeStreamResponse(SSE_EVENTS)))
    const order: string[] = []
    const onToken = vi.fn(() => order.push('token'))
    const onDone = vi.fn(() => order.push('done'))

    await queryStreaming('What GPA?', onToken, onDone)

    expect(order.at(-1)).toBe('done')
    expect(order.filter(e => e === 'token').length).toBe(3)
  })

  it('throws on non-ok response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503 }))
    await expect(queryStreaming('test', vi.fn(), vi.fn())).rejects.toThrow('HTTP 503')
  })
})
