## Overview

GooseCompass is a warm, editorial chat interface for University of Waterloo exchange students. The visual language is **watercolor + cream** — a warm off-white canvas that evokes academic print materials, paired with a **dark forest green** brand color that signals trust and institutional weight without being corporate. The illustration of a Canada goose and gosling standing on a globe anchors the brand personality: friendly, curious, and distinctly Waterloo.

The layout is a **two-panel split** at desktop: a calm, illustration-first branding panel on the left and a focused chat panel on the right. The split lets the illustration breathe while keeping the interaction surface uncluttered.

Chat surfaces use a **white card over cream canvas** pattern — AI responses appear in white floating bubbles, user messages in a muted slate-blue, and all citation and source elements are rendered in a lower-contrast teal to stay present but non-intrusive.

**Key Characteristics:**
- White canvas as the default page background. Cream, not white — reads as warm and academic rather than sterile.
- Dark forest green primary on the wordmark, subtitle, and send button. The dominant brand signal.
- Muted slate-blue user bubbles. Neutral enough to not compete with response text; distinct from the AI bubble.
- Cream AI response bubbles with a soft drop shadow — crisp and readable over the cream canvas.
- Watercolor illustration as brand asset: Canada goose + gosling on a globe with soft clouds. Line-art watercolor, never photorealistic. The illustration is the only decorative element.
- Inline citation chips (`{component.citation-chip}`) and a bottom source bar keep provenance always visible.
- Border radius is uniformly generous: `{rounded.lg}` (16px) on message bubbles and the chat panel, `{rounded.full}` on the send button.
- Disclaimer line below the input reinforces the RAG system's honest grounding: "GooseCompass may make mistakes. Please verify important information."

## Colors

