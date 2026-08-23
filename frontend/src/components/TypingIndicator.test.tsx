import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TypingIndicator } from './TypingIndicator'

describe('TypingIndicator', () => {
  it('renders an accessible status region', () => {
    render(<TypingIndicator />)
    expect(screen.getByRole('status', { name: /typing/i })).toBeInTheDocument()
  })

  it('renders three dots', () => {
    const { container } = render(<TypingIndicator />)
    expect(container.querySelectorAll('.typing-indicator__dot')).toHaveLength(3)
  })
})
