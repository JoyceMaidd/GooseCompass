import { describe, it, expect, afterEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useCitationPopoverPosition } from './useCitationPopoverPosition'

function stubTrigger(result: ReturnType<typeof useCitationPopoverPosition>, rect: Partial<DOMRect>) {
  result.triggerRef.current = {
    getBoundingClientRect: () => rect as DOMRect,
  } as unknown as HTMLButtonElement
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('useCitationPopoverPosition', () => {
  it('starts closed with placement below', () => {
    const { result } = renderHook(() => useCitationPopoverPosition())
    expect(result.current.isOpen).toBe(false)
    expect(result.current.placement).toBe('below')
  })

  it('opens with placement below when there is ample space below', () => {
    vi.stubGlobal('innerHeight', 800)
    const { result } = renderHook(() => useCitationPopoverPosition())
    act(() => {
      stubTrigger(result.current, { top: 100, bottom: 120 })
      result.current.show()
    })
    expect(result.current.isOpen).toBe(true)
    expect(result.current.placement).toBe('below')
  })

  it('flips to placement above when space below is insufficient', () => {
    vi.stubGlobal('innerHeight', 400)
    const { result } = renderHook(() => useCitationPopoverPosition())
    act(() => {
      stubTrigger(result.current, { top: 350, bottom: 370 })
      result.current.show()
    })
    expect(result.current.isOpen).toBe(true)
    expect(result.current.placement).toBe('above')
  })

  it('hide() closes the popover', () => {
    vi.stubGlobal('innerHeight', 800)
    const { result } = renderHook(() => useCitationPopoverPosition())
    act(() => {
      stubTrigger(result.current, { top: 100, bottom: 120 })
      result.current.show()
    })
    expect(result.current.isOpen).toBe(true)

    act(() => {
      result.current.hide()
    })
    expect(result.current.isOpen).toBe(false)
  })
})
