import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useChat } from './useChat'
import * as client from '../api/client'
import type { Citation } from '../types'

const CITATION_ONE: Citation = { id: 'one', title: 'Source One', url: 'https://uwaterloo.ca/one' }
const CITATION_TWO: Citation = { id: 'two', title: 'Source Two', url: 'https://uwaterloo.ca/two' }
const CITATION_GPA: Citation = { id: 'gpa', title: 'GPA Requirements', url: 'https://uwaterloo.ca/gpa' }

vi.mock('../api/client')

const mockQueryStreaming = vi.mocked(client.queryStreaming)

beforeEach(() => {
  vi.resetAllMocks()
})

describe('useChat', () => {
  it('starts with empty messages and isLoading false', () => {
    const { result } = renderHook(() => useChat())
    expect(result.current.messages).toEqual([])
    expect(result.current.isLoading).toBe(false)
  })

  it('appends user and assistant messages when sendMessage is called', async () => {
    mockQueryStreaming.mockResolvedValue(undefined)

    const { result } = renderHook(() => useChat())
    await act(async () => {
      result.current.sendMessage('What GPA do I need?')
    })

    expect(result.current.messages).toHaveLength(2)
    expect(result.current.messages[0].role).toBe('user')
    expect(result.current.messages[0].paragraphs[0].text).toBe('What GPA do I need?')
    expect(result.current.messages[1].role).toBe('assistant')
  })

  it('sets isLoading true while streaming, false when done', async () => {
    let resolveDone!: () => void
    mockQueryStreaming.mockImplementation(async (_query, _onToken, _onParagraphEnd, onDone) => {
      await new Promise<void>(resolve => { resolveDone = resolve })
      onDone()
    })

    const { result } = renderHook(() => useChat())

    act(() => { result.current.sendMessage('test') })
    expect(result.current.isLoading).toBe(true)

    await act(async () => { resolveDone() })
    expect(result.current.isLoading).toBe(false)
  })

  it('accumulates tokens into the assistant message', async () => {
    mockQueryStreaming.mockImplementation(async (_query, onToken, onParagraphEnd, onDone) => {
      onToken('You ')
      onToken('need ')
      onToken('70%')
      onParagraphEnd([CITATION_GPA])
      onDone()
    })

    const { result } = renderHook(() => useChat())
    await act(async () => {
      result.current.sendMessage('GPA question')
    })

    const assistant = result.current.messages[1]
    expect(assistant.paragraphs[0].text).toBe('You need 70%')
    expect(assistant.paragraphs[0].citations).toEqual([CITATION_GPA])
  })

  it('starts a new paragraph after paragraph_end and accumulates independently', async () => {
    mockQueryStreaming.mockImplementation(async (_query, onToken, onParagraphEnd, onDone) => {
      onToken('First ')
      onToken('idea.')
      onParagraphEnd([CITATION_ONE])
      onToken('Second ')
      onToken('idea.')
      onParagraphEnd([CITATION_TWO])
      onDone()
    })

    const { result } = renderHook(() => useChat())
    await act(async () => {
      result.current.sendMessage('multi-part question')
    })

    const assistant = result.current.messages[1]
    expect(assistant.paragraphs).toHaveLength(2)
    expect(assistant.paragraphs[0].text).toBe('First idea.')
    expect(assistant.paragraphs[0].citations).toEqual([CITATION_ONE])
    expect(assistant.paragraphs[1].text).toBe('Second idea.')
    expect(assistant.paragraphs[1].citations).toEqual([CITATION_TWO])
  })

  it('does not leave a dangling empty trailing paragraph after the stream ends', async () => {
    mockQueryStreaming.mockImplementation(async (_query, onToken, onParagraphEnd, onDone) => {
      onToken('Only idea.')
      onParagraphEnd([CITATION_ONE])
      onDone()
    })

    const { result } = renderHook(() => useChat())
    await act(async () => {
      result.current.sendMessage('single-part question')
    })

    const assistant = result.current.messages[1]
    expect(assistant.paragraphs).toHaveLength(1)
  })

  it('sets isLoading false on streaming error', async () => {
    mockQueryStreaming.mockRejectedValue(new Error('network error'))

    const { result } = renderHook(() => useChat())
    await act(async () => {
      result.current.sendMessage('failing query')
    })

    expect(result.current.isLoading).toBe(false)
  })

  it('clears messages and isLoading when startNewChat is called', async () => {
    mockQueryStreaming.mockResolvedValue(undefined)

    const { result } = renderHook(() => useChat())
    await act(async () => {
      result.current.sendMessage('What GPA do I need?')
    })
    expect(result.current.messages).toHaveLength(2)

    act(() => {
      result.current.startNewChat()
    })

    expect(result.current.messages).toEqual([])
    expect(result.current.isLoading).toBe(false)
  })
})
