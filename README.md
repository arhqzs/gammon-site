# Gammon — Marketing Site & Theme Gallery

The front-door marketing site for the Gammon backgammon platform, plus a gallery of
12 design themes for choosing a visual direction.

- **Homepage (`/`)** — the landing page, currently using Theme 01 (Heritage Club).
- **Gallery (`/gallery/`)** — live previews of all 12 themes to compare and decide.
- **Themes (`/themes/`)** — themes 02–12 as standalone pages (Theme 01 is the root `index.html`).

Static HTML/CSS/JS, no build step. Hosted on GitHub Pages.

To change the homepage to a different theme, copy the chosen `themes/theme-XX.html`
over `index.html` (and fix its relative asset paths if any).
