import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useAuth } from './useAuth'
import * as authClient from '../api/authClient'
import { clearToken, getToken } from '../lib/authStorage'

vi.mock('../api/authClient', async () => {
  const actual = await vi.importActual<typeof authClient>('../api/authClient')
  return { ...actual, requestCode: vi.fn(), verifyCode: vi.fn() }
})

const mockRequestCode = vi.mocked(authClient.requestCode)
const mockVerifyCode = vi.mocked(authClient.verifyCode)

beforeEach(() => {
  vi.resetAllMocks()
})

afterEach(() => {
  clearToken()
})

describe('useAuth', () => {
  it('starts unauthenticated on the email step when no token is stored', () => {
    const { result } = renderHook(() => useAuth())
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.step).toBe('email')
  })

  it('starts authenticated when a token is already stored', () => {
    localStorage.setItem('goosecompass_token', 'existing-token')
    const { result } = renderHook(() => useAuth())
    expect(result.current.isAuthenticated).toBe(true)
  })

  it('decodes and initializes email from a stored JWT on mount', () => {
    const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huQHV3YXRlcmxvby5jYSIsImlhdCI6MTcyNjA3ODAwMCwiZXhwIjoxNzI2MDgxNjAwfQ.fakesignature'
    localStorage.setItem('goosecompass_token', token)
    const { result } = renderHook(() => useAuth())
    expect(result.current.email).toBe('john@uwaterloo.ca')
  })

  it('submitEmail success advances to the otp step', async () => {
    mockRequestCode.mockResolvedValue(undefined)
    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await result.current.submitEmail('student@uwaterloo.ca')
    })

    expect(result.current.step).toBe('otp')
    expect(result.current.email).toBe('student@uwaterloo.ca')
    expect(result.current.error).toBeNull()
  })

  it('submitEmail failure sets an error and stays on the email step', async () => {
    mockRequestCode.mockRejectedValue(new authClient.AuthApiError(400))
    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await result.current.submitEmail('student@gmail.com')
    })

    expect(result.current.step).toBe('email')
    expect(result.current.error).not.toBeNull()
  })

  it('submitCode success stores the token and marks authenticated', async () => {
    mockVerifyCode.mockResolvedValue({ access_token: 'new-token', token_type: 'bearer' })
    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await result.current.submitCode('123456')
    })

    expect(result.current.isAuthenticated).toBe(true)
    expect(getToken()).toBe('new-token')
  })

  it('submitCode failure sets an error and stays unauthenticated', async () => {
    mockVerifyCode.mockRejectedValue(new authClient.AuthApiError(401))
    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await result.current.submitCode('000000')
    })

    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.error).not.toBeNull()
  })

  it('resendCode re-requests a code for the current email', async () => {
    mockRequestCode.mockResolvedValue(undefined)
    const { result } = renderHook(() => useAuth())
    await act(async () => {
      await result.current.submitEmail('student@uwaterloo.ca')
    })

    await act(async () => {
      await result.current.resendCode()
    })

    expect(mockRequestCode).toHaveBeenCalledTimes(2)
    expect(mockRequestCode).toHaveBeenLastCalledWith('student@uwaterloo.ca')
  })

  it('signOut clears the token and resets to the email step', async () => {
    mockVerifyCode.mockResolvedValue({ access_token: 'new-token', token_type: 'bearer' })
    const { result } = renderHook(() => useAuth())
    await act(async () => {
      await result.current.submitCode('123456')
    })

    act(() => {
      result.current.signOut()
    })

    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.step).toBe('email')
    expect(getToken()).toBeNull()
  })
})
