# Superpowers Visual Companion Language

Superpowers Visual Companion is a reusable design language, not a copied page layout.

## Principles

- Establish a clear visual hierarchy from title and context to diagrams, annotations, and decisions.
- Use restrained rounded technical panels, soft grids, subtle shadows, and purposeful whitespace.
- Use explicit arrows, connectors, lanes, boundaries, and labels to show relationships.
- Do not use cards alone to represent relationships.
- Do not use a fixed page template.
- Adapt composition, density, and emphasis to the confirmed technical model.

## Semantic Color

Use a stable semantic color system across the page:

- processing or active flow: blue;
- success or completed state: green;
- waiting, gate, or human confirmation: amber;
- failure, blocked path, or destructive risk: red;
- neutral structure and context: slate or gray.

Semantic color must supplement labels, shapes, and line styles; never make color the only carrier of meaning.

## Relationship Rendering

Prefer inline SVG for relational diagrams so arrows, lanes, groups, and accessible text stay crisp offline. A diagram must explain direction and ownership without relying on decorative cards.

## Responsive Composition

Design the desktop composition first without assuming a wide fixed canvas. Below 720px, provide a mobile semantic alternative: convert horizontal relationships into a readable vertical order, preserve labels and direction, and avoid merely shrinking text or the entire SVG. Desktop and mobile views must communicate the same confirmed facts.
