import { DocumentIcon } from './DocumentIcon'
import type { Citation } from '../types'

interface CitationItemProps {
  citation: Citation
}

/**
 * A single source row inside a citation popover.
 *
 * Shows the source's full title and snippet preview, with a link to open
 * the original source in a new tab when a URL is available.
 *
 * @param props.citation - The citation to render.
 */
export function CitationItem({ citation }: CitationItemProps) {
  return (
    <li className="citation-item">
      <span className="citation-item__icon">
        <DocumentIcon />
      </span>
      <div>
        <p className="citation-item__title">{citation.title}</p>
        {citation.snippet && <p className="citation-item__snippet">{citation.snippet}</p>}
        {citation.url && (
          <a
            className="citation-item__link"
            href={citation.url}
            target="_blank"
            rel="noopener noreferrer"
          >
            View source →
          </a>
        )}
      </div>
    </li>
  )
}
