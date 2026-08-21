import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

vi.mock('./hooks/useChat', () => ({
  useChat: () => ({ messages: [], isLoading: false, sendMessage: vi.fn(), startNewChat: vi.fn() }),
}))

describe('App', () => {
  it('renders ChatPage', () => {
    render(<App />)

    expect(screen.getByRole('heading', { name: /GooseCompass/i })).toBeInTheDocument()
  })
})
