import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { CitationPopover } from './CitationPopover'
import type { Citation } from '../types'

const CITATIONS: Citation[] = [
  { id: 'a', title: 'Source A', url: 'https://a.example' },
  { id: 'b', title: 'Source B', url: 'https://b.example' },
  { id: 'c', title: 'Source C', url: 'https://c.example' },
]

describe('CitationPopover', () => {
  it('renders a "Sources" heading', () => {
    render(<CitationPopover citations={CITATIONS} placement="below" />)
    expect(screen.getByText('Sources')).toBeInTheDocument()
  })

  it('renders one item per citation', () => {
    render(<CitationPopover citations={CITATIONS} placement="below" />)
    expect(screen.getByText('Source A')).toBeInTheDocument()
    expect(screen.getByText('Source B')).toBeInTheDocument()
    expect(screen.getByText('Source C')).toBeInTheDocument()
  })

  it('applies the below placement class', () => {
    const { container } = render(<CitationPopover citations={CITATIONS} placement="below" />)
    expect(container.querySelector('.citation-popover--below')).not.toBeNull()
  })

  it('applies the above placement class', () => {
    const { container } = render(<CitationPopover citations={CITATIONS} placement="above" />)
    expect(container.querySelector('.citation-popover--above')).not.toBeNull()
  })
})
