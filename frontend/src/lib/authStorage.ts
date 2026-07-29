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
