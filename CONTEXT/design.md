<!-- Purpose: Specify reference-led visual geometry, typography, 3D scenes, interactions, accessibility, and visual acceptance. -->
# Fusion: exact-reference UI specification

## 1. Design mandate

Reconstruct all six supplied CY · FOCUS screens faithfully. This supersedes the old guide's optional sidebar, four top tabs, orange logo pill, large rounded cards, gradient buttons, and exclusion of maps/3D. Recoloring existing components is insufficient.

Durable references:
- R1 [Dashboard](references/01-dashboard.png): metrics, map/hotspots/bars, activity, device and upper decorative strip.
- R2 [Compliance](references/02-compliance.png): angled device, coverage band/table, expanded upload/heatmap/code preview.
- R3 [Findings table](references/03-findings-table.png): dense table, chips, view toggle, title and actions.
- R4 [Findings board](references/04-findings-board.png): five columns, compact cards, status counts and thumbnails.
- R5 [Incident detail](references/05-incident-detail.png): metadata, tabs, polar/radar charts, entities.
- R6 [Filtered empty](references/06-filtered-empty.png): nested menus, orange triangulated globe, split CTA and lower exterior strip.

Exact source fonts, CSS, models, shaders, and motion are unavailable. Values below are reconstruction starting points inferred from raster images, not recovered originals. Calibrate by comparing browser captures. Do not claim the exact font has been identified. The existing [template video](template.mp4) is supplementary material; its motion was not analyzed for this specification.

## 2. Workbench, presentation, and showcase

**Workbench:** functioning Fusion screens with actual records. Preserve the full visual system, layout, navigation, and objects while using honest product labels.

**Presentation wrapper:** optional device/bezel/browser strip/exterior scene around those functioning screens. Required for the requested demo appearance. Normal editing remains flat; narrow screens omit the wrapper.

**Reference showcase:** isolated, persistently labeled “Reference showcase · sample data” mode reproduces literal CY · FOCUS branding, sample world map, owners, dates, CVSS values, ISO labels, and charts. Samples never enter live history, evidence exports, scans, or transactions. Default product identity is Fusion; literal reference identity belongs to this showcase.

The showcase must not become an excuse to leave live pages with the old UI. This distinction exists because screenshot metrics cannot be presented as measured security results.

## 3. Global shell and navigation

At roughly 1080–1200 CSS px usable desktop screen width, begin with 22–28 px shell inset, 188–208 px sidebar, and 18–24 px main gutter. Match proportional geometry instead of treating differently scaled device pixels as CSS values.

Sidebar: tall dark panel, warm top tint, angular/clipped top-right shoulder. Brand 18–20 px from left and 22–28 px from top. Split New scan/+ button below, followed by 18–24 px gap before navigation. Navigation rows 32–36 px tall in dense desktop mode, thin 14–16 px icons, 8–10 px icon/label gap. Active item has subtle pale fill and a **thin pale/white left rail**, as seen in the images; orange is the CTA accent. The previous guide's orange rail is superseded.

Exact destination order: Dashboard, Findings, Incidents, Compliance, Vault, Integrations. Help & Docs and a small local profile/initial tile sit at bottom above/below a subtle divider. No fabricated logged-in user in live mode.

Main content: small breadcrumb line, regular 22–24 px page title below, actions right-aligned. No large masthead, marketing hero, or global workflow tabs. Grid gaps 8–12 px; panel padding 14–18 px; dense table cells 10–14 px horizontal. Sidebar may be sticky; content scrolls naturally.

Routes: /dashboard, /findings, /findings/:id, /scans/:id, /patches/:id, /incidents, /incidents/:id, /compliance, /vault, /integrations, /help. IDs and filters survive reload. Patch review is reached through finding detail. Back/forward restores the user's view.

## 4. Colors and surfaces

These are provisional design tokens to tune against references and measured contrast.

