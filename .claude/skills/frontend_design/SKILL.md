## Purpose

This document describes how the GooseCompass landing page should be implemented. It complements `DESIGN.md`, which defines the visual design system (colors, typography, spacing, components, etc.). This document focuses on page structure, layout, positioning, assets, responsiveness, and implementation recommendations.

The goal is to recreate the provided design as closely as possible while keeping the implementation responsive, maintainable, and component-based.

---

# General Principles

* Build the interface using semantic HTML and CSS (or Tailwind CSS).
* Do **not** recreate the page as one large background image.
* Only use image assets for decorative illustrations:

  * watercolor background (PNG)
  * globe (SVG)
  * mother goose (SVG)
  * gosling (SVG)
* All text, chat messages, buttons, citations, and inputs should be real HTML elements.
* The page should remain responsive across desktop and mobile devices.
* The design should feel light, airy, and uncluttered.

---

# Overall Layout

The application consists of a **single full-screen page**.

Desktop layout:

```
+---------------------------------------------------------------+
|                                                               |
|   Hero Section (40%)        |      Chat Interface (60%)       |
|                             |                                 |
|                             |                                 |
|                             |                                 |
|                             |                                 |
|                             |                                 |
+---------------------------------------------------------------+
```

The page occupies the full viewport.

```
width: 100vw
height: 100vh
overflow: hidden
```

Use Flexbox for the main layout.

```css
display: flex;
```

Recommended proportions:

* Left panel: 40%
* Right panel: 60%

The divider between the two sections should not be visually obvious. The layout should feel open rather than split.

---

# Background

The watercolor paper texture should be implemented as a page background.

The PNG should contain only decorative artwork such as:

* watercolor texture
* subtle clouds
* soft paper grain

The background should **not** include:

* globe
* goose
* text
* chat interface

Recommended CSS:

```
background-size: cover;
background-position: center;
background-repeat: no-repeat;
```

The background should remain fixed while the content scrolls (if scrolling is ever introduced).

---

# Left Hero Section

The left section serves as branding and visual identity.

Layout:

```
+------------------------------------+

GooseCompass

Short description

           (large empty space)

          Goose
      Gosling

   Top half of Globe

+------------------------------------+
```

The hero section should use a vertical Flexbox layout.

```
display: flex;
flex-direction: column;
justify-content: space-between;
```

This naturally places the branding near the top and the illustration near the bottom.

---

# Hero Content

Contains only:

* Project title
* One-line description

No navigation bar.

No buttons.

No feature list.

No decorative icons.

Leave generous whitespace around the text.

The text should be left-aligned.

---

# Illustration

The illustration is composed from **three separate SVG assets**.

```
Hero Illustration

├── Globe
├── Mother Goose
└── Gosling
```

These should be placed inside a single relative container.

```
position: relative;
```

The globe is the base layer.

The goose and gosling are absolutely positioned above the globe.

```
Hero Illustration

relative

    Globe

    Goose
      absolute

    Gosling
      absolute
```

---

# Globe

The globe should remain **completely static**.

No rotation.

No floating animation.

No scaling.

Only the **top half** of the globe should be visible.

The lower half should extend beyond the bottom edge of the viewport so that the globe appears much larger than the screen.

Example:

```
Viewport

---------------------------

      Goose

   _____________
  /             \
 /               \
|                 |

-------------------
(bottom of screen)
```

Approximately 45–55% of the globe should be hidden below the viewport.

The globe should be horizontally centered within the hero illustration.

---

# Mother Goose

The mother goose stands on top of the globe.

Requirements:

* facing right
* upright
* no rotation
* no animation
* SVG should preserve transparency

Position:

approximately centered horizontally on the visible globe.

---

# Gosling

The gosling follows behind the mother goose.

Requirements:

* facing right
* positioned slightly behind
* slightly lower than the mother goose
* approximately 20–30% of the mother's size

Maintain consistent spacing between the two birds.

---

# Illustration Layer Order

The z-index order should be:

```
Background PNG

↓

Globe

↓

Mother Goose

↓

Gosling

↓

Text
```

Nothing should overlap the project title.

---

# Right Chat Panel

