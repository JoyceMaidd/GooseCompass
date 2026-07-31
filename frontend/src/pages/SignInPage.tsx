import { useState } from 'react'
import { SignInForm } from '../components/SignInForm'
import type { AuthStep } from '../types'

interface SignInPageProps {
  step: AuthStep
  email: string
  isLoading: boolean
  error: string | null
  onSubmitEmail: (email: string) => void
  onSubmitCode: (code: string) => void
  onResend: () => void
}

/**
 * Sign-in page: gates access behind a verified @uwaterloo.ca email + one-time code.
 *
 * Starts with a hero section featuring the GooseCompass title and tagline with a
 * "Get Started" button. Clicking the button reveals the sign-in form. Presentational
 * only — auth state and actions are owned by App.tsx's single `useAuth()` call and
 * passed down as props, so this component (and the chat page it gates) always see a
 * consistent, single source of truth.
 *
 * @param props.step - Which step of the sign-in flow to render.
 * @param props.email - The email being verified (shown during the code step).
 * @param props.isLoading - Disables inputs/buttons while a request is in flight.
 * @param props.error - Error message to display, if any.
 * @param props.onSubmitEmail - Called with the entered email.
 * @param props.onSubmitCode - Called with the entered code.
 * @param props.onResend - Called to re-request a code for the current email.
 */
export function SignInPage({ step, email, isLoading, error, onSubmitEmail, onSubmitCode, onResend }: SignInPageProps) {
  const [showForm, setShowForm] = useState(false)

  return (
    <div className="sign-in-page">
      <div className={`sign-in-page__hero ${showForm ? 'sign-in-page__hero--hidden' : ''}`}>
        <h1 className="sign-in-page__wordmark">GooseCompass</h1>
        <p className="sign-in-page__tagline">Navigate Your Exchange Journey</p>
        <button className="sign-in-page__cta-button" onClick={() => setShowForm(true)}>
          Get Started
        </button>
      </div>

      <div className={`sign-in-page__form-panel ${!showForm ? 'sign-in-page__form-panel--hidden' : ''}`}>
        <div className="sign-in-page__form-card">
          <h2 className="sign-in-page__form-title">Sign in</h2>
          <p className="sign-in-page__form-subtitle">Sign in with your @uwaterloo.ca email</p>
          <SignInForm
            step={step}
            email={email}
            isLoading={isLoading}
            error={error}
            onSubmitEmail={onSubmitEmail}
            onSubmitCode={onSubmitCode}
            onResend={onResend}
          />
        </div>
      </div>
    </div>
  )
}