| Token | Starting value | Purpose |
|---|---|---|
| --page-bg | #0b0f10 | Screen base |
| --surface-sidebar | #141616 | Sidebar |
| --surface-panel | #181c1d | Main panels |
| --surface-raised | #222627 | Cards/striped rows |
| --surface-hover | #2b2d2d | Hover/selected fill |
| --wash-top | #66301b | Burnt-orange top atmosphere |
| --wash-mid | #35231c | Brown transition |
| --accent-primary | #f13b08 | Solid orange CTA |
| --accent-hot | #ff5724 | Hotspots/mesh highlights |
| --text-primary | #f2efeb | Primary text |
| --text-secondary | #b8b3ae | Secondary text |
| --text-muted | #969591 | Supporting labels |
| --line-subtle | rgba(235,228,218,.11) | Dividers |
| --line-warm | rgba(232,72,22,.35) | Selected evidence border |
| --status-high | #ff613b | High severity with text |
| --status-medium | #efbc57 | Warning/medium |
| --status-low | #b5c65d | Low review signal |
| --status-pass | #25b87b | A passed check |
| --status-error | #f65c66 | Execution error |
| --focus | #ffe0b2 | Keyboard focus |

The warm wash covers the upper 25–40% and fades through brown to near-black; it must not make every card solid orange. Lower panels retain the cooler charcoal visible in references. Fine borders, restrained shadows, no glass everywhere. Avoid cyan, saturated purple, thick neon outlines, or glowing text.

Cards: 2–5 px radius. Buttons/menus: 3–4 px. Owner tiles: 2–3 px. Large curves belong to the device only. CTAs are solid orange, not gradients or green “accept” buttons. Darken the functional CTA background as needed for white-label contrast while preserving orange character; record this accessibility adjustment. Bright sample colors may remain in noninteractive showcase artwork.

Use semantic tokens. Migrate misleading --accent-blue/--accent-cyan names out of existing code once consumers are updated. Do not introduce theme changes merely because a generic design tool recommends them.

## 5. Typography and iconography

The references show restrained neutral/narrow sans text with regular headings, not a heavy geometric hero font. Exact family is unknown. Compare locally bundled Inter with the existing Plus Jakarta Sans using identical labels and capture scale; choose the closer reconstruction and record font file/version/license. System-ui is an explicitly provisional fallback if no suitable bundled asset exists. No runtime Google Fonts/CDN dependency.

JetBrains Mono or available monospace is reserved for code/hashes/addresses. Table labels and ordinary rows remain sans-serif; use tabular numerals for values. The earlier “all table rows monospace” description is superseded.

| Role | Desktop target | Weight / spacing |
|---|---|---|
| Wordmark | 17–19 px | 500, .04em |
| Page title | 22–24 px / 1.25 | 400 |
| Panel title | 13–15 px / 1.4 | 500 |
| Body/navigation | 12–14 px / 1.45 | 400–500 |
| Table headings | 9–10 px / 1.4 | 500, .10–.14em uppercase |
| Metadata | 10–12 px / 1.5 | 400 |
| Metric value | 24–28 px / 1.15 | 400 |
| Code | 12–13 px / 1.6 | 400 |
| Mobile body | at least 16 px / 1.5 | 400 |

Maintain readable zoom and contrast; desktop metadata can remain dense. Longer explanatory passages use comfortable line length and 1.5–1.7 line height.

Use existing Lucide SVGs, consistent 1.25–1.5 strokes. Match dashboard grid, findings focus, incidents document, compliance book/shield, vault folder, integrations plug, help/home, list/grid and download silhouettes. No emojis or unrelated icon families. Icon buttons require accessible names.

## 6. Shared components and interaction states

**Split CTA:** main rectangle plus separate square button with 3–4 px gap. Main opens default scan dialog; plus opens fixture/file/paste modes and disabled explanations. Showcase uses New task where visible. Busy submission prevents duplicate clicks immediately.

