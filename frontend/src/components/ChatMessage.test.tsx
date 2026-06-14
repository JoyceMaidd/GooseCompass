import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ChatMessage } from './ChatMessage'
import type { CitedParagraph } from '../types'

const PARAGRAPHS: CitedParagraph[] = [
  {
    text: 'You need a minimum cumulative GPA of 70%.',
    citations: ['https://uwaterloo.ca/gpa-requirements'],
  },
  {
    text: 'ETH Zurich has its own admission criteria.',
    citations: ['https://uwaterloo.ca/eth-zurich'],
  },
]

describe('ChatMessage — assistant role', () => {
  it('renders all paragraph texts', () => {
    render(<ChatMessage paragraphs={PARAGRAPHS} role="assistant" />)
    expect(screen.getByText(/minimum cumulative GPA/)).toBeInTheDocument()
    expect(screen.getByText(/ETH Zurich has its own/)).toBeInTheDocument()
  })

  it('renders citation links for each paragraph', () => {
    render(<ChatMessage paragraphs={PARAGRAPHS} role="assistant" />)
    const links = screen.getAllByRole('link')
    expect(links).toHaveLength(2)
    expect(links[0]).toHaveAttribute('href', 'https://uwaterloo.ca/gpa-requirements')
    expect(links[1]).toHaveAttribute('href', 'https://uwaterloo.ca/eth-zurich')
  })

  it('renders citation links in superscript elements', () => {
    const { container } = render(<ChatMessage paragraphs={PARAGRAPHS} role="assistant" />)
    const sups = container.querySelectorAll('sup')
    expect(sups).toHaveLength(2)
  })

  it('opens citation links in a new tab', () => {
    render(<ChatMessage paragraphs={PARAGRAPHS} role="assistant" />)
    for (const link of screen.getAllByRole('link')) {
      expect(link).toHaveAttribute('target', '_blank')
    }
  })
})

describe('ChatMessage — user role', () => {
  it('renders paragraph text', () => {
    const userParagraphs: CitedParagraph[] = [{ text: 'What GPA do I need?', citations: [] }]
    render(<ChatMessage paragraphs={userParagraphs} role="user" />)
    expect(screen.getByText('What GPA do I need?')).toBeInTheDocument()
  })

  it('does not render citation links for user messages', () => {
    const userParagraphs: CitedParagraph[] = [
      { text: 'What GPA do I need?', citations: ['https://should-not-appear.com'] },
    ]
    render(<ChatMessage paragraphs={userParagraphs} role="user" />)
    expect(screen.queryByRole('link')).toBeNull()
  })
})
