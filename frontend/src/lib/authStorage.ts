const TOKEN_KEY = 'goosecompass_token'

/** Read the stored JWT, or null if none is present. */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

/** Persist the JWT for future sessions. */
export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

/** Remove the stored JWT (sign-out). */
export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

/** Decode the `sub` (email) claim from a JWT payload for display only (no signature verification). */
export function decodeEmailFromToken(token: string): string | null {
  try {
    const payload = token.split('.')[1]
    if (!payload) return null
    const json = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
    const parsed = JSON.parse(json)
    return typeof parsed.sub === 'string' ? parsed.sub : null
  } catch {
    return null
  }
}

/** Read the email embedded in the currently stored JWT, if any token is present. */
export function getStoredEmail(): string | null {
  const token = getToken()
  return token ? decodeEmailFromToken(token) : null
}