**Breadcrumb/title/actions:** linked ancestors, text current segment, no host paths. Compact list/grid toggle, Export and download icon remain at reference positions. View toggles preserve filters and operate on the same dataset.

**Tables:** hairline horizontal separators, quiet stripes, tiny severity square plus label, broad asset/description column, narrow metadata columns. Truncate with full-value/copy access. Sorting is visible and announced. Live Confidence replaces unsupported CVSS without changing the visual density.

**Badges/cards:** prefer small icon/dot plus text over large pills. Board cards have ID/severity line, asset subline, date/owner footer, upper-right menu. Thumbnails exist only for attached evidence or labeled samples.

**Menus:** first filter menu about 190–220 px wide; submenu 160–190 px, aligned to focused row. Dark surface, thin border, modest shadow. Keyboard arrows/Enter/Escape, outside dismissal, focus return, collision repositioning. No hover-only operation. Selected chips can be removed individually or cleared.

**Source/diff:** immutable source, line numbers, orange range tint/gutter, real hunk ranges, addition/removal signs as well as colors, original/candidate labels and hash reveal. Render text safely. A separate editing workflow creates a new revision; it never overwrites the source viewer.

**Validation:** title “Validation results,” per-check status/logs, candidate hash, parent-run identity. No certificate/audited wording. Missing, skipped, failed, unsupported, and timeout remain visible. Acceptance and validation have separate labels.

**Dialogs:** semantic title, focus trap/return, Escape where safe, readable errors, bounded scroll. Disabled controls explain availability in visible text or an accessible popover, not title-only tooltips.

**Feedback:** reserve skeleton dimensions. Loading, network error, compiler error, no history, completed-zero and no-match are distinct. Toasts supplement persistent errors. Job completion should not steal keyboard focus.

## 7. R1 — Dashboard

Four compact KPI cards across top. Lower grid roughly 55% map/bars and 45% activity. Sidebar occupies approximately one fifth of usable width. KPI label upper-left, small trend chip upper-right, large number below-left, mini chart right.

Live metrics: open review findings; recorded local incidents; required checks passed/required checks; measured validation duration. Show scope/window/denominator. Unknown duration/trend is unavailable. Do not invent sparklines or carry sample values into live mode.

Showcase map: subdued world silhouette with concentric orange hotspots, varying radius and opacity, translucent outer disc, stronger middle disc, bright core. Fine horizontal bars with value/label pairs and muted ticked baseline beneath. Live map slot uses an explicitly labeled contract/call topology unless genuine geographic data exists; never geolocate wallet addresses.

Activity: seven to nine visible compact rows depending on height, outline icon tile, event title/details/time, diagonal open arrow. Actual scan/validation/selection/export/replay events. Sort/window controls and Full report link work. If no events exist, preserve the panel geometry and show a useful empty state.

## 8. R2 — Compliance / Check coverage

Sidebar and header as reference. Live profile selector names a local check set; showcase retains ISO 27001. Wide summary band below title: warning/status icon, percentage and scope, right detail action.

Columns: check ID, status, description, evidence, reviewer, last run/next review. Broad description, narrow status/reviewer, fine row rules, expandable chevron.

Expanded content:
- left dashed evidence-upload well with centered Browse and allowed inert-file types;
- right heatmap with several rows of approximately 7–10 px colored cells and small regular gaps;
- floating Concern preview/code panel overlapping heatmap, translucent dark surface, thin border, subtle shadow, icon/title and syntax-colored inert text.

Live heatmap axes must be defined, e.g. checks versus runs; not-run uses its own state. Coverage denominator includes required failed/skipped/unrun checks. This page does not certify regulatory compliance. Bounded attachments may be text/JSON/images/PDF downloads; no execution of HTML/scripts/configurations.

## 9. R3 — Findings table

Breadcrumb, Findings title, chip/filter row beneath, view controls and Export right. Dense full-width table. Reference 03 is cropped: match the visible area without inventing an unseen footer.

