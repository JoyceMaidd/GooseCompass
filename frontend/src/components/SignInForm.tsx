import { useState, type FormEvent } from 'react'
import type { AuthStep } from '../types'

interface SignInFormProps {
  step: AuthStep
  email: string
  isLoading: boolean
  error: string | null
  onSubmitEmail: (email: string) => void
  onSubmitCode: (code: string) => void
  onResend: () => void
}

/**
 * Two-step sign-in form: email entry, then one-time code entry.
 *
 * @param props.step - Which step to render.
 * @param props.email - The email being verified (shown during the code step).
 * @param props.isLoading - Disables inputs/buttons while a request is in flight.
 * @param props.error - Error message to display, if any.
 * @param props.onSubmitEmail - Called with the entered email.
 * @param props.onSubmitCode - Called with the entered code.
 * @param props.onResend - Called to re-request a code for the current email.
 */
export function SignInForm({ step, email, isLoading, error, onSubmitEmail, onSubmitCode, onResend }: SignInFormProps) {
  const [emailValue, setEmailValue] = useState('')
  const [codeValue, setCodeValue] = useState('')

  function handleEmailSubmit(e: FormEvent) {
    e.preventDefault()
    if (!emailValue.trim() || isLoading) return
    onSubmitEmail(emailValue.trim())
  }

  function handleCodeSubmit(e: FormEvent) {
    e.preventDefault()
    if (!codeValue.trim() || isLoading) return
    onSubmitCode(codeValue.trim())
  }

  return (
    <div className="sign-in-form">
      {error && <p className="sign-in-form__error" role="alert">{error}</p>}

      {step === 'email' && (
        <form className="sign-in-form__step" onSubmit={handleEmailSubmit}>
          <label className="sign-in-form__label" htmlFor="sign-in-email">
            @uwaterloo.ca email
          </label>
          <input
            id="sign-in-email"
            className="sign-in-form__input"
            type="email"
            value={emailValue}
            onChange={e => setEmailValue(e.target.value)}
            disabled={isLoading}
            placeholder="you@uwaterloo.ca"
          />
          <button className="sign-in-form__submit" type="submit" disabled={isLoading || !emailValue.trim()}>
            Send code
          </button>
        </form>
      )}

      {step === 'otp' && (
        <form className="sign-in-form__step" onSubmit={handleCodeSubmit}>
          <p className="sign-in-form__hint">Code sent to {email}</p>
          <label className="sign-in-form__label" htmlFor="sign-in-code">
            Verification code
          </label>
          <input
            id="sign-in-code"
            className="sign-in-form__input"
            type="text"
            inputMode="numeric"
            value={codeValue}
            onChange={e => setCodeValue(e.target.value)}
            disabled={isLoading}
            placeholder="123456"
          />
          <button className="sign-in-form__submit" type="submit" disabled={isLoading || !codeValue.trim()}>
            Verify
          </button>
          <button
            className="sign-in-form__resend"
            type="button"
            onClick={onResend}
            disabled={isLoading}
          >
            Resend code
          </button>
        </form>
      )}
    </div>
  )
}
