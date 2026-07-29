import type { VerifyCodeResponse } from '../types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

/** Thrown when an auth request fails, carrying the response status so callers can distinguish cases (e.g. 429 cooldown vs 401 wrong code). */
export class AuthApiError extends Error {
  status: number

  constructor(status: number) {
    super(`HTTP ${status}`)
    this.status = status
  }
}

/**
 * Request a one-time code be emailed to the given @uwaterloo.ca address.
 *
 * @param email - The address to send a one-time code to.
 */
export async function requestCode(email: string): Promise<void> {
  const response = await fetch(`${API_URL}/auth/request-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  })
  if (!response.ok) throw new AuthApiError(response.status)
}

/**
 * Verify a one-time code and exchange it for a session JWT.
 *
 * @param email - The address being verified.
 * @param code - The one-time code the user received.
 * @returns The verify-code response, including the issued JWT.
 */
export async function verifyCode(email: string, code: string): Promise<VerifyCodeResponse> {
  const response = await fetch(`${API_URL}/auth/verify-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, code }),
  })
  if (!response.ok) throw new AuthApiError(response.status)
  return response.json()
}