Live columns: ID, severity, asset/source, confidence, review status, local reviewer, review date; detector in detail or secondary line. Showcase preserves CVSS/assignee samples. Row opens detail/source. Nested copy/menu actions do not accidentally trigger row navigation. Missing values say unavailable.

Findings detail must preserve this shell while adding immutable source, explanation, recommendation, raw evidence link, supported patch action, and actual source locations. A new scan clears stale selection.

## 10. R4 — Findings board

Five columns: Open, Triaged, In progress, Resolved, Canceled. Small heading icon, label/count; dark column wells; 8–10 px gutters. Compact cards with consistent inner padding and optional evidence thumbnail. Column height/composition matches reference, not a giant loose kanban.

At narrow widths use an internally scrollable labeled region. Provide keyboard status menu even with drag/drop. Persist states and edits, expose failed mutation/retry, retain history. Resolved needs a review reason/evidence link and never erases the original detector result or proves security. Empty columns keep their geometry without dummy cards.

## 11. R5 — Incident detail

Breadcrumb and record title, Download report right. Full-width metadata band: record title left, reviewer/created/review-date/updated fields, status/severity right, tabs along bottom.

Tabs: Overview, Detections, Notes, Logs, Respond. Every tab has actual content or an honest empty state. Respond links to review/guidance and supported patching, not a fake auto-pause feature.

Lower grid about 35%/65%: left information card over polar findings chart; right radar chart above entity table. Keep restrained borders and orange emphasis around main evidence area.

Polar plot: concentric rings, radial divisions, translucent orange/amber/red sectors. Radar: fine polygon grid, six labels, three outline/fill series only where data exists. Live dimensions/units/formula must be defined; do not invent quantitative residual-risk scores. Include legend and numerical table. Missing data retains layout with unavailable message.

Entities show actual contract/account roles, addresses, exact balances/deltas or receipt IDs. Full-value/copy action and historical session marker required. Observations, trace evidence, and root-cause hypotheses remain separate.

## 12. R6 — Filtered empty state and globe

Keep title/actions top, filter popover left, large central dark space, orange wireframe globe in remaining content, small Default/Advanced control near its bottom, one-line message, and split New scan/+ CTA.

Globe reconstruction:
- triangulated sphere, initial 24–36 longitudinal by 14–22 latitudinal bands, tuned to reference;
- thin orange network with sparse bright nodes, dark/transparent interior and front/back edge intensity;
- irregular dissolving/displaced triangles and particles across top 15–25%, lower hemisphere intact;
- no thick orbit rings, filled orange planet, blue glow, continents texture, or shield substitute;
- desktop diameter roughly 310–370 px at reference-like screen width, responsive clamp;
- fixed seeded capture pose; optional very slow rotation when motion allowed.

Use pinned lazy-loaded Three.js and deterministic geometry. Keep a local SVG/image fallback with comparable silhouette for unavailable/lost WebGL. Canvas is decorative/aria-hidden, pointer-events none, below real menus/buttons. Pause on hidden tab/offscreen route, dispose resources on unmount, freeze entirely for reduced motion.

No-match text only appears for a completed dataset with active filters. No-history, zero findings, errors and pending scans differ. Default/Advanced changes filter-field density while preserving valid selections; it cannot imply another analysis engine.

## 13. Device and exterior objects

Straight R1/R3/R4/R6 device: black bezel, thin metallic rim, inner black padding and smaller rounded screen mask, subtle top/left highlight. Start 18–26 px bezel relative to 1100 px screen, outer corner 48–60 px and inner 22–28 px; tune by overlay.

Decorative browser strip: left sidebar/back/forward glyphs, subdued centered address well, right utilities. Presentation only. Do not treat a drawn lock/address as actual connection security. Normal mode avoids duplicating browser chrome.

R2/R5 perspective presets apply to the wrapper, not individually skewed controls. Keep DOM usable, offer flat-view toggle, and match viewpoints separately.

