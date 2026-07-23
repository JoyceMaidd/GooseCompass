import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { CitationBubble } from './CitationBubble'
import type { Citation } from '../types'

const ONE: Citation = { id: 'a', title: 'Source A', url: 'https://a.example' }
const TWO: Citation = { id: 'b', title: 'Source B', url: 'https://b.example' }

describe('CitationBubble', () => {
  it('renders nothing for an empty citation list', () => {
    const { container } = render(<CitationBubble citations={[]} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders a direct link for a single citation, with no popover trigger', () => {
    render(<CitationBubble citations={[ONE]} />)
    const link = screen.getByRole('link', { name: /Source A/ })
    expect(link).toHaveAttribute('href', 'https://a.example')
    expect(link).toHaveAttribute('target', '_blank')
    expect(screen.queryByRole('button')).toBeNull()
  })

  it('renders a button trigger showing the first title and +N for multiple citations', () => {
    render(<CitationBubble citations={[ONE, TWO]} />)
    expect(screen.getByRole('button', { name: /Source A \+1/ })).toBeInTheDocument()
  })

  it('reveals the popover on hover and hides it on mouse leave', () => {
    const { container } = render(<CitationBubble citations={[ONE, TWO]} />)
    const bubble = container.querySelector('.citation-bubble') as HTMLElement

    expect(screen.queryByRole('region', { name: 'Sources' })).toBeNull()

    fireEvent.mouseEnter(bubble)
    expect(screen.getByRole('region', { name: 'Sources' })).toBeInTheDocument()

    fireEvent.mouseLeave(bubble)
    expect(screen.queryByRole('region', { name: 'Sources' })).toBeNull()
  })

  it('reveals the popover on focus', () => {
    render(<CitationBubble citations={[ONE, TWO]} />)
    const trigger = screen.getByRole('button', { name: /Source A \+1/ })

    fireEvent.focus(trigger)
    expect(screen.getByRole('region', { name: 'Sources' })).toBeInTheDocument()
  })

  it('keeps the popover open when blur moves focus onto a popover link', () => {
    const { container } = render(<CitationBubble citations={[ONE, TWO]} />)
    const trigger = screen.getByRole('button', { name: /Source A \+1/ })

    fireEvent.focus(trigger)
    const popoverLink = screen.getAllByRole('link', { name: /View source/ })[0]
    fireEvent.blur(trigger, { relatedTarget: popoverLink })

    expect(container.querySelector('.citation-popover')).not.toBeNull()
  })

  it('closes the popover when blur moves focus outside the bubble', () => {
    render(<CitationBubble citations={[ONE, TWO]} />)
    const trigger = screen.getByRole('button', { name: /Source A \+1/ })

    fireEvent.focus(trigger)
    fireEvent.blur(trigger, { relatedTarget: document.body })

    expect(screen.queryByRole('region', { name: 'Sources' })).toBeNull()
  })
})
