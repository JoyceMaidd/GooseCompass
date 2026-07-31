import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SignInPage } from './SignInPage'

beforeEach(() => {
  vi.clearAllMocks()
})

describe('SignInPage', () => {
  it('renders the hero section by default with title, tagline, and Get Started button', () => {
    render(
      <SignInPage
        step="email"
        email=""
        isLoading={false}
        error={null}
        onSubmitEmail={vi.fn()}
        onSubmitCode={vi.fn()}
        onResend={vi.fn()}
      />
    )

    expect(screen.getByRole('heading', { name: /GooseCompass/i })).toBeInTheDocument()
    expect(screen.getByText(/Navigate Your Exchange Journey/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Get Started/i })).toBeInTheDocument()
  })

  it('hides the hero and shows the form when Get Started is clicked', async () => {
    render(
      <SignInPage
        step="email"
        email=""
        isLoading={false}
        error={null}
        onSubmitEmail={vi.fn()}
        onSubmitCode={vi.fn()}
        onResend={vi.fn()}
      />
    )

    const getStartedButton = screen.getByRole('button', { name: /Get Started/i })
    const heroSection = getStartedButton.closest('.sign-in-page__hero')

    await userEvent.click(getStartedButton)

    expect(heroSection).toHaveClass('sign-in-page__hero--hidden')
    expect(screen.getByText(/Sign in with your @uwaterloo\.ca email/i)).toBeInTheDocument()
  })

  it('renders the sign-in form with the correct subtitle after Get Started is clicked', async () => {
    render(
      <SignInPage
        step="email"
        email=""
        isLoading={false}
        error={null}
        onSubmitEmail={vi.fn()}
        onSubmitCode={vi.fn()}
        onResend={vi.fn()}
      />
    )

    await userEvent.click(screen.getByRole('button', { name: /Get Started/i }))

    expect(screen.getByRole('heading', { level: 2, name: /Sign in/i })).toBeInTheDocument()
    expect(screen.getByText(/Sign in with your @uwaterloo\.ca email/i)).toBeInTheDocument()
  })

  it('delegates form submission to the passed callbacks', async () => {
    const onSubmitEmail = vi.fn()
    render(
      <SignInPage
        step="email"
        email=""
        isLoading={false}
        error={null}
        onSubmitEmail={onSubmitEmail}
        onSubmitCode={vi.fn()}
        onResend={vi.fn()}
      />
    )

    await userEvent.click(screen.getByRole('button', { name: /Get Started/i }))
    await userEvent.type(screen.getByRole('textbox'), 'test@uwaterloo.ca')
    await userEvent.click(screen.getByRole('button', { name: /Send code/i }))

    expect(onSubmitEmail).toHaveBeenCalledWith('test@uwaterloo.ca')
  })
})
