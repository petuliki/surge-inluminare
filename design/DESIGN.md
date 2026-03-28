# Design System Document: The Sacred Archive

## 1. Overview & Creative North Star
### The Creative North Star: "The Digital Curator"
This design system rejects the ephemeral nature of modern tech in favor of "The Digital Curator"—an aesthetic rooted in permanence, authority, and the hushed sanctity of a private archive. It is designed for an AI Voice Agent that does not just "process tasks" but "renders counsel." 

We break the standard "app template" look by using intentional asymmetry—placing key information off-center to mimic the layout of a rare manuscript—and employing a high-contrast typography scale. Elements should feel like physical objects placed on a heavy cream vellum. This is not a flat interface; it is a digital desk in a wood-paneled study.

---

## 2. Colors
The palette is dominated by the tension between the ancient (cream/off-white) and the authoritative (deep cardinal red).

*   **Primary (`#820012`):** Our "Cardinal Red." To be used sparingly for high-impact moments, critical CTAs, and the voice activity indicator.
*   **Surface & Background (`#fbf9f4`):** A warm, textured off-white. This is the "paper" of our system.
*   **The "No-Line" Rule:** Explicitly prohibit the use of 1px solid borders to define sections. All separation must be achieved through background color shifts. For example, a content block should sit on `surface-container-low` (`#f5f3ee`) against the `surface` background.
*   **Surface Hierarchy:** Use the `surface-container` tiers to create depth. A secondary sidebar might use `surface-container-high` (`#eae8e3`), while a main interaction card uses `surface-container-lowest` (`#ffffff`) to appear as a fresh sheet of paper laid on top.
*   **The "Glass & Gradient" Rule:** For floating UI elements (like a voice modulation panel), use Glassmorphism. Apply `surface` with 80% opacity and a 20px backdrop blur. For primary buttons, use a subtle linear gradient from `primary` (`#820012`) to `primary_container` (`#a61d24`) to give the button a "wax seal" dimensionality.

---

## 3. Typography
Our typography is a dialogue between the liturgical past and functional present.

*   **Display & Headlines (Newsreader):** A sophisticated serif. Used for state titles and agent greetings. The `display-lg` (3.5rem) should be used with tight tracking to feel like a masthead.
*   **Body & UI (Work Sans):** A clean, modern sans-serif that ensures the "Agent's" transcriptions and technical data remain highly legible and objective.
*   **Hierarchy as Authority:** Use extreme scale differences. A large `display-md` headline should be paired directly with a `label-sm` metadata tag to create an editorial, high-end feel.

---

## 4. Elevation & Depth
We eschew the "Material" shadow in favor of **Tonal Layering**.

*   **The Layering Principle:** Stacking is our primary tool. A `surface-container-lowest` card sitting on a `surface-container-low` background creates a natural, soft "lift."
*   **Ambient Shadows:** If an element must float (e.g., a critical alert), use a highly diffused shadow: `0px 20px 40px rgba(27, 28, 25, 0.06)`. Note the color is a tint of our `on-surface` black, not pure gray.
*   **The "Ghost Border" Fallback:** If a container needs more definition, use a "Ghost Border": the `outline-variant` (`#e2bebc`) at 15% opacity. It should be felt, not seen.
*   **Roundedness:** Following the **0px scale**, all elements are sharp-edged. This conveys the rigid, uncompromising nature of an ancient institution.

---

## 5. Components

### Buttons
*   **Primary:** Sharp 0px corners. Background is a Cardinal Red gradient. Label is `title-sm` in `on-primary` (white), all-caps with 0.05rem letter spacing.
*   **Tertiary:** No background. Underlined with a 1px stroke of `primary` only on hover.

### Voice Input / Waveform
*   Instead of a standard "Siri" wave, use a rhythmic series of vertical bars in `primary`. The container should be a semi-transparent `surface` glass panel with `backdrop-blur`.

### Cards & Lists
*   **Cards:** Never use borders. Use `surface-container-highest` for the card body. 
*   **The "Anti-Divider" Rule:** Forbid 1px horizontal dividers. Separate list items using `spacing-4` (1.4rem) of vertical white space or by alternating background tones between `surface` and `surface-container-low`.

### Input Fields
*   **Text Inputs:** Bottom-border only (the "Ghost Border" at 20% opacity). When focused, the border transitions to `primary` with a 2px width. Labels use `label-md` in `secondary`.

### Signature Component: "The Seal"
*   A circular floating action button (FAB) that houses the logo. Unlike other components, this is the only element allowed a subtle 3D inner-shadow to look like a pressed wax seal.

---

## 6. Do's and Don'ts

### Do
*   **Do** use asymmetrical margins. For instance, give the main text block a larger left margin than right to mimic a book gutter.
*   **Do** use the `tertiary` wood-toned colors (`#4e3a21`) for secondary icons or subtle backgrounds to warm up the interface.
*   **Do** treat white space as a luxury. Use the `spacing-16` (5.5rem) and `spacing-20` (7rem) scales to let key typography "breathe."

### Don't
*   **Don't** use rounded corners (`0px` is the absolute rule). Softness is achieved through color and blur, not geometry.
*   **Don't** use "Electric" colors. Even the error state (`#ba1a1a`) should feel like a deep oxide red, never neon.
*   **Don't** use icons for everything. Favor elegant text labels (`label-md`) to maintain the scholarly aesthetic.