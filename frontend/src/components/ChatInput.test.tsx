import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatInput } from './ChatInput'

describe('ChatInput', () => {
  it('calls onSubmit with the typed text when Enter is pressed', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} disabled={false} />)

    await userEvent.type(screen.getByRole('textbox'), 'What GPA do I need?{Enter}')

    expect(onSubmit).toHaveBeenCalledOnce()
    expect(onSubmit).toHaveBeenCalledWith('What GPA do I need?')
  })

  it('clears the textarea after submission', async () => {
    render(<ChatInput onSubmit={vi.fn()} disabled={false} />)
    const textarea = screen.getByRole('textbox')

    await userEvent.type(textarea, 'My question{Enter}')

    expect(textarea).toHaveValue('')
  })

  it('does not submit on Shift+Enter — inserts newline instead', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} disabled={false} />)

    await userEvent.type(screen.getByRole('textbox'), 'line one{Shift>}{Enter}{/Shift}line two')

    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('does not submit empty or whitespace-only input', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} disabled={false} />)

    await userEvent.type(screen.getByRole('textbox'), '   {Enter}')

    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('disables textarea and button when disabled prop is true', () => {
    render(<ChatInput onSubmit={vi.fn()} disabled={true} />)

    expect(screen.getByRole('textbox')).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
  })

  it('calls onSubmit when Send button is clicked', async () => {
    const onSubmit = vi.fn()
    render(<ChatInput onSubmit={onSubmit} disabled={false} />)

    await userEvent.type(screen.getByRole('textbox'), 'Button submit test')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))

    expect(onSubmit).toHaveBeenCalledWith('Button submit test')
  })
})
