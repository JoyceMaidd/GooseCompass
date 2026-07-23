import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { CitationItem } from './CitationItem'
import type { Citation } from '../types'

describe('CitationItem', () => {
  it('renders the full title and snippet', () => {
    const citation: Citation = {
      id: 'a',
      title: 'Exchange Eligibility Requirements',
      snippet: 'Students must maintain a 70% GPA.',
      url: 'https://uwaterloo.ca/exchange',
    }
    render(
      <ul>
        <CitationItem citation={citation} />
      </ul>,
    )
    expect(screen.getByText('Exchange Eligibility Requirements')).toBeInTheDocument()
    expect(screen.getByText('Students must maintain a 70% GPA.')).toBeInTheDocument()
  })

  it('omits the snippet paragraph when snippet is undefined', () => {
    const citation: Citation = { id: 'a', title: 'Doc', url: 'https://example.com' }
    const { container } = render(
      <ul>
        <CitationItem citation={citation} />
      </ul>,
    )
    expect(container.querySelector('.citation-item__snippet')).toBeNull()
  })

  it('renders a link with correct href and target when url is present', () => {
    const citation: Citation = { id: 'a', title: 'Doc', url: 'https://example.com/page' }
    render(
      <ul>
        <CitationItem citation={citation} />
      </ul>,
    )
    const link = screen.getByRole('link', { name: /View source/ })
    expect(link).toHaveAttribute('href', 'https://example.com/page')
    expect(link).toHaveAttribute('target', '_blank')
  })

  it('omits the link entirely when url is undefined', () => {
    const citation: Citation = { id: 'a', title: 'Doc' }
    render(
      <ul>
        <CitationItem citation={citation} />
      </ul>,
    )
    expect(screen.queryByRole('link')).toBeNull()
  })
})
