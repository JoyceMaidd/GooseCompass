import type { FocusEvent } from 'react'
import { CitationPopover } from './CitationPopover'
import { DocumentIcon } from './DocumentIcon'
import { useCitationPopoverPosition } from '../hooks/useCitationPopoverPosition'
import type { Citation } from '../types'

interface CitationBubbleProps {
  citations: Citation[]
}

/**
 * Compact inline citation control shown at the end of a cited paragraph.
 *
 * A single citation renders as a direct link to its source. Multiple
 * citations render as a "first title +N" trigger that reveals a popover
 * listing every source on hover or keyboard focus.
 *
 * @param props.citations - Citations supporting the paragraph this bubble follows.
 */
export function CitationBubble({ citations }: CitationBubbleProps) {
  const { triggerRef, isOpen, placement, show, hide } = useCitationPopoverPosition()

  if (citations.length === 0) return null

  const [first, ...rest] = citations

  if (rest.length === 0) {
    return (
      <span className="citation-bubble">
        <a
          className="citation-pill"
          href={first.url}
          target="_blank"
          rel="noopener noreferrer"
        >
          <DocumentIcon />
          {first.title}
        </a>
      </span>
    )
  }

  function handleBlur(e: FocusEvent<HTMLSpanElement>) {
    if (!e.currentTarget.contains(e.relatedTarget as Node)) hide()
  }

  return (
    <span
      className="citation-bubble"
      onMouseEnter={show}
      onMouseLeave={hide}
      onFocus={show}
      onBlur={handleBlur}
    >
      <button
        ref={triggerRef}
        type="button"
        className="citation-pill"
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        <DocumentIcon />
        {first.title} +{rest.length}
      </button>
      {isOpen && <CitationPopover citations={citations} placement={placement} />}
    </span>
  )
}
