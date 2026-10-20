---
name: RegWatch Intelligence Design System
colors:
  surface: '#051424'
  surface-dim: '#051424'
  surface-bright: '#2c3a4c'
  surface-container-lowest: '#010f1f'
  surface-container-low: '#0d1c2d'
  surface-container: '#122131'
  surface-container-high: '#1c2b3c'
  surface-container-highest: '#273647'
  on-surface: '#d4e4fa'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#d4e4fa'
  inverse-on-surface: '#233143'
  outline: '#908fa0'
  outline-variant: '#464554'
  surface-tint: '#c0c1ff'
  primary: '#c0c1ff'
  on-primary: '#1000a9'
  primary-container: '#8083ff'
  on-primary-container: '#0d0096'
  inverse-primary: '#494bd6'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#ca8100'
  on-tertiary-container: '#3e2400'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#07006c'
  on-primary-fixed-variant: '#2f2ebe'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#051424'
  on-background: '#d4e4fa'
  surface-variant: '#273647'
typography:
  display-lg:
    fontFamily: Geist
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Geist
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Geist
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Geist
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-md:
    fontFamily: Geist
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Geist
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system targets institutional fintech compliance officers, general counsels, and risk managers who demand absolute clarity, precision, and focus. The aesthetic reflects a refined, modern SaaS interface built on dark-theme fundamentals: calm, deliberate, and high-signal, actively rejecting decorative noise, over-embellished neon halos, or faux-cyberpunk telemetry visuals.

Visual characteristics draw from focused **Minimalism** blended with **Modern Enterprise SaaS** norms:
- **Atmosphere:** Deep obsidian navy and charcoal backdrops that minimize optical fatigue during exhaustive audit trails and regulatory policy reviews.
- **Tone:** Authoritative, vigilant, and neutral. Visual tension is kept minimal; hierarchy is established through strict typographic scale, precise borders, and discrete tonal layering.
- **Information Density:** Balanced and legible. Data tables, compliance checklists, and regulatory diff-viewers utilize generous negative space and comfortable padding rather than cramped enterprise gridlines.

## Colors

The color architecture is built around an austere, highly controlled dark palette where color is applied strictly for state indication, active selection, and primary interaction.

### Surface Tiers
- **Base Canvas (`#0B1120`):** The foundational application background. Deep navy-charcoal with zero saturation bloat.
- **Card / Surface Default (`#151F32`):** Primary elevated surface for content containers, dashboards, and feeds.
- **Surface Elevated / Hover (`#1E293B`):** Interactive containers, table header rows, drop-down sheets, and flyout navigation.
- **Surface Active / Border Subdued (`#334155`):** Structural hairline dividers, inactive switch tracks, and subdued focus rings.

### Text & Content
- **Text Primary (`#F8FAFC`):** Crisp off-white ensuring WCAG AAA legibility against deep navy bases.
- **Text Secondary (`#94A3B8`):** Slate gray for metadata, regulatory citations, captions, and inactive labels.
- **Text Tertiary (`#64748B`):** Muted placeholders and helper text.

### Interactive & Status Tokens
- **Primary Action (`#6366F1`):** Restrained indigo used sparingly for focal actions, selected navigation items, and focus indicators.
- **Compliant / Low Risk (`#10B981`):** Emerald green indicating satisfied controls, passed rule evaluations, and clean attestations.
- **Warning / Moderate Risk (`#F59E0B`):** Amber for pending jurisdictional changes, upcoming filing deadlines, and non-blocking audits.
- **Critical / High Risk (`#EF4444`):** Pure rose/red reserved strictly for severe non-compliance, breached thresholds, and immediate legal exposure alerts.
- **Neutral / Insufficient Data (`#64748B`):** Slate gray for untested frameworks, neutral audit steps, or unknown data signals.

## Typography

The design system uses **Geist** throughout all primary text hierarchy, providing a sterile, modern geometric-grotesque personality engineered for data-dense software. For raw regulatory clauses, API audit payloads, and control hash references, **JetBrains Mono** is utilized.

### Formatting Principles
- **Readability Over Grandeur:** Heading weights are clamped at `600` (Semi-Bold) to prevent dark surfaces from feeling aggressive or heavy.
- **Tabular Figures:** Numbers within tables, risk counters, and dates must always render with tabular lining (`font-variant-numeric: tabular-nums`) to ensure vertical alignment.
- **Uppercase Labels:** The `label-sm` role is applied to badges, risk tier labels, and section caps with slight positive tracking (`+0.04em`) to ensure quick visual scanning.

## Layout & Spacing

