# Personal Hub Template v1.0

## Tech Stack
- **Framework:** Astro 5.0
- **Styling:** Tailwind CSS 4.0
- **UI Pattern:** Bento Grid + Glassmorphism
- **Database:** SQLite (WASM)
- **Deployment:** Vercel Edge

## Features
- 🚀 Ultra-fast performance (Lighthouse 95+)
- 🎨 Modern glassmorphism design
- 📱 Fully responsive (mobile-first)
- 🌙 Dark mode support
- ♿ WCAG 2.1 AA accessible
- 📦 Offline-first with SQLite WASM

## File Structure
```
/
├── src/
│   ├── components/
│   │   ├── BentoGrid.astro
│   │   ├── GlassCard.astro
│   │   └── Navigation.astro
│   ├── layouts/
│   │   └── BaseLayout.astro
│   ├── pages/
│   │   └── index.astro
│   └── styles/
│       └── global.css
├── public/
│   └── favicon.svg
├── package.json
├── astro.config.mjs
├── tailwind.config.js
└── README.md
```

## Quick Start
```bash
npm install
npm run dev
```

## Performance Budget
- LCP: < 2.5s
- FID: < 100ms
- CLS: < 0.1
- Bundle Size: < 50KB

## Customization Points
1. Color tokens in `src/styles/global.css`
2. Grid layout in `src/components/BentoGrid.astro`
3. Content in `src/pages/index.astro`

---
**Version:** 1.0.0  
**Last Updated:** 2025-01-15  
**Compatibility:** Astro 5.0+, Node 18+
