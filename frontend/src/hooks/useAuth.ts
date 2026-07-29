import { useState } from 'react'
import { AuthApiError, requestCode, verifyCode } from '../api/authClient'
import { clearToken, getToken, setToken } from '../lib/authStorage'
import type { AuthStep } from '../types'

function requestCodeErrorMessage(status: number): string {
  if (status === 429) return 'Please wait a bit before requesting another code.'
  if (status === 400) return 'Please use your @uwaterloo.ca email address.'
  return 'Could not send a code. Please try again.'
}

function verifyCodeErrorMessage(status: number): string {
  if (status === 401) return 'Incorrect or expired code. Please try again.'
  return 'Could not verify that code. Please try again.'
}

/**
 * Owns the email-OTP sign-in flow and current authentication status.
 *
 * @returns isAuthenticated - True once a token is present (from a prior session or a fresh sign-in).
 * @returns step - Current stage of the sign-in flow: 'email' or 'otp'.
 * @returns email - The email currently being verified.
 * @returns isLoading - True while a request-code or verify-code call is in flight.
 * @returns error - Human-readable error from the last failed action, or null.
 * @returns submitEmail - Request an OTP for the given email; advances to 'otp' step on success.
 * @returns submitCode - Verify the OTP; on success stores the token and marks authenticated.
 * @returns resendCode - Re-request an OTP for the current email (subject to server-side cooldown).
 * @returns signOut - Clear the stored token and return to the 'email' step.
 */
export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => getToken() !== null)
  const [step, setStep] = useState<AuthStep>('email')
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function submitEmail(candidateEmail: string) {
    setIsLoading(true)
    setError(null)
    try {
      await requestCode(candidateEmail)
      setEmail(candidateEmail)
      setStep('otp')
    } catch (e) {
      setError(e instanceof AuthApiError ? requestCodeErrorMessage(e.status) : 'Could not send a code. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  async function submitCode(code: string) {
    setIsLoading(true)
    setError(null)
    try {
      const { access_token } = await verifyCode(email, code)
      setToken(access_token)
      setIsAuthenticated(true)
    } catch (e) {
      setError(e instanceof AuthApiError ? verifyCodeErrorMessage(e.status) : 'Could not verify that code. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  async function resendCode() {
    await submitEmail(email)
  }

  function signOut() {
    clearToken()
    setIsAuthenticated(false)
    setStep('email')
    setEmail('')
  }

  return { isAuthenticated, step, email, isLoading, error, submitEmail, submitCode, resendCode, signOut }
}