The layout employs a responsive 12-column grid system paired with strict inner vertical rhythms based on an 8px base unit.

### Layout Mechanics
- **Desktop (1200px+):** Max application canvas constraint of `1440px` centered, or dynamic full-width layouts anchored by a fixed `260px` collateral navigation rail. Fluid 12-column content container with `1.5rem` (24px) gutters and `2rem` (32px) margins.
- **Tablet (768px – 1199px):** Collapsible sidebar rail into an icon dock. 8-column grid with `1.25rem` gutters.
- **Mobile (< 768px):** 4-column layout with `1rem` margins and gutters. Cards flatten their lateral padding to maximize viewable data surface.

### Padding and Density Philosophy
- Dashboard cards maintain `1.5rem` inner padding for spacious reading comfort.
- High-density policy review surfaces and tabular logs scale down internal cell padding to `0.75rem` vertical and `1rem` horizontal, preserving scanning speed without visual clutter.

## Elevation & Depth

This system intentionally excludes heavy diffuse drop shadows and fluorescent glow filters. Spatial hierarchy is maintained through **tonal surfacing** and **crisp micro-borders**:

- **Canvas (Level 0):** `#0B1120`. No border, baseline canvas.
- **Card / Surface Default (Level 1):** `#151F32` with a 1px border rendered in `#1E293B`.
- **Raised Interactive / Popover (Level 2):** `#1E293B` with a 1px border in `#334155` and a slight structural shadow: `0 8px 24px -4px rgba(0, 0, 0, 0.45)`.
- **Modals & Drawers (Level 3):** `#151F32` overlaid on a 60% opacity `#0B1120` backdrop blur (4px blur). Borders use `#334155`.

## Shapes

The design system maintains a balanced, contemporary geometry that softens institutional compliance tools while sustaining visual discipline:

- **Interactive Elements (Buttons, Inputs, Selectors):** `8px` (`0.5rem`) corner radius.
- **Structural Containers (Cards, Panels, Modals):** `12px` (`0.75rem`) to `16px` (`1rem`) corner radius.
- **Status Pills, Avatars, Badges:** Full pill radius (`9999px`) to immediately distinguish categorical state markers from actionable containers.
- **Dividers & Outlines:** 1px width across all interior layout tiers.

## Components

### Buttons
- **Primary:** Solid `#6366F1` background, `#FFFFFF` text, `8px` border radius, `0.5rem 1rem` padding. On hover, background shifts to `#4F46E5`. Active states drop brightness slightly.
- **Secondary / Ghost:** Transparent background with a `1px` border in `#1E293B` and `#F8FAFC` text. On hover, background becomes `#1E293B` with border `#334155`.
- **Destructive:** Bordered or subtle fill in `#EF4444` with a 10% opacity tint, transitioning to solid on critical confirmation.

### Badges & Status Chips
- Built with a full pill radius, compact padding (`0.125rem 0.625rem`), and `label-sm` font.
- Designed with subtle 10% background fills and solid text to ensure clarity without distracting from core data:
  - Compliant: `#10B981` (10% bg), `#10B981` text.
  - Warning: `#F59E0B` (10% bg), `#F59E0B` text.
  - Critical: `#EF4444` (10% bg), `#EF4444` text.
  - Neutral / Unverified: `#64748B` (15% bg), `#94A3B8` text.

### Form Fields & Inputs
- Background `#0B1120` inset against `#151F32` parent cards.
- Border: `1px solid #1E293B`.
- Text: `#F8FAFC` with placeholder text in `#64748B`.
- Focus state: Border transitions to `#6366F1` with an outer, unblurred focus ring (`2px` solid at 20% opacity). Never utilize heavy neon blur glows.

### Cards
- Standard surface `#151F32`, defined by a crisp `1px solid #1E293B` border.
- Headers are separated with an optional subtle `1px` border line in `#1E293B` when housing filters, tabs, or bulk actions.
- Interactive list rows inside cards highlight with `#1E293B` on hover.

### Checkboxes & Radios
- Size `16px x 16px`, corner radius `4px` (checkbox) or circular (radio).
- Default: `1px solid #334155`, background `#0B1120`.
- Checked: Background `#6366F1`, border `#6366F1` with a crisp off-white checkmark icon.

### Regulatory Diff & Policy Cards
- Purpose-built components for compliance tracking:
  - Left-hand border strip (3px wide) colored by status token (`#10B981`, `#F59E0B`, `#EF4444`).
  - Monospace references (`JetBrains Mono`) for regulatory section identifiers (e.g., `SEC-Rule-17a-4`, `FINRA-3110`).