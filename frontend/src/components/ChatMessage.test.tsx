import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ChatMessage } from './ChatMessage'
import type { CitedParagraph } from '../types'

const PARAGRAPHS: CitedParagraph[] = [
  {
    text: 'You need a minimum cumulative GPA of 70%.',
    citations: [
      { id: 'gpa', title: 'GPA Requirements', url: 'https://uwaterloo.ca/gpa-requirements' },
    ],
  },
  {
    text: 'ETH Zurich has its own admission criteria.',
    citations: [
      { id: 'eth-1', title: 'ETH Zurich Guide', url: 'https://uwaterloo.ca/eth-zurich' },
      { id: 'eth-2', title: 'ETH Admissions', url: 'https://ethz.ch/admissions' },
    ],
  },
]

describe('ChatMessage — assistant role', () => {
  it('renders all paragraph texts', () => {
    render(<ChatMessage paragraphs={PARAGRAPHS} role="assistant" />)
    expect(screen.getByText(/minimum cumulative GPA/)).toBeInTheDocument()
    expect(screen.getByText(/ETH Zurich has its own/)).toBeInTheDocument()
  })

  it('renders a single citation as a direct link', () => {
    render(<ChatMessage paragraphs={PARAGRAPHS} role="assistant" />)
    const link = screen.getByRole('link', { name: /GPA Requirements/ })
    expect(link).toHaveAttribute('href', 'https://uwaterloo.ca/gpa-requirements')
    expect(link).toHaveAttribute('target', '_blank')
  })

  it('renders multiple citations as a button trigger with a +N count', () => {
    render(<ChatMessage paragraphs={PARAGRAPHS} role="assistant" />)
    expect(screen.getByRole('button', { name: /ETH Zurich Guide \+1/ })).toBeInTheDocument()
  })

  it('does not render a paragraph with empty text', () => {
    const withTrailingEmpty: CitedParagraph[] = [...PARAGRAPHS, { text: '', citations: [] }]
    const { container } = render(<ChatMessage paragraphs={withTrailingEmpty} role="assistant" />)
    expect(container.querySelectorAll('p')).toHaveLength(2)
  })

  it('renders no citation control when a paragraph has no citations', () => {
    const noCitations: CitedParagraph[] = [{ text: 'Plain statement.', citations: [] }]
    render(<ChatMessage paragraphs={noCitations} role="assistant" />)
    expect(screen.queryByRole('link')).toBeNull()
    expect(screen.queryByRole('button')).toBeNull()
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
      {
        text: 'What GPA do I need?',
        citations: [{ id: 'x', title: 'Should not appear', url: 'https://should-not-appear.com' }],
      },
    ]
    render(<ChatMessage paragraphs={userParagraphs} role="user" />)
    expect(screen.queryByRole('link')).toBeNull()
  })
})
