import { useState, type KeyboardEvent } from 'react'

interface ChatInputProps {
  onSubmit: (query: string) => void
  disabled: boolean
}

/**
 * Text input area for submitting chat queries.
 *
 * Pressing Enter submits the query and clears the field.
 * Shift+Enter inserts a newline without submitting.
 * The input and button are both disabled while `disabled` is true.
 *
 * @param props.onSubmit - Called with the trimmed query string on submission.
 * @param props.disabled - When true, prevents input and submission.
 */
export function ChatInput({ onSubmit, disabled }: ChatInputProps) {
  const [value, setValue] = useState('')

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  function submit() {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSubmit(trimmed)
    setValue('')
  }

  return (
    <div className="chat-input">
      <textarea
        className="chat-input__textarea"
        value={value}
        onChange={e => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="Ask a question about your exchange..."
        rows={1}
      />
      <button
        className="chat-input__submit"
        onClick={submit}
        disabled={disabled || !value.trim()}
        aria-label="Send"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <path d="M8 13V3M8 3L3.5 7.5M8 3l4.5 4.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
    </div>
  )
}
