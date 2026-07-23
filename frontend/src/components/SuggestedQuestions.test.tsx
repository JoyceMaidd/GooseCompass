import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SuggestedQuestions } from './SuggestedQuestions'

describe('SuggestedQuestions', () => {
  it('renders each question exactly once in the accessible tree', () => {
    render(<SuggestedQuestions onSelect={vi.fn()} />)

    expect(screen.getAllByRole('button', { name: 'How do I apply for an exchange program?' })).toHaveLength(1)
    expect(screen.getAllByRole('button', { name: "What's the application deadline?" })).toHaveLength(1)
  })

  it('calls onSelect with the exact question text when a pill is clicked', async () => {
    const onSelect = vi.fn()
    render(<SuggestedQuestions onSelect={onSelect} />)

    await userEvent.click(screen.getByRole('button', { name: 'I want to study abroad, what should I do?' }))

    expect(onSelect).toHaveBeenCalledWith('I want to study abroad, what should I do?')
  })

  it('hides duplicate marquee pills from assistive tech', () => {
    render(<SuggestedQuestions onSelect={vi.fn()} />)

    const allPills = screen.getAllByText('Do I need a visa for my exchange?')
    expect(allPills).toHaveLength(2)
    expect(allPills.some(el => el.getAttribute('aria-hidden') === 'true')).toBe(true)
  })
})
