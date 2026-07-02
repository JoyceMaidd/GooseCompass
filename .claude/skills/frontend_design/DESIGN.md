## Colors

### Brand & Accent
- **Forest Green / Primary** (`{colors.primary}` — #3B493F): The GooseCompass signature color. Used on the wordmark, subtitle text, and the send button.
- **Online Green** (`{colors.status-online}` — #3AC642): The small dot next to "Online" in the chat header.

### Surface
- **Canvas** (`{colors.canvas}` — #FDFCFB): Default page background. Warm cream — the defining non-white of the brand.
- **Surface AI Bubble** (`{colors.bubble-ai}` — #F8F8F0): AI response message cards. Cream white.
- **Surface User Bubble** (`{colors.bubble-user}` — #E7F1F1): User message cards. Muted pale teal-blue; text color is dark (`{colors.body}`).
- **Surface Input** (`{colors.surface-input}` — #fefefe): The message input field. White, with a subtle border.
- **Hairline** (`{colors.hairline}` — #EBEBEB): 1px borders on the input field and chat panel edges. Use a visible light gray so borders are perceivable.

### Text
- **Ink** (`{colors.ink}` — #39483E): Headlines primary, and secondary text in the branding panel. Dark forest, slightly off-black.
- **Body** (`{colors.body}` — #2D2D2E): Text in conversation.
- **Muted** (`{colors.muted}` — #999DA0): Timestamp labels, disclaimer text. Sub-information, never competes with message content.
- **Citation Text** (`{colors.citation-text}` — #8DA9A7): Inline `[1]` chip labels and source attribution links.

### Semantic
- **Success** (`{colors.success}` — #4ade80): Online status dot.

## Typography

### Font Family
The system uses a clean humanist sans-serif (system-ui / Inter) throughout. Exception: the left-panel wordmark "GooseCompass" and tagline use **Lora** (Google Fonts, weight 400 and 700). Import: `https://fonts.googleapis.com/css2?family=Lora:wght@400;700&display=swap`.

### Hierarchy

| Token | Size | Weight | Line Height | Letter Spacing | Use |
|---|---|---|---|---|---|
| `{typography.brand-name}` | 36px | 700 | 1.1 | -0.5px | "GooseCompass" wordmark in the branding panel |
| `{typography.brand-tagline}` | 16px | 400 | 1.5 | 0 | "Your AI study companion…" subtitle |
| `{typography.chat-header}` | 16px | 600 | 1.2 | 0 | "GooseCompass" label in the chat panel header |
| `{typography.message}` | 15px | 400 | 1.55 | 0 | Message body text in both bubbles |
| `{typography.timestamp}` | 12px | 400 | 1.4 | 0 | Time labels below messages |
| `{typography.citation-chip}` | 12px | 500 | 1.0 | 0 | Inline `[1]` citation number inside a chip |
| `{typography.source-label}` | 13px | 400 | 1.4 | 0 | Source attribution line at the bottom of the chat panel |
| `{typography.disclaimer}` | 12px | 400 | 1.4 | 0 | "GooseCompass may make mistakes…" line |
| `{typography.button-label}` | 13px | 500 | 1.0 | 0 | "New Chat +" button label |
| `{typography.input-placeholder}` | 15px | 400 | 1.55 | 0 | "Ask anything about exchange at Waterloo…" |

### Principles
Lora is only for the branding panel (left side). All chat panel text uses system-ui / Inter. Body text in messages uses weight 400 for both turns; bubble color differentiates speaker.

## Layout

### Spacing System
- **Base unit:** 4px.
- **Tokens:** `{spacing.xs}` 4px · `{spacing.sm}` 8px · `{spacing.md}` 12px · `{spacing.lg}` 16px · `{spacing.xl}` 24px · `{spacing.xxl}` 32px.
- **Chat panel internal padding:** `{spacing.xl}` (24px) horizontal, `{spacing.lg}` (16px) vertical.
- **Message bubble padding:** `{spacing.lg}` (16px) horizontal, `{spacing.md}` (12px) vertical.
- **Message gap:** `{spacing.xl}` (24px) between consecutive turns.
- **Header height:** 56px — compact but gives the status dot and "New Chat" button enough room.
- **Input area padding:** `{spacing.lg}` (16px) all sides.

### Grid & Container
- **Two-panel split at desktop:** Left panel ~40% width (branding + illustration), right panel ~60% (chat). The split is not equal — the chat panel is wider.
- **Chat panel max width:** ~720px. Centering it inside the right half keeps line lengths comfortable.
- **Message bubbles:** AI bubbles left-aligned, max-width ~80% of chat panel. User bubbles right-aligned, max-width ~70%.
- **Source bar:** full-width strip pinned at the very bottom of the chat card, below the disclaimer.

## Elevation & Depth

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Canvas, branding panel, chat background |
| Hairline | 1px `{colors.hairline}` border | Input field, chat panel outer edge |
| AI bubble | `0 1px 4px rgba(0,0,0,0.08)` | White AI response cards — subtle lift off canvas |
| Send button | No shadow | Dark green circle; color provides enough affordance |

The elevation philosophy is **color + canvas contrast first**. The AI bubble reads as elevated against the cream canvas purely through color; shadows are minimal. The user bubble has no shadow — the color is its own signal.

## Shapes

### Border Radius Scale

| Token | Value | Use |
|---|---|---|
| `{rounded.sm}` | 8px | "New Chat" button, input field |
| `{rounded.md}` | 12px | Citation chip, source bar |
| `{rounded.lg}` | 16px | AI and user message bubbles, chat panel container |
| `{rounded.full}` | 9999px | Send button (circular), online status dot |

### Illustration
The brand illustration is a watercolor painting of a Canada goose (adult) and gosling standing on a globe, with soft watercolor clouds. Style: loose brush strokes, muted warm pigments, no hard outlines. It is the only illustration in the product — it appears only in the left branding panel and should never be tiled, scaled to icon size, or reproduced in dark contexts.

## Components

### Chat Panel Header

**`chat-header`** — 56px tall bar spanning the full width of the chat panel. `{colors.canvas}` background with a `{colors.hairline}` bottom border. Left side: "GooseCompass" in `{typography.chat-header}` with a `{colors.status-online}` dot and "Online" label in `{typography.timestamp}`. Right side: `{component.button-new-chat}`.

### Buttons

**`button-new-chat`** — Small outlined button: "New Chat +" label, `{colors.canvas}` background, `{colors.hairline}` border, `{colors.ink}` text, `{rounded.sm}` (8px), padding 6px × 14px, `{typography.button-label}`.

**`button-send`** — Circular send button, 40px diameter. Background `{colors.primary}` (forest green), white arrow icon centered, `{rounded.full}`. No label.

### Message Bubbles

**`bubble-ai`** — Left-aligned card. Background `{colors.bubble-ai}` (#F8F8F0), text `{colors.body}` (#2D2D2E), `{typography.message}`, padding 12px × 16px, `{rounded.lg}` (16px), soft drop shadow `0 1px 4px rgba(0,0,0,0.08)`. Inline citation chips appear inside the bubble text flow. A timestamp in `{typography.timestamp}` and `{colors.muted}` sits below the bubble, left-aligned.

**`bubble-user`** — Right-aligned card. Background `{colors.bubble-user}` (#E7F1F1), text `{colors.body}` (#2D2D2E), same padding, radius, and shadow as `bubble-ai`. Timestamp sits below, right-aligned.

### Citation Elements

**`citation-chip`** — Inline element inside AI bubble text. Small rounded chip: `[1]` number in `{typography.citation-chip}`, background a light teal tint (~#d6eaf2), text `{colors.citation-text}`, `{rounded.md}` (12px), padding 1px × 6px. Appears immediately after the cited sentence, inline.

**`source-bar`** — A full-width strip pinned at the **very bottom** of the chat card, below the disclaimer. Light background (slightly darker cream). Numbered source entries: `[1]` index + hyperlinked document title in `{colors.citation-text}` + external link icon (↗). `{typography.source-label}`. Multiple sources stack vertically.

### Input Area

**`message-input`** — Full-width text field inside the input zone. Background `{colors.surface-input}` (#ffffff), 1px `{colors.hairline}` border, `{rounded.sm}` (8px), height 48px, padding 12px × 16px. Placeholder text in `{colors.muted}`, `{typography.input-placeholder}`.

**`disclaimer`** — Single line of text centered below the input area. `{typography.disclaimer}`, `{colors.muted}`. "GooseCompass may make mistakes. Please verify important information." Always visible — never hidden.

### Branding Panel

**`brand-panel`** — Left ~40% of the viewport. Background `{colors.canvas}`. Top-left: wordmark "GooseCompass" in `{typography.brand-name}` (`{colors.ink}`), followed by the tagline in `{typography.brand-tagline}` (`{colors.body}`). Centered in the panel: the watercolor illustration at its natural proportions, no card or border around it. No nav, no buttons, no other chrome.

## Do's and Don'ts

### Do
- Keep the branding panel free of interactive elements. It is an illustration canvas only.
- Use the Canada goose illustration as the sole decorative asset. No abstract shapes, gradients, or pattern fills.
- Show citation chips inline in AI response text — never footnote-only. The connection between claim and source must be visible in the message itself.
- Keep the disclaimer visible at all times below the input. This is a non-negotiable transparency signal.
- Use `{colors.primary}` (forest green) only on the wordmark and send button. Don't use it on interactive labels or body text in the chat panel.
- Right-align user bubbles. Left-align AI bubbles. Never center either.

### Don't
- Don't use pure white (`#ffffff`) as the canvas background. The cream is the brand's warmth signal.
- Don't introduce a second illustration or decorative image. One watercolor asset is the rule.
- Don't hide or abbreviate the source bar when citations exist. Full document titles with external-link icons are required.
- Don't use the forest green (`{colors.primary}`) for message text in either bubble type — it creates ambiguity with citation-teal links.
- Don't use a serif font for any element in the chat panel. The editorial warmth comes from canvas and illustration, not type.
- Don't add hover effects to message bubbles. Only the send button and "New Chat" button have interactive states.

## Responsive Behavior

See `FRONTEND.md` for full breakpoint specs. Touch target minimums:
- Send button: 40 × 40px.
- New Chat button: min 36px height.
- Citation chips are non-interactive on mobile; the source-bar link is the tappable target.