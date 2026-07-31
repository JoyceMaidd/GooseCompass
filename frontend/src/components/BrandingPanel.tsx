/**
 * Left-side branding panel on the sign-in page: wordmark + tagline only.
 *
 * No illustration (per DESIGN.md spec, deliberately left out rather than
 * filled with a placeholder) and no interactive chrome, per the
 * "illustration canvas only" rule.
 */
export function BrandingPanel() {
  return (
    <div className="branding-panel">
      <h1 className="branding-panel__wordmark">GooseCompass</h1>
      <p className="branding-panel__tagline">Your AI study companion for exchange at Waterloo</p>
    </div>
  )
}
