import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'
import * as useAuthModule from './hooks/useAuth'

vi.mock('./hooks/useAuth')
vi.mock('./hooks/useChat', () => ({
  useChat: () => ({ messages: [], isLoading: false, sendMessage: vi.fn(), startNewChat: vi.fn() }),
}))

const mockUseAuth = vi.mocked(useAuthModule.useAuth)

beforeEach(() => {
  vi.resetAllMocks()
})

describe('App', () => {
  it('renders SignInPage when not authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      step: 'email',
      email: '',
      isLoading: false,
      error: null,
      submitEmail: vi.fn(),
      submitCode: vi.fn(),
      resendCode: vi.fn(),
      signOut: vi.fn(),
    })

    render(<App />)

    expect(screen.getByText(/Sign in with your @uwaterloo\.ca email/i)).toBeInTheDocument()
  })

  it('renders ChatPage when authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      step: 'email',
      email: '',
      isLoading: false,
      error: null,
      submitEmail: vi.fn(),
      submitCode: vi.fn(),
      resendCode: vi.fn(),
      signOut: vi.fn(),
    })

    render(<App />)

    expect(screen.getByRole('heading', { name: /GooseCompass/i })).toBeInTheDocument()
    expect(screen.queryByText(/Sign in with your @uwaterloo\.ca email/i)).not.toBeInTheDocument()
  })
})