The right side contains a single rounded chat container.

The chat container is **not** full width.

It should have generous margins from the viewport.

Recommended:

```
Top margin

24–32px

Left margin

24px

Right margin

24px

Bottom margin

24px
```

The container should nearly fill the available height.

---

# Chat Container Layout

The chat card uses a vertical layout.

```
Header

↓

Conversation

↓

Input

↓

Citation List
```

Use Flexbox.

```
display: flex;
flex-direction: column;
```

The conversation area should grow automatically.

```
flex: 1;
```

---

# Header

Contains:

* GooseCompass title
* Online indicator
* "New Chat" button

The header remains fixed inside the chat card.

Do not allow messages to scroll over the header.

---

# Conversation Area

The conversation occupies the majority of the card.

Messages should scroll vertically if necessary.

Horizontal scrolling should never occur.

Use consistent spacing between messages.

---

# User Messages

User messages:

* aligned right
* rounded rectangle
* fixed maximum width (~65% of container)

Never span the full width.

---

# Assistant Messages

Assistant messages:

* aligned left
* larger than user messages
* include inline citation badges

Citation badges should be real HTML elements.

Example:

```
The minimum CAV is 70%.

[1]
```

Do not render citations as plain text.

---

# Message Width

Assistant messages should never exceed approximately 70% of the chat width.

Long paragraphs should wrap naturally.

Avoid extremely wide text blocks.

---

# Input Area

The input stays anchored to the bottom of the chat container.

Structure:

```
+--------------------------------------+
| Ask anything...                 Send |
+--------------------------------------+
```

The input should stretch horizontally.

The send button remains fixed on the right.

---

# Citation Section

A small citation area appears below the input.

Each citation is a clickable HTML link.

Example:

```
[1] University of Waterloo Exchange Eligibility Requirements
```

Do not display raw URLs.

Open links in a new tab.

---

# Component Structure

Suggested React component hierarchy:

```
App

├── Background
├── LandingPage
│
├── HeroSection
│     ├── HeroText
│     └── HeroIllustration
│            ├── Globe
│            ├── Goose
│            └── Gosling
│
└── ChatPanel
      ├── ChatHeader
      ├── MessageList
      │      ├── UserMessage
      │      ├── AssistantMessage
      │      └── CitationBadge
      ├── ChatInput
      └── CitationList
```

Each component should have a single responsibility.

Avoid placing all layout logic inside one file.

---

# Asset Organization

```
src/

assets/

    background.png

    globe.svg

    goose.svg

    gosling.svg

components/

    Hero/

    Chat/

    Layout/

pages/

hooks/

styles/
```

---

# Responsive Behaviour

## Desktop (>1024px)

Maintain the 40/60 split.

The hero illustration remains visible.

The globe stays partially below the viewport.

---

## Tablet (768–1024px)

Adjust to approximately 45/55.

Reduce globe size slightly.

Reduce illustration height.

Maintain side-by-side layout.

---

## Mobile (<768px)

Switch to a vertical layout.

```
Hero

↓

Chat
```

The hero section occupies roughly 35–40% of the screen.

The chat occupies the remaining space.

Scale the globe down while keeping it partially cropped at the bottom.

Reduce whitespace appropriately.

---

# Animations

The interface should remain calm and understated.

Recommended animations:

* Button hover transitions
* Input focus transitions
* Message fade-in when received

Do **not** animate:

* globe
* goose
* gosling

Avoid excessive motion.

---

# Accessibility

* Use semantic HTML.
* Keyboard navigation should support every interactive element.
* Input should autofocus only when appropriate.
* All buttons require visible focus states.
* SVG illustrations should be marked as decorative (`aria-hidden="true"`).
* Citation links should have descriptive accessible labels.
* Maintain WCAG AA contrast as defined in `DESIGN.md`.

---

# Performance Recommendations

* Optimize SVGs using SVGO.
* Compress the watercolor PNG using WebP if browser support is acceptable.
* Lazy-load illustration assets only if future pages are introduced.
* Avoid unnecessary JavaScript for layout; prefer CSS Flexbox and Grid.
* Keep decorative assets separate from functional UI to simplify future updates.