Exterior stage fades warm gray-brown to dark charcoal with faint large grid arcs. Upper strip in R1 and lower strip in R6 repeat:
- white/off-white thin geodesic polygon-cell spheres with transparent centers;
- curved rectangular grid/saddle or flared cylindrical lattice objects;
- wordmark plus tiny supporting caption;
- measured spacing, partial edge cropping, subtle depth.

Reconstruct these with geometry/SVG and record provenance. They are required visual objects, not optional gradient decoration. Do not paste screenshots over the app to simulate functioning UI. Reference brand belongs to showcase; Fusion identity belongs to product presentation.

## 14. Motion, stacking, and responsive behavior

Micro transitions: 150–220 ms for color/opacity/transform, no transition:all or layout-bouncing hover. Globe rotation spans tens of seconds, never fast spinning. Real execution indicators have textual status; reduced motion uses static state.

Layers: base 0; decoration 1; content 10; sticky navigation 20; popovers 40; modal overlay 60; modal 70; feedback 80. Test actual stacking contexts and canvas overlap.

1440/1280: full dense layout. 1024: reduce gutters first. 768: collapsible sidebar, stacked charts. 375: drawer nav, single-column metrics, mobile-readable text, bounded table/board scrolling. No outer horizontal overflow; no hidden controls at 200% zoom. Device packaging hides on narrow viewports; app content remains.

## 15. Accessibility and performance gates

Normal text: 4.5:1 contrast; large text: 3:1 under the applicable definition. Measure composited backgrounds. [W3C contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).

Project touch target: 44 by 44 CSS px hit area through padding/expanded hit zones, retaining compact visible glyphs. This is a project choice, not a claim that WCAG AA universally requires 44 px. [W3C target-size guidance](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html).

Require skip link, semantic headings/tables, named icons, visible focus, color-plus-label states, accessible nested menus, drag alternatives, chart tables, and polite status announcements without rereading logs on every poll. Errors include recovery.

Provisional budgets to measure on recorded demo hardware:
- warm local primary route usable within 2 seconds with backend ready;
- 3D bundle separate and nonblocking for scanner controls;
- no hidden idle render loops;
- target smooth 30 fps minimum for visible decorative scene, lower-detail/static fallback if needed;
- cap decorative DPR at a measured 1.5–2;
- ten scene mounts/unmounts leave no accumulating canvases/listeners.
These are targets, not achieved measurements. Change them only with documented rationale/evidence.

## 16. Visual acceptance procedure

1. Freeze sample data, clock, mesh seed, viewport/DPR and bundled fonts; wait for readiness.
2. Capture all six reference compositions plus live loading/error/no-history/focus/mobile states.
3. Compare flat app crops first, then device/exterior perspective. R3 establishes only its visible crop.
4. Overlay matched-scale captures and inspect sidebar bounds, title baselines, columns, row density, orange wash, font letterforms, charts, mesh silhouette and filter overlap.
5. Record each deviation by reference/region, expected/actual, correction and any intentional accessibility/semantic exception.
6. Fix structure before tiny color changes. A matching palette alone is not completion.
7. Keep baseline/actual/diff captures and manual review. Whole-image equality is inappropriate across inferred perspective/fonts; accepted deterministic app captures become regression baselines.
8. Verify controls separately; screenshots do not prove functionality.

Do not repeatedly ask for unavailable original assets. Proceed with the closest documented reconstruction, and disclose unverified font/asset identity.

## 17. Applied skills

Used ui-ux-pro-max and ui-ux-designer. Design-system search returned generic dense-dashboard/Fira/blue suggestions; screenshot requirements take precedence, so those visual defaults are not adopted. Applied accessibility, async errors, derived-state, responsive and state-testing guidance. The designer skill's referenced implementation-playbook file is absent; its main guide and user references suffice. No invented user research or visual test results are claimed.
