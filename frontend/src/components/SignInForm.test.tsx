import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SignInForm } from './SignInForm'

describe('SignInForm', () => {
  describe('email step', () => {
    it('calls onSubmitEmail with the typed email on submit', async () => {
      const onSubmitEmail = vi.fn()
      render(
        <SignInForm
          step="email"
          email=""
          isLoading={false}
          error={null}
          onSubmitEmail={onSubmitEmail}
          onSubmitCode={vi.fn()}
          onResend={vi.fn()}
        />,
      )

      await userEvent.type(screen.getByRole('textbox', { name: /email/i }), 'student@uwaterloo.ca')
      await userEvent.click(screen.getByRole('button', { name: 'Send code' }))

      expect(onSubmitEmail).toHaveBeenCalledWith('student@uwaterloo.ca')
    })

    it('does not submit an empty email', async () => {
      const onSubmitEmail = vi.fn()
      render(
        <SignInForm
          step="email"
          email=""
          isLoading={false}
          error={null}
          onSubmitEmail={onSubmitEmail}
          onSubmitCode={vi.fn()}
          onResend={vi.fn()}
        />,
      )

      expect(screen.getByRole('button', { name: 'Send code' })).toBeDisabled()
      expect(onSubmitEmail).not.toHaveBeenCalled()
    })

    it('disables input and button while isLoading', () => {
      render(
        <SignInForm
          step="email"
          email=""
          isLoading={true}
          error={null}
          onSubmitEmail={vi.fn()}
          onSubmitCode={vi.fn()}
          onResend={vi.fn()}
        />,
      )

      expect(screen.getByRole('textbox', { name: /email/i })).toBeDisabled()
      expect(screen.getByRole('button', { name: 'Send code' })).toBeDisabled()
    })
  })

  describe('otp step', () => {
    it('shows the email the code was sent to', () => {
      render(
        <SignInForm
          step="otp"
          email="student@uwaterloo.ca"
          isLoading={false}
          error={null}
          onSubmitEmail={vi.fn()}
          onSubmitCode={vi.fn()}
          onResend={vi.fn()}
        />,
      )

      expect(screen.getByText(/student@uwaterloo\.ca/)).toBeInTheDocument()
    })

    it('calls onSubmitCode with the typed code on submit', async () => {
      const onSubmitCode = vi.fn()
      render(
        <SignInForm
          step="otp"
          email="student@uwaterloo.ca"
          isLoading={false}
          error={null}
          onSubmitEmail={vi.fn()}
          onSubmitCode={onSubmitCode}
          onResend={vi.fn()}
        />,
      )

      await userEvent.type(screen.getByRole('textbox', { name: /verification code/i }), '123456')
      await userEvent.click(screen.getByRole('button', { name: 'Verify' }))

      expect(onSubmitCode).toHaveBeenCalledWith('123456')
    })

    it('calls onResend when the resend button is clicked', async () => {
      const onResend = vi.fn()
      render(
        <SignInForm
          step="otp"
          email="student@uwaterloo.ca"
          isLoading={false}
          error={null}
          onSubmitEmail={vi.fn()}
          onSubmitCode={vi.fn()}
          onResend={onResend}
        />,
      )

      await userEvent.click(screen.getByRole('button', { name: 'Resend code' }))

      expect(onResend).toHaveBeenCalledOnce()
    })
  })

  it('renders the error message when present', () => {
    render(
      <SignInForm
        step="email"
        email=""
        isLoading={false}
        error="Please use your @uwaterloo.ca email address."
        onSubmitEmail={vi.fn()}
        onSubmitCode={vi.fn()}
        onResend={vi.fn()}
      />,
    )

    expect(screen.getByRole('alert')).toHaveTextContent('Please use your @uwaterloo.ca email address.')
  })
})
