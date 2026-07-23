import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatPage } from './ChatPage'
import * as useChatModule from '../hooks/useChat'
import type { Message } from '../types'

vi.mock('../hooks/useChat')

const mockUseChat = vi.mocked(useChatModule.useChat)

function makeMessages(overrides: Partial<Message>[] = []): Message[] {
  return overrides.map(o => ({
    role: 'assistant' as const,
    paragraphs: [{ text: '', citations: [] }],
    ...o,
  }))
}

beforeEach(() => {
  vi.resetAllMocks()
})

describe('ChatPage', () => {
  it('renders the header and input', () => {
    mockUseChat.mockReturnValue({ messages: [], isLoading: false, sendMessage: vi.fn(), startNewChat: vi.fn() })
    render(<ChatPage />)
    expect(screen.getByRole('heading', { name: /GooseCompass/i })).toBeInTheDocument()
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('calls sendMessage when user submits a query', async () => {
    const sendMessage = vi.fn()
    mockUseChat.mockReturnValue({ messages: [], isLoading: false, sendMessage, startNewChat: vi.fn() })
    render(<ChatPage />)

    await userEvent.type(screen.getByRole('textbox'), 'What GPA do I need?{Enter}')

    expect(sendMessage).toHaveBeenCalledWith('What GPA do I need?')
  })

  it('renders assistant message text from the messages array', () => {
    mockUseChat.mockReturnValue({
      messages: makeMessages([
        { role: 'user', paragraphs: [{ text: 'What GPA?', citations: [] }] },
        {
          role: 'assistant',
          paragraphs: [
            {
              text: 'You need 70%.',
              citations: [{ id: 'uw', title: 'UWaterloo', url: 'https://uwaterloo.ca' }],
            },
          ],
        },
      ]),
      isLoading: false,
      sendMessage: vi.fn(),
      startNewChat: vi.fn(),
    })
    render(<ChatPage />)

    expect(screen.getByText('What GPA?')).toBeInTheDocument()
    expect(screen.getByText('You need 70%.')).toBeInTheDocument()
  })

  it('disables input while isLoading is true', () => {
    mockUseChat.mockReturnValue({ messages: [], isLoading: true, sendMessage: vi.fn(), startNewChat: vi.fn() })
    render(<ChatPage />)
    expect(screen.getByRole('textbox')).toBeDisabled()
  })

  it('calls startNewChat when the New Chat button is clicked', async () => {
    const startNewChat = vi.fn()
    mockUseChat.mockReturnValue({ messages: [], isLoading: false, sendMessage: vi.fn(), startNewChat })
    render(<ChatPage />)

    await userEvent.click(screen.getByRole('button', { name: /New Chat/i }))

    expect(startNewChat).toHaveBeenCalledOnce()
  })
})
