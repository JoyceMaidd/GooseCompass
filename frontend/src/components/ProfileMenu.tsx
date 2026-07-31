import { useState, type FocusEvent } from 'react'
import { ProfileIcon } from './ProfileIcon'

interface ProfileMenuProps {
  email: string
  onSignOut: () => void
}

/**
 * Avatar trigger in the chat header that opens a dropdown with account info
 * and a sign-out action.
 *
 * Click-triggered rather than hover-triggered (unlike the citation popover)
 * since a menu with a sign-out action shouldn't open on incidental hover.
 * Closes via the same blur-containment technique as CitationBubble so it
 * still works for keyboard users, without a global document click listener.
 *
 * @param props.email - Signed-in user's email, shown in the dropdown header.
 * @param props.onSignOut - Called when "Log out" is selected.
 */
export function ProfileMenu({ email, onSignOut }: ProfileMenuProps) {
  const [isOpen, setIsOpen] = useState(false)

  function handleBlur(e: FocusEvent<HTMLDivElement>) {
    if (!e.currentTarget.contains(e.relatedTarget as Node)) setIsOpen(false)
  }

  function handleSignOut() {
    setIsOpen(false)
    onSignOut()
  }

  return (
    <div className="profile-menu" onBlur={handleBlur}>
      <button
        type="button"
        className="profile-menu__avatar"
        aria-haspopup="true"
        aria-expanded={isOpen}
        aria-label="Account menu"
        onClick={() => setIsOpen(open => !open)}
      >
        <ProfileIcon />
      </button>
      {isOpen && (
        <div className="profile-menu__dropdown" role="menu">
          {email && <p className="profile-menu__email">Signed in as {email}</p>}
          <button type="button" className="profile-menu__logout" role="menuitem" onClick={handleSignOut}>
            Log out
          </button>
        </div>
      )}
    </div>
  )
}
