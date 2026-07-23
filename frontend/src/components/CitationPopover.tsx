import { CitationItem } from './CitationItem'
import type { Citation } from '../types'

interface CitationPopoverProps {
  citations: Citation[]
  placement: 'above' | 'below'
}

/**
 * Floating panel listing every citation supporting a paragraph.
 *
 * Positioned above or below its trigger via a CSS placement modifier class,
 * and scrolls internally when the citation list is long.
 *
 * @param props.citations - All citations to list, in order.
 * @param props.placement - Whether to anchor the panel above or below the trigger.
 */
export function CitationPopover({ citations, placement }: CitationPopoverProps) {
  return (
    <div
      className={`citation-popover citation-popover--${placement}`}
      role="region"
      aria-label="Sources"
    >
      <p className="citation-popover__heading">Sources</p>
      <ul className="citation-popover__list">
        {citations.map(citation => (
          <CitationItem key={citation.id} citation={citation} />
        ))}
      </ul>
    </div>
  )
}
