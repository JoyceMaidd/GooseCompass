import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { decodeEmailFromToken, getStoredEmail, setToken, clearToken } from './authStorage'

describe('authStorage', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    localStorage.clear()
  })

  describe('decodeEmailFromToken', () => {
    it('decodes a valid JWT and returns the email from the sub claim', () => {
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QHV3YXRlcmxvby5jYSIsImlhdCI6MTcyNjA3ODAwMCwiZXhwIjoxNzI2MDgxNjAwfQ.fakesignature'
      const email = decodeEmailFromToken(token)
      expect(email).toBe('test@uwaterloo.ca')
    })

    it('returns null for a malformed token (missing payload segment)', () => {
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fakesignature'
      const email = decodeEmailFromToken(token)
      expect(email).toBeNull()
    })

    it('returns null for a token with invalid base64 in the payload', () => {
      const token = 'header.!!!invalid!!!.signature'
      const email = decodeEmailFromToken(token)
      expect(email).toBeNull()
    })

    it('returns null for a token where sub is not a string', () => {
      const token = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOjEyMzQ1fQ.signature'
      const email = decodeEmailFromToken(token)
      expect(email).toBeNull()
    })

    it('returns null for a token with no sub claim', () => {
      const token = 'eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3MjYwNzgwMDB9.signature'
      const email = decodeEmailFromToken(token)
      expect(email).toBeNull()
    })
  })

  describe('getStoredEmail', () => {
    it('returns the decoded email when a token is stored', () => {
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huQHV3YXRlcmxvby5jYSIsImlhdCI6MTcyNjA3ODAwMCwiZXhwIjoxNzI2MDgxNjAwfQ.fakesignature'
      setToken(token)
      const email = getStoredEmail()
      expect(email).toBe('john@uwaterloo.ca')
    })

    it('returns null when no token is stored', () => {
      const email = getStoredEmail()
      expect(email).toBeNull()
    })

    it('returns null when the stored token is malformed', () => {
      setToken('invalid.token.format')
      const email = getStoredEmail()
      expect(email).toBeNull()
    })
  })
})