### Brand & Accent
- **Forest Green / Primary** (`{colors.primary}` — #3B493F): The GooseCompass signature color. Used on the wordmark, subtitle text, and the send button. Deep, trustworthy, and distinctly Waterloo (echoes the university's green).
- **Online Green** (`{colors.status-online}` — #3AC642): The small dot next to "Online" in the chat header. Signal-green — unmistakable, not decorative.
- **Citation Teal** (`{colors.citation}` — #92A9AC): Inline citation chips and source link text. Lower contrast than primary — present but not demanding.

### Surface
- **Canvas** (`{colors.canvas}` — #FDFCFB): Default page background. Warm cream — the defining non-white of the brand.
- **Surface AI Bubble** (`{colors.bubble-ai}` — #F8F8F0): AI response message cards. Cream white.
- **Surface User Bubble** (`{colors.bubble-user}` — #E7F1F1): User message cards. Muted slate-blue — visually distinct from AI without high contrast.
- **Surface Input** (`{colors.surface-input}` — #fefefe): The message input field. White, with a subtle border.
- **Hairline** (`{colors.hairline}` — #FCFCFC): 1px borders on the input field and chat panel edges.
- **Submit Button** (`{colors.submit}` - #8DA9A7): The button for submission.

### Text
- **Ink** (`{colors.ink}` — #39483E): Headlines primary, and secondary text in the branding panel. Dark forest, slightly off-black.
- **Body** (`{colors.body}` — #2D2D2E): Text in conversation.
- **Muted** (`{colors.muted}` — #999DA0): Timestamp labels, disclaimer text. Sub-information, never competes with message content.
- **Citation Text** (`{colors.citation-text}` — #8DA9A7): Inline `[1]` chip labels and source attribution links.

### Semantic
- **Success** (`{colors.success}` — #4ade80): Online status dot.

## Typography

### Font Family
The system uses a clean humanist sans-serif throughout — no display serif. This keeps the interface feeling lightweight and approachable for a student audience. The wordmark "GooseCompass" and introduction sentence use Lora.

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
No serif display face. The brand warmth comes from the illustration and the cream canvas, not from typography. All text stays humanist sans at consistent weights. The wordmark is bold but not tracked — tight and confident. Body text in messages uses weight 400 for both user and AI turns; the bubble color alone differentiates speaker.

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
- **Source bar:** full-width strip pinned to the bottom of the chat panel, above the input.

### Whitespace Philosophy
The left branding panel is generous and uncrowded — the illustration needs breathing room. The right chat panel is task-focused, with tighter spacing between UI chrome (header, input bar) and more relaxed spacing in the message stream itself.

## Elevation & Depth

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Canvas, branding panel, chat background |
| Hairline | 1px `{colors.hairline}` border | Input field, chat panel outer edge |
| AI bubble | `0 1px 4px rgba(0,0,0,0.08)` | White AI response cards — subtle lift off canvas |
| Send button | No shadow | Dark green circle; color provides enough affordance |

The elevation philosophy is **color + canvas contrast first**. The white AI bubble reads as elevated against the cream canvas purely through color; shadows are minimal. The user bubble (slate-blue) has no shadow — the color is its own signal.

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

**`bubble-ai`** — Left-aligned card. Background `{colors.bubble-ai}` (#ffffff), text `{colors.on-bubble-ai}`, `{typography.message}`, padding 12px × 16px, `{rounded.lg}` (16px), soft drop shadow `0 1px 4px rgba(0,0,0,0.08)`. Inline citation chips appear inside the bubble text flow. A timestamp in `{typography.timestamp}` and `{colors.muted}` sits below the bubble, left-aligned.

**`bubble-user`** — Right-aligned card. Background `{colors.bubble-user}` (#8fa3b8), text `{colors.on-bubble-user}` (white), same padding, radius, and shadow as `bubble-ai`. Timestamp sits below, right-aligned.

### Citation Elements

**`citation-chip`** — Inline element inside AI bubble text. Small rounded chip: `[1]` number in `{typography.citation-chip}`, background a light teal tint (~#d6eaf2), text `{colors.citation-text}`, `{rounded.md}` (12px), padding 1px × 6px. Appears immediately after the cited sentence, inline.

**`source-bar`** — A full-width strip pinned between the message stream and the input area. Light background (slightly darker cream, ~`{colors.hairline}`). Numbered source entries: `[1]` index + hyperlinked document title in `{colors.citation-text}` + external link icon (↗). `{typography.source-label}`. Multiple sources stack vertically within the bar.

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

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 768px | Branding panel hides entirely; chat panel goes full-screen; illustration moved to a small icon in the chat header |
| Tablet | 768–1024px | Branding panel collapses to a narrow strip showing wordmark only, no illustration; chat panel takes ~70% |
| Desktop | > 1024px | Full two-panel split: ~40% branding / ~60% chat |

### Touch Targets
- `{component.button-send}` at exactly 40 × 40px — meets minimum tap target.
- `{component.button-new-chat}` at minimum 36px height — provide extra padding on mobile.
- `{component.citation-chip}` is non-interactive on mobile (inline display only); the `{component.source-bar}` link is the tappable target.

### Collapsing Strategy
- On mobile, the chat panel expands to full viewport. The "GooseCompass" wordmark moves to the top nav bar as a smaller label (weight 600, `{typography.chat-header}`).
- Message bubbles expand to ~90% width of the panel on mobile rather than the 70–80% desktop cap.
- The source bar stacks vertically — each source on its own line, no truncation.

## Known Gaps

- Dark mode is not specified. The cream canvas + watercolor illustration do not have dark variants defined.
- The citation chip interaction on desktop (hover/focus state, whether it links to an anchor or opens a popover) is not specified in the current design.
- Loading / streaming state for AI response bubbles (typing indicator, progressive token reveal) is not shown in the reference frame.
- Error states (no results found, API failure) are not captured in the design — those message variants need separate design treatment.
- The "New Chat" flow (whether it clears the panel, opens a new tab, or routes to a fresh session) is not specified.
- Multi-source scenarios with more than 3 citations per response may need a collapsed/expanded source bar design.