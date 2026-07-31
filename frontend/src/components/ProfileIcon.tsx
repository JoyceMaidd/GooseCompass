/**
 * Generic person-outline glyph used as the profile avatar indicator.
 *
 * Rendered with white strokes on a filled primary-green circle background,
 * mirroring the structure of DocumentIcon.
 */
export function ProfileIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="8" r="4" stroke="white" strokeWidth="1.6" />
      <path d="M4 20c0-4.4 3.6-7 8-7s8 2.6 8 7" stroke="white" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  )
}
