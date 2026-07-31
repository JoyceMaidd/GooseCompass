import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ProfileMenu } from './ProfileMenu'

beforeEach(() => {
  vi.clearAllMocks()
})

describe('ProfileMenu', () => {
  it('renders the avatar button closed by default', () => {
    render(<ProfileMenu email="test@uwaterloo.ca" onSignOut={vi.fn()} />)
    const button = screen.getByRole('button', { name: /Account menu/i })
    expect(button).toBeInTheDocument()
    expect(button).toHaveAttribute('aria-expanded', 'false')
  })

  it('opens the dropdown when the avatar is clicked', async () => {
    render(<ProfileMenu email="test@uwaterloo.ca" onSignOut={vi.fn()} />)
    const button = screen.getByRole('button', { name: /Account menu/i })

    await userEvent.click(button)

    expect(button).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByText(/Signed in as test@uwaterloo\.ca/)).toBeInTheDocument()
  })

  it('shows the log out button in the dropdown when open', async () => {
    render(<ProfileMenu email="test@uwaterloo.ca" onSignOut={vi.fn()} />)

    await userEvent.click(screen.getByRole('button', { name: /Account menu/i }))

    expect(screen.getByRole('menuitem', { name: /Log out/i })).toBeInTheDocument()
  })

  it('does not render the email line when email is empty', async () => {
    render(<ProfileMenu email="" onSignOut={vi.fn()} />)

    await userEvent.click(screen.getByRole('button', { name: /Account menu/i }))

    expect(screen.queryByText(/Signed in as/i)).not.toBeInTheDocument()
    expect(screen.getByRole('menuitem', { name: /Log out/i })).toBeInTheDocument()
  })

  it('closes the dropdown and calls onSignOut when Log out is clicked', async () => {
    const onSignOut = vi.fn()
    render(<ProfileMenu email="test@uwaterloo.ca" onSignOut={onSignOut} />)

    await userEvent.click(screen.getByRole('button', { name: /Account menu/i }))
    const logoutButton = screen.getByRole('menuitem', { name: /Log out/i })

    await userEvent.click(logoutButton)

    expect(onSignOut).toHaveBeenCalledOnce()
    expect(screen.getByRole('button', { name: /Account menu/i })).toHaveAttribute('aria-expanded', 'false')
  })

  it('closes the dropdown when focus moves outside', async () => {
    render(
      <div>
        <ProfileMenu email="test@uwaterloo.ca" onSignOut={vi.fn()} />
        <button>Outside</button>
      </div>
    )

    const avatarButton = screen.getByRole('button', { name: /Account menu/i })
    const outsideButton = screen.getByRole('button', { name: /Outside/i })

    await userEvent.click(avatarButton)
    expect(avatarButton).toHaveAttribute('aria-expanded', 'true')

    await userEvent.click(outsideButton)
    expect(avatarButton).toHaveAttribute('aria-expanded', 'false')
  })

  it('toggles the dropdown on repeated clicks', async () => {
    render(<ProfileMenu email="test@uwaterloo.ca" onSignOut={vi.fn()} />)
    const button = screen.getByRole('button', { name: /Account menu/i })

    await userEvent.click(button)
    expect(button).toHaveAttribute('aria-expanded', 'true')

    await userEvent.click(button)
    expect(button).toHaveAttribute('aria-expanded', 'false')

    await userEvent.click(button)
    expect(button).toHaveAttribute('aria-expanded', 'true')
  })
})
