import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrandingPanel } from './BrandingPanel'

describe('BrandingPanel', () => {
  it('renders the wordmark heading', () => {
    render(<BrandingPanel />)
    expect(screen.getByRole('heading', { name: /GooseCompass/i })).toBeInTheDocument()
  })

  it('renders the tagline text', () => {
    render(<BrandingPanel />)
    expect(screen.getByText(/Your AI study companion for exchange at Waterloo/i)).toBeInTheDocument()
  })

  it('contains no interactive elements (buttons, links)', () => {
    render(<BrandingPanel />)
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
    expect(screen.queryByRole('link')).not.toBeInTheDocument()
  })
})
