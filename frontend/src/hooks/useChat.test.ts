import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useChat } from './useChat'
import * as client from '../api/client'

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
    mockQueryStreaming.mockImplementation(async (_query, _onToken, onDone) => {
      await new Promise<void>(resolve => { resolveDone = resolve })
      onDone([])
    })

    const { result } = renderHook(() => useChat())

    act(() => { result.current.sendMessage('test') })
    expect(result.current.isLoading).toBe(true)

    await act(async () => { resolveDone() })
    expect(result.current.isLoading).toBe(false)
  })

  it('accumulates tokens into the assistant message', async () => {
    mockQueryStreaming.mockImplementation(async (_query, onToken, onDone) => {
      onToken('You ')
      onToken('need ')
      onToken('70%')
      onDone(['https://uwaterloo.ca/gpa'])
    })

    const { result } = renderHook(() => useChat())
    await act(async () => {
      result.current.sendMessage('GPA question')
    })

    const assistant = result.current.messages[1]
    expect(assistant.paragraphs[0].text).toBe('You need 70%')
    expect(assistant.paragraphs[0].citations).toEqual(['https://uwaterloo.ca/gpa'])
  })

  it('sets isLoading false on streaming error', async () => {
    mockQueryStreaming.mockRejectedValue(new Error('network error'))

    const { result } = renderHook(() => useChat())
    await act(async () => {
      result.current.sendMessage('failing query')
    })

    expect(result.current.isLoading).toBe(false)
  })
})
