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
- **Citation Text** (`{colors.citation-text}` — #8DA9A7): Inline citation pill labels and source attribution links.

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
| `{typography.citation-chip}` | 13px | 500 | 1.0 | 0 | Citation pill label (source title, or "title +N") |
| `{typography.source-label}` | 13px | 500 | 1.4 | 0 | Source title inside a citation popover's `citation-item` row |
| `{typography.disclaimer}` | 12px | 400 | 1.4 | 0 | "GooseCompass may make mistakes…" line |
| `{typography.button-label}` | 13px | 500 | 1.0 | 0 | "New Chat +" button label |
| `{typography.input-placeholder}` | 15px | 400 | 1.55 | 0 | "Ask anything about exchange at Waterloo…" |
| `{typography.empty-title}` | 20px | 600 | 1.4 | 0 | Landing hero title, "Ask anything about your UWaterloo exchange" |
| `{typography.empty-subtitle}` | 14px | 400 | 1.4 | 0 | Landing hero subtitle, "Start your journey here" |

### Principles
Lora is only for the branding panel (left side). All chat panel text uses system-ui / Inter. Body text in messages uses weight 400 for both turns; bubble color differentiates speaker.

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
| `{rounded.md}` | 12px | Citation popover panel |
| `{rounded.lg}` | 16px | AI and user message bubbles, chat panel container |
| `{rounded.full}` | 9999px | Send button (circular), online status dot, citation pill, hero question pill |


## Components

### Chat Panel Header

**`chat-header`** — 56px tall bar spanning the full width of the chat panel. `{colors.canvas}` background with a `{colors.hairline}` bottom border. Left side: "GooseCompass" in `{typography.chat-header}` with a `{colors.status-online}` dot and "Online" label in `{typography.timestamp}`. Right side: `{component.button-new-chat}`.

### Buttons

**`button-new-chat`** — Small outlined button: "New Chat +" label, `{colors.canvas}` background, `{colors.hairline}` border, `{colors.ink}` text, `{rounded.sm}` (8px), padding 6px × 14px, `{typography.button-label}`.

**`button-send`** — Circular send button, 40px diameter. Background `{colors.primary}` (forest green), white arrow icon centered, `{rounded.full}`. No label.

### Message Bubbles

**`bubble-ai`** — Left-aligned card. Background `{colors.bubble-ai}` (#F8F8F0), text `{colors.body}` (#2D2D2E), `{typography.message}`, padding 12px × 16px, `{rounded.lg}` (16px), soft drop shadow `0 1px 4px rgba(0,0,0,0.08)`. Inline citation pills appear inside the bubble text flow. A timestamp in `{typography.timestamp}` and `{colors.muted}` sits below the bubble, left-aligned.

**`bubble-user`** — Right-aligned card. Background `{colors.bubble-user}` (#E7F1F1), text `{colors.body}` (#2D2D2E), same padding, radius, and shadow as `bubble-ai`. Timestamp sits below, right-aligned.

### Landing Hero

**`hero-question-pill`** — Example-question chip shown beneath the landing subtitle, before any conversation starts. Background `{colors.bubble-ai}` (#F8F8F0), 1px `{colors.hairline}` border, text `{colors.ink}`, `{rounded.full}` (9999px), padding 8px × 16px, `{typography.button-label}` scale (13px/500). Unlike message bubbles, this is a real interactive button: on hover it takes a light `{colors.citation-bg}` tint and the AI-bubble elevation shadow (`0 1px 4px rgba(0,0,0,0.08)`). Clicking a pill sends its question immediately.

**`suggested-questions-marquee`** — Two `hero-question-pill` rows drifting slowly and continuously in opposite directions (one leftward, one rightward), each row pausing on hover so a pill can be read and clicked without drifting away. The row edges fade via a mask-image gradient rather than clipping abruptly. Motion is disabled under `prefers-reduced-motion: reduce`.

### Citation Elements

**`citation-pill`** — Inline element at the end of a cited paragraph. A single citation renders as a direct link styled as a small rounded pill; multiple citations render as a "first title +N" trigger. Background `{colors.citation-bg}` (#d6eaf2), text `{colors.citation-text}`, `{rounded.full}` (999px), padding 4px × 10px, `{typography.citation-chip}`, includes a small document icon. Opens a `citation-popover` on **both** hover and keyboard focus.

**`citation-popover`** — Floating panel anchored above or below its trigger pill depending on available viewport space (300px wide, scrolls internally past 320px tall). `{rounded.md}` (12px), `{colors.surface-input}` background, `{colors.hairline}` border, elevated shadow `0 4px 16px rgba(0,0,0,0.12)`. Entrance animation: 180ms ease-out, opacity + a small `translateY` (6px from the side it emerges from). Lists every source as a `citation-item` — document icon, full title, snippet, and a "View source →" link — never truncated or abbreviated. An invisible hover-bridge spacer between the pill and the panel keeps the popover open while the cursor crosses the gap.

### Input Area

**`message-input`** — Full-width text field inside the input zone. Background `{colors.surface-input}` (#ffffff), 1px `{colors.hairline}` border, `{rounded.sm}` (8px), height 48px, padding 12px × 16px. Placeholder text in `{colors.muted}`, `{typography.input-placeholder}`.

**`disclaimer`** — Single line of text centered below the input area. `{typography.disclaimer}`, `{colors.muted}`. "GooseCompass may make mistakes. Please verify important information." Always visible — never hidden.

### Branding Panel

**`brand-panel`** — Left ~40% of the viewport. Background `{colors.canvas}`. Top-left: wordmark "GooseCompass" in `{typography.brand-name}` (`{colors.ink}`), followed by the tagline in `{typography.brand-tagline}` (`{colors.body}`). Centered in the panel: the watercolor illustration at its natural proportions, no card or border around it. No nav, no buttons, no other chrome.

## Do's and Don'ts

### Do
- Keep the branding panel free of interactive elements. It is an illustration canvas only.
- Use the Canada goose illustration as the sole decorative asset. No abstract shapes, gradients, or pattern fills.
- Show citation pills inline in AI response text — never footnote-only. The connection between claim and source must be visible in the message itself.
- Keep the disclaimer visible at all times below the input. This is a non-negotiable transparency signal.
- Use `{colors.primary}` (forest green) only on the wordmark and send button. Don't use it on interactive labels or body text in the chat panel.

### Don't
- Don't use pure white (`#ffffff`) as the canvas background. The cream is the brand's warmth signal.
- Don't introduce a second illustration or decorative image. One watercolor asset is the rule.
- Don't make a citation's sources reveal on click-only. Both hover **and** keyboard focus must open the popover, and it must list full document titles — never truncated or abbreviated.
- Don't use the forest green (`{colors.primary}`) for message text in either bubble type — it creates ambiguity with citation-teal links.
- Don't use a serif font for any element in the chat panel. The editorial warmth comes from canvas and illustration, not type.
- Don't add hover effects to message bubbles. Interactive states are reserved for actual controls — the send button, "New Chat" button, citation pills, and hero question pills.