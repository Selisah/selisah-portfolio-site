# Portfolio Pages, Education Application Section, and Sketch Map Design

## Overview

This design defines how to extend the Flask portfolio site with:
- A dynamic menu bar that links to dedicated portfolio pages
- An application-style education page with rich academic and role details
- A sketch-style map page with geographically accurate markers and dotted connectors
- JSON files as separate shared data sources per section

The implementation uses a hybrid approach:
- Flask + Jinja for routes, shared layout, and non-map pages
- A focused JavaScript renderer for map visualization

## Goals

- Create clear, dedicated pages for core portfolio sections.
- Keep navigation dynamic and reusable across all pages.
- Represent education in a structured "application section" format.
- Render a non-detailed sketch map with custom visual style:
  - White background
  - Light green map outline (`#66BB6A`)
  - Red location markers
  - Dotted connectors between geographically placed locations
- Store content in separate JSON files per section for easy maintenance.

## Scope

### In Scope

- Routing and templates for:
  - `/` (home)
  - `/about`
  - `/work`
  - `/education`
  - `/hobbies`
  - `/map`
- Shared base template and dynamic navbar generation
- JSON loader utility and section-specific JSON files
- Education page layout and data model
- Map page SVG rendering via JS with custom style and connection behavior

### Out of Scope

- Database persistence
- Authenticated editing UI
- Detailed political map demarcation
- Advanced GIS/projection libraries

## Architecture

### Backend (Flask)

- Flask route handlers load section data from JSON files using a shared loader utility.
- A shared nav configuration is provided to all templates to render menu items dynamically.
- Routes pass only view-ready data to templates; templates remain mostly declarative.

### Frontend (Jinja + CSS + JS)

- A shared `base.html` controls page structure and navbar.
- Section templates render content blocks/cards from JSON data.
- `map.html` provides an SVG container and embeds map payload for JS.
- `map-renderer.js` draws:
  - Simplified world outline
  - Red markers at projected coordinates
  - Dotted connector lines based on configured pairs
  - Marker labels/notes

## Proposed File Structure

- `app/__init__.py` (routes and request handling)
- `app/data_loader.py` (JSON reading and fallback logic)
- `app/templates/base.html` (shared layout + dynamic navbar)
- `app/templates/index.html`
- `app/templates/about.html`
- `app/templates/work.html`
- `app/templates/education.html`
- `app/templates/hobbies.html`
- `app/templates/map.html`
- `app/static/styles/main.css` (global styles + section/page styling)
- `app/static/js/map-renderer.js` (map rendering logic)
- `data/about.json`
- `data/work.json`
- `data/education.json`
- `data/hobbies.json`
- `data/map_locations.json`
- `data/site_nav.json` (optional but recommended)

## Navigation Design

- Navbar is rendered from shared page config data.
- Every page uses the same menu component from `base.html`.
- Menu items include label, route, and enabled state.
- Active route receives visual highlight styling.
- Disabled menu entries are not rendered.

## Data Design

### `data/education.json`

Top-level shape:
- `profile_summary`: short application-style intro text
- `current_education`: array
- `past_education`: array
- `campus_positions`: array
- `jobs`: array (optional but supported)

Education entry fields:
- `school_name`
- `location`
- `program_or_level`
- `classification`
- `gpa`
- `start_date`
- `grad_date`
- `status`
- `coursework` (array)
- `extracurriculars` (array)
- `highlights` (array)

Campus position entry fields:
- `title`
- `organization`
- `start_date`
- `end_date`
- `duration_text`
- `impact`

Job entry fields:
- `title`
- `organization`
- `location`
- `start_date`
- `end_date`
- `duration_text`
- `highlights` (array)

### `data/map_locations.json`

Top-level shape:
- `map_style`
- `locations`
- `connections`

`map_style` fields:
- `outline_color`: `#66BB6A`
- `background_color`: `#FFFFFF`
- `marker_color`: `#E02424`
- `connector_style`: `dotted`

`locations` entry fields:
- `id`
- `name`
- `country`
- `lat`
- `lng`
- `label`
- `note`

`connections` entry fields:
- `from_id`
- `to_id`

Design intent for connections:
- Connections are explicitly defined pairs, not inferred from list order.
- Marker placement remains geographically accurate.
- Pairing choices are arranged to create a haphazard, mostly Z-like connector pattern.

## Page Behavior

### Home (`/`)
- Shows profile photo and quick identity/introduction content.

### About (`/about`)
- Renders personal summary and profile details from JSON.

### Work (`/work`)
- Renders prior work experiences as cards/sections.

### Education (`/education`)
- Renders application-style sections for:
  - Current education
  - Past education
  - Campus positions
  - Jobs (if present)
- Long lists (coursework/extracurriculars/highlights) are displayed as readable tag groups or bullets.

### Hobbies (`/hobbies`)
- Renders hobbies with images and descriptions.

### Map (`/map`)
- White background map canvas
- Light green world outline (`#66BB6A`)
- Red location markers
- Dotted connector lines from `connections`
- Label and note display for each place

## Map Rendering Strategy

- Use inline SVG for visual control and responsiveness.
- Use a lightweight coordinate projection from latitude/longitude to SVG x/y.
- Draw operations in this order:
  1. Background
  2. Sketch outline
  3. Dotted connector lines
  4. Location markers
  5. Labels and notes
- Keep map intentionally minimal, avoiding detailed regional boundaries.

## Error Handling and Resilience

- JSON loader returns safe defaults when files are missing or malformed.
- Templates show non-breaking fallback content when arrays are empty.
- Map renderer skips invalid location entries and continues rendering valid points.
- Console warnings are used for map data issues to support debugging.

## Testing and Validation Plan

- Verify each route renders successfully.
- Verify navbar consistency and active-link behavior on all pages.
- Verify each section reads from its dedicated JSON file.
- Validate education sections for layout readability with long arrays.
- Validate map style requirements:
  - Background is white
  - Outline is `#66BB6A`
  - Markers are red
  - Connectors are dotted and based on configured pairs
- Validate geographic plausibility of marker placement.
- Check responsive behavior for navbar, cards, and map on smaller screens.

## Implementation Phases

1. Add JSON data files and loader utility.
2. Introduce base template and dynamic navbar plumbing.
3. Split and wire section routes and templates.
4. Implement application-style education page structure.
5. Build map renderer JS and map page SVG container.
6. Polish styles and run route/data/map/responsive validation.

## Decision Summary

- Chosen architecture: Flask + Jinja + map-only JS renderer (hybrid).
- Data storage: separate JSON file per section.
- Map style color decision: outline `#66BB6A` (light green), white background, red markers.
- Map connector behavior: geographically placed locations with explicit non-linear dotted pair connections for a haphazard mostly Z-like visual flow.
