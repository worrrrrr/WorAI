# Design System Specification for AI Generation

## 1. Design Tokens (JSON Format)
```json
{
  "colors": {
    "primary": "#3B82F6",
    "secondary": "#10B981",
    "accent": "#8B5CF6",
    "background": {
      "light": "#FFFFFF",
      "dark": "#0F172A",
      "glass": "rgba(255, 255, 255, 0.1)"
    },
    "text": {
      "primary": "#1E293B",
      "secondary": "#64748B",
      "inverse": "#F8FAFC"
    }
  },
  "typography": {
    "fontFamily": {
      "sans": ["Inter", "system-ui", "sans-serif"],
      "mono": ["JetBrains Mono", "monospace"]
    },
    "fontSize": {
      "xs": "0.75rem",
      "sm": "0.875rem",
      "base": "1rem",
      "lg": "1.125rem",
      "xl": "1.25rem",
      "2xl": "1.5rem",
      "3xl": "1.875rem",
      "4xl": "2.25rem"
    },
    "fontWeight": {
      "normal": 400,
      "medium": 500,
      "semibold": 600,
      "bold": 700
    }
  },
  "spacing": {
    "xs": "0.25rem",
    "sm": "0.5rem",
    "md": "1rem",
    "lg": "1.5rem",
    "xl": "2rem",
    "2xl": "3rem",
    "3xl": "4rem"
  },
  "borderRadius": {
    "sm": "0.25rem",
    "md": "0.5rem",
    "lg": "0.75rem",
    "xl": "1rem",
    "2xl": "1.5rem",
    "full": "9999px"
  },
  "shadows": {
    "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
    "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
    "glass": "0 8px 32px 0 rgba(31, 38, 135, 0.37)"
  }
}
```

## 2. Layout Patterns

### Bento Grid Layout
- **Description:** Modular grid system with varying cell sizes
- **Use Cases:** Dashboard, Personal Hub, Portfolio
- **AI Instructions:**
  - Use CSS Grid with `grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))`
  - Allow cells to span multiple rows/columns using `grid-column: span 2`
  - Maintain consistent gap of `1.5rem`

### Glassmorphism Cards
- **Background:** `backdrop-filter: blur(12px)`
- **Border:** `1px solid rgba(255, 255, 255, 0.2)`
- **Shadow:** Use glass shadow token
- **AI Instructions:** Apply to cards, modals, and navigation elements

## 3. Interaction Rules

### Micro-interactions
- **Hover:** Scale 1.02 + shadow increase (duration: 200ms)
- **Click:** Scale 0.98 (duration: 100ms)
- **Page Transition:** Fade + slide up (duration: 300ms)

### Loading States
- **Skeleton:** Shimmer animation with gradient
- **Spinner:** Circular with primary color
- **Progress Bar:** Smooth transition with easing

## 4. Responsive Breakpoints
```yaml
mobile: "max-width: 640px"
tablet: "max-width: 1024px"
desktop: "min-width: 1025px"
wide: "min-width: 1440px"
```

## 5. Dark Mode Strategy
- **Detection:** System preference + manual toggle
- **Implementation:** CSS custom properties with `[data-theme="dark"]`
- **AI Instructions:** Always define both light and dark variants for all colors

## 6. Accessibility Requirements
- **Contrast Ratio:** Minimum 4.5:1 for text
- **Focus States:** Visible outline with 2px offset
- **Keyboard Navigation:** Full support for Tab, Enter, Escape
- **Screen Readers:** ARIA labels for all interactive elements

## 7. AI Generation Prompts

### For Component Creation
```
Create a [COMPONENT_TYPE] with the following specifications:
- Style: [STYLE_NAME] from design tokens
- Layout: [LAYOUT_PATTERN]
- Interactions: [INTERACTION_LIST]
- Responsive: Mobile-first approach
- Accessibility: WCAG 2.1 AA compliant
```

### For Page Assembly
```
Assemble a page using these components:
- Header: [COMPONENT_REF]
- Main Content: [BENTO_GRID with cells: CELL_1, CELL_2, ...]
- Footer: [COMPONENT_REF]
Apply global styles from design.md tokens.
```

## 8. Version Control
- **Current Version:** 1.0.0
- **Last Updated:** 2025-01-15
- **Change Log:** Initial release with Astro 5.0 + Tailwind 4.0 compatibility
