import { useCallback, useRef, useState } from 'react'

/** Computed placement for a citation popover relative to its trigger. */
export interface PopoverPlacement {
  placement: 'above' | 'below'
}

const POPOVER_MAX_HEIGHT = 320

/**
 * Manages open/closed state and above/below placement for a citation popover.
 *
 * The popover flips above its trigger when there isn't enough room below in
 * the viewport, per the citation feature spec's positioning requirement.
 *
 * @returns triggerRef - Ref to attach to the popover's trigger element.
 * @returns isOpen - Whether the popover should currently render.
 * @returns placement - 'above' or 'below', valid once the popover is open.
 * @returns show - Opens the popover and recomputes its placement.
 * @returns hide - Closes the popover.
 */
export function useCitationPopoverPosition() {
  const triggerRef = useRef<HTMLButtonElement>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [placement, setPlacement] = useState<PopoverPlacement['placement']>('below')

  const show = useCallback(() => {
    const rect = triggerRef.current?.getBoundingClientRect()
    if (rect) {
      const spaceBelow = window.innerHeight - rect.bottom
      setPlacement(spaceBelow < POPOVER_MAX_HEIGHT && rect.top > spaceBelow ? 'above' : 'below')
    }
    setIsOpen(true)
  }, [])

  const hide = useCallback(() => setIsOpen(false), [])

  return { triggerRef, isOpen, placement, show, hide }
}
