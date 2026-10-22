# IDEAL Thinkers site: standing instructions

The site (ailiteracycurriculum.ictevangelist.com) is a free primary AI literacy curriculum by Mark Anderson FCCT. It is static: `build.py` builds every page from the files in `data/`. Edit `build.py` or the data, run `python3 build.py`, and commit the built pages with the change.

## Keep the change log up to date

Whenever you change the site or its resources, add a dated entry to the What's new data file describing the change, and set the 'updated' date on any lesson whose plan or slides changed. Follow the writing rules in this file.

Only substantial changes go into What's new (Mark, 2026-10-22): new or changed resources, pages and content, and real fixes. Small visual tweaks, such as hover effects or spacing, are left out.

- The What's new data file is `data/whats-new.json`. Add new entries at the top: `date` (YYYY-MM-DD) and any of `new`, `updated` and `fixed`, each a list of `{"text": ..., "link": ...}`. `link` is a site path such as `glossary/` (`""` for the home page). If an entry for today already exists, add to it.
- A lesson's `updated` field is in `data/curriculum.json` (YYYY-MM-DD, empty when unchanged). When set, the lesson page shows an "Updated" note linking to What's new.
- The What's new page and the RSS feed (`whats-new/feed.xml`) are rebuilt from the data file by `python3 build.py`; nothing is sent by hand.

## Writing rules

- British English.
- Never use em dashes or en dashes. Use commas, semicolons, colons or full stops.
- Direct, authoritative, warm but not effusive.
- No AI-cliché phrasing: no "this isn't X, it's Y" constructions, no portentous openers, no "earns its place", "gently push back", "dive into", "unlock", "seamless", "exciting", "we're thrilled", "in today's world" or similar.
- Match the tone of the existing site.
- Do not change lesson content or existing URLs unless asked.

## Design rules

- Match the existing design system. Exo 2 for headings, Poppins for everything else.
- WCAG 2.2 AA contrast; keyboard accessible; works at 360px wide.
- Never cap line length on site copy: no max-width in ch on paragraphs, ledes or subtitles.
- Design and uniformity (Mark, 2026-10-22): when changing any element, keep it uniform with its siblings. If one box, card, button or text block must change size, position or style, change the matching ones the same way, and check the whole layout visually before calling it done. This applies to the lesson slides and documents too.
