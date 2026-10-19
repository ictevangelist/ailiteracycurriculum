#!/usr/bin/env python3
"""Builds the IDEAL Thinkers site from data/curriculum.json and data/ican.json.

Run: python3 build.py   (writes the pages into this folder)
All internal links are relative, so the site works on GitHub Pages and in previews.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT", ROOT)
PREVIEW = bool(os.environ.get("PREVIEW"))  # preview build: links point at index.html files
SITE = "https://ailiteracycurriculum.ictevangelist.com"
DATA = json.load(open(os.path.join(ROOT, "data/curriculum.json"), encoding="utf-8"))
ICAN = {r["code"]: r["i_can"] for r in json.load(open(os.path.join(ROOT, "data/ican.json"), encoding="utf-8"))}
SPOTS = json.load(open(os.path.join(ROOT, "data/roadmap-spots.json"), encoding="utf-8"))
EXTRA_SPOTS = json.load(open(os.path.join(ROOT, "data/roadmap-extra-spots.json"), encoding="utf-8"))
TRACKER = "18lutsh179zuY39y_L8VkzipVrCeSc1RHHuu3eA9D3ZE"
ROADMAP_PDF = "1xqUuxwFz0IVMQis2mX5iACgGPqD9xT6y"
GUIDE_URL = "https://docs.google.com/document/d/1ZSazUK-00P8Ne2G3T94l6GCVGfHIuzoJKU2catPhCTw/preview"
GA_ID = "G-1X05FYT3MT"  # Google Analytics measurement ID (G-...); empty = no analytics, no banner
LAUNCHED = True  # flip to True at launch: allows indexing and writes the sitemap
BUILT = "2026-10-14"  # sitemap lastmod
LICENCE_URL = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
AGES = {1: "5-6", 2: "6-7", 3: "7-8", 4: "8-9", 5: "9-10", 6: "10-11"}
AUTHOR = {"@type": "Person", "@id": SITE + "/#mark", "name": "Mark Anderson", "honorificSuffix": "FCCT",
          "url": "https://ictevangelist.com/",
          "sameAs": ["https://www.linkedin.com/in/themarkanderson/", "https://bsky.app/profile/ictevangelist.bsky.social", "https://twitter.com/ictevangelist"]}
COURSE_ID = SITE + "/#curriculum"

e = html.escape
IDEAL = [
    ("I", "Informed", "Know what it is", "Know what it is and how it works", "Know how it works and where it falls short"),
    ("D", "Deliberate", "Use it on purpose", "Use it for a reason, not as a shortcut", "Use it for a goal, deliberately and sparingly"),
    ("E", "Ethical", "Be fair and kind", "Be fair, honest and kind", "Use it fairly and question whether it is fair"),
    ("A", "Accurate", "Check it", "Check it before you trust it", "Fact check, look for bias, find the evidence"),
    ("L", "Learning", "Keep learning", "Make sure it helps you learn", "Keep your own thinking in charge"),
]
LINK_NAMES = {"DC": "Digital Citizenship", "DL": "Digital Literacy", "CS": "Computer Science"}


def slug(t):
    t = t.lower().replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


LESSONS = {}
for y in DATA["years"]:
    y["path"] = f"year-{y['n']}/"
    for l in y["lessons"]:
        l["year"] = y
        l["path"] = f"year-{y['n']}/{slug(l['title'])}/"
        l["i_can"] = ICAN.get(l["code"], [])
        LESSONS[l["code"]] = l


def rel(depth, path=""):
    return "../" * depth + path


def letters(ideal):
    return ["I", "D", "E", "A", "L"] if ideal.strip() == "All" else [x.strip() for x in ideal.split(",")]


def badges(ideal):
    if ideal.strip() == "All":
        return '<span class="badges"><span class="vh">IDEAL: all five habits</span>' + "".join(
            f'<span class="b b-{x}" aria-hidden="true">{x}</span>' for x in "IDEAL") + "</span>"
    ls = letters(ideal)
    names = {x[0]: x[1] for x in IDEAL}
    lab = ", ".join(names[x] for x in ls)
    return f'<span class="badges"><span class="vh">IDEAL: {lab}</span>' + "".join(
        f'<span class="b b-{x}" aria-hidden="true">{x}</span>' for x in ls) + "</span>"


def links_text(links):
    parts = []
    for p in [x.strip() for x in links.split(",")]:
        parts.append(f'<abbr title="{LINK_NAMES[p]}">{p}</abbr>' if p in LINK_NAMES else e(p))
    return ", ".join(parts)


TEACHER = json.load(open(os.path.join(ROOT, "data/teacher.json"), encoding="utf-8"))
DISCLOSURE = {"Y1L6", "Y3L1", "Y4L6", "Y5L3", "Y6L6"}  # can prompt disclosures (Guide, Safeguarding)


def lesson_ref(depth, code, slides="", title=True):
    l = LESSONS.get(code)
    if not l:
        return e(code)
    name = f'Year {l["year"]["n"]} Lesson {l["n"]}' + (f': {e(l["title"])}' if title else "")
    return f'<a href="{rel(depth, l["path"])}">{name}</a>' + (f' ({e(slides)})' if slides else "")


def codes_text(depth, s):
    """plain text with Y5L1 style codes -> 'Year 5 Lesson 1' links"""
    return re.sub(r"Y(\d)L(\d)", lambda m: lesson_ref(depth, m.group(0), title=False), e(s))


def code_link(depth, code):
    code = code.replace(" ", "")
    l = LESSONS.get(code)
    if not l:
        return e(code)
    return f'<a href="{rel(depth, l["path"])}">Y{l["year"]["n"]} L{l["n"]}</a>'


def codes_html(depth, s):
    return re.sub(r"Y\d L\d", lambda m: code_link(depth, m.group(0)), e(s))


NAV = [("", "Home"), ("how-it-works/", "How it works"), ("year-groups/", "Year groups"), ("curriculum-map/", "Curriculum map"),
       ("progression/", "Progression"), ("assessment/", "Assessment"), ("safety/", "Safety"), ("using-the-lessons/", "Using the lessons")]


def page(path, title, desc, body, depth, year=None, ld=None, crumbs=None):
    canon = SITE + "/" + path
    graph = list(ld or [])
    if crumbs:
        trail = [("Home", "")] + crumbs
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + "/" + p} for i, (n, p) in enumerate(trail)]})
    ldj = ""
    if graph:
        ldj = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("</", "<\\/") + "</script>\n"
    robots = "" if LAUNCHED else '<meta name="robots" content="noindex">\n'
    cur = ' aria-current="page"'
    nav = "".join(
        f'<a href="{rel(depth, p)}"{cur if p == path else ""}>{n}</a>' for p, n in NAV)
    ycls = f' class="y{year}"' if year else ""
    years_nav = "".join(
        f'<a class="yb y{y["n"]}{" yb-on" if path.startswith(y["path"]) else ""}" href="{rel(depth, y["path"])}"{cur if path == y["path"] else ""}>'
        f'<span class="yb-n">Year {y["n"]}</span><span class="yb-t">{e(y["title"])}</span></a>' for y in DATA["years"])
    consent_link = ' <button type="button" class="foot-btn" data-consent-open>Cookie settings</button>' if GA_ID else ""
    consent = f"""<aside class="consent" aria-label="Analytics cookies" hidden>
<p>Can I use Google Analytics cookies to see which pages get read, so I can improve the site? <a href="{rel(depth, 'privacy/')}">Privacy notice</a></p>
<p class="consent-btns"><button type="button" class="btn" data-consent="yes">Accept</button><button type="button" class="btn btn-ghost" data-consent="no">No thanks</button></p>
</aside>
<script src="{rel(depth, 'js/consent.js')}" data-ga="{GA_ID}" defer></script>
""" if GA_ID else ""
    doc = f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{robots}<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta property="og:site_name" content="IDEAL Thinkers">
<meta property="og:locale" content="en_GB">
<meta property="og:image" content="{SITE}/images/social-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="IDEAL Thinkers: a free AI literacy and fluency curriculum for primary schools, Year 1 to Year 6">
<meta name="twitter:card" content="summary_large_image">
<meta name="author" content="Mark Anderson">
{ldj}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Exo+2:wght@600;700;800&family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel(depth, 'css/site.css')}">
<link rel="icon" href="{rel(depth, 'favicon.svg')}" type="image/svg+xml">
</head>
<body{ycls}>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
<div class="wrap top-in">
<a class="brand" href="{rel(depth)}"><span class="brand-name"><span class="bn-1">IDEAL</span> <span class="bn-2">Thinkers</span></span><span class="brand-tag">An AI literacy and fluency curriculum</span></a>
<nav class="nav" aria-label="Main">{nav}</nav>
</div>
<nav class="years-bar" aria-label="Year groups"><div class="wrap years-in">{years_nav}</div></nav>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
<div class="wrap foot-in">
<p><strong>IDEAL Thinkers</strong> is the AI Literacy strand of the Primary Digital Cognition Curriculum, by <a href="https://ictevangelist.com/">Mark Anderson FCCT</a>.</p>
<p>IDEAL Thinkers &copy; 2026 Mark Anderson. Free to use for non commercial purposes under <a href="{rel(depth, 'licence/')}">CC BY-NC-SA 4.0</a>. It cannot be taken, distributed or shared for commercial purposes.</p>
<p class="foot-links"><a href="{rel(depth, 'progression/')}">Progression and coverage</a> <a href="{rel(depth, 'assessment/')}">Assessment</a> <a href="{rel(depth, 'licence/')}">Licence</a> <a href="{rel(depth, 'privacy/')}">Privacy</a>{consent_link} <a href="https://ictevangelist.com/">ictevangelist.com</a></p>
</div>
</footer>
{consent}</body>
</html>
"""
    if PREVIEW:
        doc = re.sub(r'href="((?:\.\./)*[^":#]*/)"', r'href="\1index.html"', doc).replace('href=""', 'href="index.html"')
    # Google Drive folders, copies and previews open in a new tab; downloads stay put
    doc = re.sub(r'(<a [^>]*href="https://(?:drive|docs)\.google\.com/(?:drive/folders/[^"]*|[^"]*/(?:copy|preview))")',
                 r'\1 target="_blank" rel="noopener"', doc)
    out = os.path.join(OUT, path, "index.html") if path else os.path.join(OUT, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(doc)
    PAGES.append(path)


PAGES = []

LICENCE_PANEL = """<aside class="licence-panel" aria-label="Licence">
<p class="lp-title"><span class="ic ic-gold" aria-hidden="true"><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M10.5 9.8a2.8 2.8 0 1 0 0 4.4"/><path d="M16.5 9.8a2.8 2.8 0 1 0 0 4.4"/></svg></span>Free to use. Protected by copyright.</p>
<p>IDEAL Thinkers is free for schools and teachers, but it is protected by copyright and a Creative Commons licence (CC BY-NC-SA 4.0). That means it cannot be taken, distributed or shared for commercial purposes. You're welcome to copy and adapt it for your own teaching, as long as you credit "IDEAL Thinkers by Mark Anderson, ictevangelist.com" and share any adapted versions under the same licence.</p>
<p><a class="btn btn-ghost" href="{href}">Read the licence</a></p>
</aside>"""


ICONS = {
    "book": '<path d="M2 5h7a3 3 0 0 1 3 3v12a2 2 0 0 0-2-2H2z"/><path d="M22 5h-7a3 3 0 0 0-3 3v12a2 2 0 0 1 2-2h8z"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "bulb": '<path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7V16h8v-1.3A7 7 0 0 0 12 2z"/>',
    "usercheck": '<circle cx="9" cy="8" r="4"/><path d="M2 21a7 7 0 0 1 14 0"/><path d="M16 11l2 2 4-4"/>',
    "loop": '<path d="M20 11a8 8 0 0 0-14.9-3"/><path d="M4 4v4h4"/><path d="M4 13a8 8 0 0 0 14.9 3"/><path d="M20 20v-4h-4"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    "seedling": '<path d="M12 21v-9"/><path d="M12 12c0-4 3-7 8-7 0 4-3 7-8 7z"/><path d="M12 14c0-3-2.5-5.5-7-5.5 0 3 2.5 5.5 7 5.5z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "grid": '<rect x="3" y="3" width="8" height="8" rx="2"/><rect x="13" y="3" width="8" height="8" rx="2"/><rect x="3" y="13" width="8" height="8" rx="2"/><rect x="13" y="13" width="8" height="8" rx="2"/>',
    "landmark": '<path d="M3 21h18"/><path d="M5 21V10"/><path d="M19 21V10"/><path d="M9 21V10"/><path d="M15 21V10"/><path d="M2 10l10-6 10 6z"/>',
    "layers": '<path d="M12 2l9 4.5-9 4.5-9-4.5z"/><path d="M3 11.5l9 4.5 9-4.5"/><path d="M3 16.5l9 4.5 9-4.5"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18"/><path d="M8 3v4"/><path d="M16 3v4"/>',
    "people": '<circle cx="8" cy="8" r="3"/><circle cx="16" cy="8" r="3"/><path d="M2 20a6 6 0 0 1 12 0"/><path d="M10 20a6 6 0 0 1 12 0"/>',
    "brain": '<path d="M9 3a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 3 3 2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z"/><path d="M15 3a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-3 3 2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/>',
    "stairs": '<path d="M3 20h5v-5h5v-5h5V5h3"/>',
    "slides": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M12 16v4"/><path d="M8 20h8"/>',
    "plan": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/><path d="M8 13h8"/><path d="M8 17h5"/>',
    "unplug": '<path d="M9 2v5"/><path d="M15 2v5"/><path d="M6 7h12v4a6 6 0 0 1-12 0z"/><path d="M12 17v5"/><path d="M3 3l18 18"/>',
    "nouser": '<circle cx="9" cy="8" r="4"/><path d="M2 21a7 7 0 0 1 14 0"/><path d="M17 8l4 4"/><path d="M21 8l-4 4"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="18" rx="2"/><path d="M9 4V2h6v2"/><path d="M9 11h6"/><path d="M9 15h4"/>',
    "heartshield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M12 16s-3.5-2-3.5-4.3a1.8 1.8 0 0 1 3.5-.9 1.8 1.8 0 0 1 3.5.9C15.5 14 12 16 12 16z"/>',
    "chart": '<path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-7"/><path d="M22 20H2"/>',
    "licence": '<circle cx="12" cy="12" r="9"/><path d="M10.5 9.8a2.8 2.8 0 1 0 0 4.4"/><path d="M16.5 9.8a2.8 2.8 0 1 0 0 4.4"/>',
}


def icon(name, colour="i", size=26, cls="ic"):
    return (f'<span class="{cls} ic-{colour}" aria-hidden="true"><svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg></span>')


def chatty(cls="chatty", label=""):
    """Chatty, the class chatbot from the Year 4 decks, redrawn from the slide's own shapes."""
    a11y = f'role="img" aria-label="{e(label)}"' if label else 'aria-hidden="true"'
    return (f'<svg class="{cls}" viewBox="0 0 209 329" {a11y}>'
            '<line x1="104.4" y1="20" x2="104.4" y2="58" stroke="#2C3E50" stroke-width="5"/>'
            '<circle cx="104.4" cy="12.6" r="12.6" fill="#E8562A"/>'
            '<rect x="0" y="57.4" width="208.8" height="167" rx="24" fill="#8E44AD"/>'
            '<rect x="26.1" y="83.5" width="156.6" height="114.8" rx="16" fill="#FFFFFF"/>'
            '<circle class="ch-eye" cx="72" cy="124.2" r="14.6" fill="#2C3E50"/>'
            '<circle class="ch-eye" cx="136.7" cy="124.2" r="14.6" fill="#2C3E50"/>'
            '<path d="M78 166 Q104.4 186 130.8 166" fill="none" stroke="#2C3E50" stroke-width="4.5" stroke-linecap="round"/>'
            '<rect x="31.3" y="234.9" width="146.2" height="94" rx="16" fill="#8E44AD"/></svg>')


POSTERS = {"ai-loop": ("The AI Loop", "ideal-thinkers-ai-loop-poster-a4.pdf"),
           "ideal-habits": ("The habits grow with the children", "ideal-thinkers-ideal-habits-poster-a4.pdf")}


def poster_block(depth, key):
    t, f = POSTERS[key]
    return f"""<aside class="poster card">
<img src="{rel(depth, 'images/posters/' + key + '.png')}" width="397" height="562" loading="lazy" alt="A4 poster: {e(t)}">
<div><h2>Poster: {e(t)}</h2><p>An A4 poster for your classroom wall or display board.</p>
<p><a class="btn" href="{rel(depth, 'downloads/' + f)}" download>Download the A4 poster (PDF)</a></p></div>
</aside>"""


def loop_strip():
    steps = [("Learn", "It learns from lots of examples (data) that people choose or create."),
             ("Spot", "It finds patterns in those examples."),
             ("Guess", "It uses the patterns to make a prediction: a label, a next word, a video, a picture."),
             ("Check", "It can be wrong without knowing. People check its guesses before they trust them.")]
    ic = ["book", "eye", "bulb", "usercheck"]
    return '<ol class="loop">' + "".join(
        f'<li class="loop-{i}"><span class="loop-top"><span class="loop-num">{i}</span>{icon(ic[i-1], "w", 30, "loop-ic")}</span>'
        f'<span class="loop-n">{s}</span><span class="loop-t">{e(t)}</span></li>'
        for i, (s, t) in enumerate(steps, 1)) + "</ol>"


def lesson_card(depth, l, show_year=False):
    yr = f'<span class="card-year">Year {l["year"]["n"]}</span>' if show_year else ""
    ch = '<span class="tag tag-challenge">IDEAL Challenge</span>' if l["challenge"] else ""
    data_l = " ".join(letters(l["ideal"]))
    return f"""<article class="card lesson-card y{l['year']['n']}" data-year="{l['year']['n']}" data-letters="{data_l}">
<p class="card-kicker">{yr}<span>Lesson {l['n']}</span>{ch}</p>
<h3><a href="{rel(depth, l['path'])}">{e(l['title'])}</a></h3>
<p class="card-idea">{e(l['big_idea'])}</p>
<p class="card-meta">{badges(l['ideal'])}<span class="links">{links_text(l['links'])}</span></p>
</article>"""


YEAR_ICONS = {
    # Y1 Machines That Guess: a robot with a question mark
    1: '<rect x="4" y="8" width="16" height="12" rx="3"/><path d="M12 8V4"/><circle cx="12" cy="3" r="1"/><path d="M9.5 12.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .8-1 1.4"/><path d="M12 18.5h.01"/>',
    # Y2 Using AI Wisely: a shield with a tick
    2: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    # Y3 AI in Everyday Life: a house with a signal
    3: '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M9.5 16a3.5 3.5 0 0 1 5 0"/><path d="M12 18.5h.01"/>',
    # Y4 Machines That Talk: speech bubbles
    4: '<path d="M4 5h11a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H9l-4 3v-3H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z"/><path d="M19 9h1a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-1v3l-3-3h-4"/>',
    # Y5 Data, Training and Fairness: balance scales
    5: '<path d="M12 3v18"/><path d="M7 21h10"/><path d="M5 7h14"/><path d="M5 7l-3 7a3.5 3.5 0 0 0 6 0z"/><path d="M19 7l-3 7a3.5 3.5 0 0 0 6 0z"/>',
    # Y6 AI, Society and the Future: a globe
    6: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18"/><path d="M12 3a14 14 0 0 0 0 18"/>',
}


def year_icon(n, size=34):
    return (f'<span class="yi yi{n}" aria-hidden="true"><svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{YEAR_ICONS[n]}</svg></span>')


def year_card(depth, y):
    return f"""<a class="card year-card y{y['n']}" href="{rel(depth, y['path'])}">
{year_icon(y['n'])}
<span class="yc-n">Year {y['n']}</span>
<span class="yc-t">{e(y['title'])}</span>
<span class="yc-q">{e(y['big_question'])}</span>
</a>"""


# ---------- Home ----------
FAQ = [('What is IDEAL Thinkers?', "A free AI literacy curriculum for primary schools, from Year 1 to Year 6. There are 36 lessons, six for each year group, and every lesson has a lesson plan and a slide deck. It's the AI Literacy strand of the Primary Digital Cognition Curriculum from The EdTech Playbook."),
       ('What do you mean by AI literacy and AI fluency?', "AI literacy is knowing how the AI children meet works, at a level that fits their age; what it can and cannot do; and how it affects people, fairly or unfairly. Pupils show it by explaining these ideas in their own words and applying them to a new example. AI fluency is making good decisions about AI: whether to use it at all, what to ask, how to check what comes back, and how to keep the learning their own. In primary school, pupils practise these decisions through unplugged activities and teacher-led demonstrations, not by using AI tools themselves."),
       ('Is it free?', "Yes, for schools and teachers. I've always shared my resources freely, from my days as the local authority lead teacher for computing to the early years of my blog. I became a teacher because education is a force for good: to help young people, to make a difference and to make my dent in the universe. If what I share helps just one person, that's good enough for me. With IDEAL Thinkers, I hope it helps far more than that. It's licensed under CC BY-NC-SA 4.0, so you can copy and adapt it for your own teaching as long as you credit it and share any adapted versions under the same licence. It cannot be used for commercial purposes."),
       ('Do pupils need devices or their own AI accounts?', "No. Every lesson can be taught without pupil devices, and pupils never need an AI account. Age limits differ between tools and change often: some are for 13 and over with a parent's permission, some are for adults only. Where a demonstration helps, the teacher runs it on a school approved tool, and every demonstration lesson can also be taught without one, using prepared results or an unplugged version."),
       ('How long is each lesson?', "60 minutes, and every lesson plan includes a 45 minute version. The Year 6 IDEAL Challenge runs over two 60 minute sessions. Each year's six lessons are planned as a half-term unit, and the sixth lesson is an IDEAL Challenge that doubles as the end of unit assessment."),
       ('Does it cover the National Curriculum for computing?', "It teaches the KS1 and KS2 statements on using technology safely, respectfully and responsibly, keeping personal information private, knowing where to go for help and reporting concerns, recognising common uses of information technology beyond school, and being discerning in evaluating digital content, plus selection in programs in Year 5. How feeds choose what we see connects to the KS2 statement on search results, but it does not replace teaching search. The current curriculum does not require AI to be taught; IDEAL Thinkers will be mapped against the revised computing curriculum when the draft is published."),
       ('Can I use it with Microsoft 365?', 'Yes. Every slide deck downloads as PowerPoint and every lesson plan as Word, and on Google Workspace you can make your own copy in Google Drive.')]


def build_home():
    d = 0
    years = "".join(year_card(d, y) for y in DATA["years"])
    body = f"""<section class="hero">
<div class="wrap hero-grid">
<div class="hero-text">
<p class="eyebrow">An AI literacy and fluency curriculum for primary schools, Year 1 to Year 6</p>
<h1>IDEAL Thinkers</h1>
<p class="lede">Children are growing up alongside AI. It chooses the next video they watch, finishes their sentences, listens from the kitchen worktop and answers questions in a voice that sounds friendly and sure of itself. Most of them meet it long before anyone teaches them what it is.</p>
<p class="lede">IDEAL Thinkers is designed to give primary pupils the knowledge to understand how AI works, the habits to question what it tells them, the values to use it well, and the judgement to know when it helps their learning and when it gets in the way.</p>
<div class="hero-ctas">
<a class="btn" href="curriculum-map/">Find a lesson</a>
<a class="btn btn-ghost" href="how-it-works/">How it works</a>
<a class="btn btn-ghost" href="safety/">Is it safe?</a>
</div>
</div>
<div class="hero-art">{chatty("chatty chatty-hero", "Chatty, the class chatbot from the Year 4 lessons")}</div>
</div>
</section>
<section class="wrap glance-sec">
<h2>At a glance</h2>
<dl class="glance">
<dt>What</dt><dd>A free AI literacy curriculum for primary schools: pupils learn how AI works, when to trust it, and when not to use it.</dd>
<dt>Who</dt><dd>Years 1 to 6, ages 5 to 11.</dd>
<dt>What it covers</dt><dd>Five progression strands: how AI works; staying in charge; safe, fair and honest; learning well; design and create. Mapped to the National Curriculum, SEAME and the Primary Digital Cognition Curriculum. <a href="progression/#coverage">See the coverage</a></dd>
<dt>What you get</dt><dd>36 lessons, six a year, each with a lesson plan and slides.</dd>
<dt>Time</dt><dd>60 minutes a lesson, with a 45 minute version in every plan. The Year 6 IDEAL Challenge runs over two sessions.</dd>
<dt>What you need</dt><dd>A screen for the slides. No pupil devices or AI accounts.</dd>
<dt>Who made it</dt><dd>Mark Anderson FCCT: more than 20 years as a teacher and senior leader, former local authority lead teacher for computing, and for the last ten years an independent consultant supporting hundreds of schools across the UK and around the world with AI, digital strategy and teaching and learning with technology. Lead AI consultant on the BBC's Bitesize Guide to AI, Founding Fellow of the Chartered College of Teaching, member of the BCS Schools and Colleges Committee, and award-winning author of The EdTech Playbook.</dd>
<dt>Why it is free</dt><dd>"I've always shared my resources freely. If it helps just one person, that's good enough for me; with IDEAL Thinkers, I hope it helps far more."</dd>
<dt>Feedback so far</dt><dd>Shaped by feedback from ten practising digital and computing leaders in schools across the UK, and already being taught in classrooms.</dd>
<dt>How it builds</dt><dd><a href="progression/">See the progression from Year 1 to Year 6</a></dd>
<dt>Is it safe?</dt><dd><a href="safety/">How safeguarding works</a></dd>
</dl>
</section>
<section class="wrap home-map">
<h2>The road map</h2>
<p>All 36 lessons on one page, from Year 1 to secondary school.</p>
<a class="home-map-img" href="curriculum-map/"><img src="images/ideal-thinkers-road-map.webp" width="2482" height="1754" loading="lazy" alt="The IDEAL Thinkers curriculum road map, showing all 36 lessons from Year 1 to Year 6"></a>
<p><a class="btn" href="curriculum-map/">Explore the curriculum map</a></p>
<p class="more"><a href="progression/">See how the learning builds from Year 1 to Year 6</a></p>
</section>
<section class="wrap">
<h2>How the parts fit together</h2>
<p>It is built on the principle behind all of my work: pedagogy first, technology second. Nearly every activity works without a single pupil device. Where technology appears, the teacher leads it, with a clear purpose and safeguarding built in.</p>
<p>Every plan lists exactly what to prepare, the card sets can be kept and reused each year, and every deck and plan can be copied, adapted and made your own.</p>
<ol class="ladder">
<li><h3>What pupils learn</h3><p>Five progression strands, built from Year 1 to Year 6: how AI works; staying in charge; safe, fair and honest; learning well; design and create. <a href="progression/">Progression</a></p></li>
<li><h3>The habits they build</h3><p>IDEAL: Informed, Deliberate, Ethical, Accurate, Learning. Learning Well is how the L is taught: Try it first, Hint not answer, then Plan, use, prove. <a href="how-it-works/ideal/">IDEAL</a> <a href="how-it-works/learning-well/">Learning Well</a></p></li>
<li><h3>The tools for teaching it</h3><p>The AI Loop, a simple model of how AI that learns from examples works, and STAIR, a prompting scaffold for Years 5 and 6. <a href="how-it-works/ai-loop/">The AI Loop</a></p></li>
<li><h3>How a lesson runs</h3><p>Seven phases in every lesson, for teachers to plan with. <a href="how-it-works/every-lesson/">Every lesson</a></p></li>
<li><h3>What it lines up with</h3><p>The Primary Digital Cognition Curriculum, the National Curriculum, SEAME, UDL and cognitive science, below.</p></li>
</ol>
<h3>The AI Loop: Learn, Spot, Guess, Check</h3>
{loop_strip()}
</section>
<section class="band">
<div class="wrap">
<h2>Six units, one for each year</h2>
<p>Six lessons per year, planned as a half-term unit. The sixth lesson in each year is an IDEAL Challenge, where pupils pull the unit together to make or decide something.</p>
<div class="grid grid-3">{years}</div>
</div>
</section>
<section class="band">
<div class="wrap">
<h2>What it aligns with and draws on</h2>
<div class="grid grid-2 frameworks">
<article class="card fw">
{icon("grid", "i")}<h3>The Primary Digital Cognition Curriculum</h3>
<p>The Primary Digital Cognition Curriculum, published in The EdTech Playbook, has four strands: Digital Citizenship, Digital Literacy, Computer Science and AI Literacy. IDEAL Thinkers is the full, teachable AI Literacy strand. AI does not stay in its own box, though, so every lesson also shows its links to the other three strands. Schools can see AI literacy as part of a whole approach to digital cognition rather than a bolt-on.</p>
</article>
<article class="card fw">
{icon("landmark", "d")}<h3>The National Curriculum for computing (England)</h3>
<p>Taught directly: using technology safely, respectfully and responsibly; keeping personal information private and knowing where to go for help; recognising common uses of information technology beyond school (KS1); reporting concerns, being discerning in evaluating digital content, and using selection in programs (KS2). How feeds choose what we see connects to the KS2 statement on search results, but it does not replace teaching search. The current curriculum does not require AI to be taught.</p>
</article>
<article class="card fw">
{icon("layers", "e")}<h3>SEAME</h3>
<p>SEAME, from the Raspberry Pi Computing Education Research Centre, sorts what we teach about AI into four levels: social and ethical, applications, models and engines (how AI works). It is used here as a lens to check coverage. The lessons cover all four, with engines taught through unplugged activities.</p>
</article>
<article class="card fw">
{icon("calendar", "a")}<h3>The new computing curriculum</h3>
<p>BCS is drafting a revised computing curriculum for first teaching from September 2028, and the Curriculum and Assessment Review recommended that it include AI. It is not yet statutory. IDEAL Thinkers will be mapped against the draft when it is published.</p>
</article>
<article class="card fw">
{icon("people", "l")}<h3>Universal Design for Learning</h3>
<p>Every plan offers more than one way to take part, to access the content and to show understanding, and names the main barrier in that lesson with a planned response.</p>
</article>
<article class="card fw">
{icon("brain", "i")}<h3>Cognitive science</h3>
<p>Spaced retrieval, concrete before abstract, worked examples and modelling, explicit vocabulary teaching, words always paired with the same pictures, and frequent low stakes checks for understanding.</p>
</article>
</div>
<p>Wider curriculum: RSHE, science, maths, English, geography and careers links are flagged in each lesson plan.</p>
</div>
</section>
<section class="wrap">
<h2>From a headteacher</h2>
<figure class="card quote">
<blockquote>
<p>For me as a headteacher it looks:</p>
<ul class="ticks">
<li>pedagogically well thought through</li>
<li>progressive</li>
<li>comprehensive</li>
<li>clear, for all staff to be able to pick up and use</li>
<li>really relevant for the children and the world they are living and growing up in</li>
</ul>
</blockquote>
<figcaption><strong>Tim Clarke</strong>, Headteacher, Cornerstone CE Primary School, Hampshire</figcaption>
</figure>
</section>
<section class="wrap">
<h2>Evidence and limits</h2>
<p>The design draws on <a href="https://www.aft.org/sites/default/files/Rosenshine.pdf">Rosenshine's Principles of Instruction</a> (2012), the EEF's review <a href="https://educationendowmentfoundation.org.uk/education-evidence/evidence-reviews/cognitive-science-approaches-in-the-classroom">Cognitive science approaches in the classroom</a> (2021), which finds retrieval and spacing promising but with less evidence for young pupils, <a href="https://udlguidelines.cast.org/">CAST's UDL Guidelines</a>, and a 2025 study in which pupils given answers by AI learned less than pupils given hints (<a href="https://doi.org/10.1073/pnas.2422633122">Bastani and others, PNAS</a>).</p>
<ul class="list">
<li>It has not yet been formally evaluated in classrooms.</li>
<li>Pupils practise decisions about AI through unplugged activities and teacher demonstrations. They do not use AI tools themselves, so it builds judgement about AI more than skill with particular tools.</li>
<li>It does not replace your school's computing scheme, online safety teaching or safeguarding procedures.</li>
<li>Age limits and tool features change often. Check the terms of any tool, and your school's policy, before using it.</li>
</ul>
</section>
<section class="wrap home-faq">
<h2>Common questions</h2>
{"".join(f'<div class="faq"><h3>{e(q)}</h3><p>{e(a)}</p></div>' for q, a in FAQ)}
</section>
<section class="wrap home-licence">
{LICENCE_PANEL.format(href='licence/')}
</section>"""
    page("", "IDEAL Thinkers: Free AI Literacy Curriculum for Primary Schools",
         "IDEAL Thinkers is a free AI literacy curriculum for Year 1 to Year 6 by Mark Anderson: 36 ready to teach lessons, unplugged first, with lesson plans and slides.",
         body, d, ld=[
             {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "IDEAL Thinkers", "inLanguage": "en-GB", "publisher": {"@id": AUTHOR["@id"]}},
             AUTHOR,
             {"@type": "Course", "@id": COURSE_ID, "name": "IDEAL Thinkers", "url": SITE + "/",
              "description": "A free AI literacy and fluency curriculum for primary schools, Year 1 to Year 6: 36 lessons, each with a lesson plan and slides, unplugged first.",
              "provider": {"@id": AUTHOR["@id"]}, "author": {"@id": AUTHOR["@id"]}, "inLanguage": "en-GB",
              "educationalLevel": "Primary school, Key Stage 1 and Key Stage 2 (Year 1 to Year 6)", "typicalAgeRange": "5-11",
              "isAccessibleForFree": True, "license": LICENCE_URL, "copyrightHolder": {"@id": AUTHOR["@id"]}, "copyrightYear": 2026,
              "audience": {"@type": "EducationalAudience", "educationalRole": "teacher"},
              "teaches": ["How AI works: learn, spot, guess, check", "Questioning and checking what AI tells you", "Using AI ethically, safely and on purpose", "Keeping your own thinking in charge when learning with AI"],
              "hasPart": [{"@type": "Course", "name": f"Year {y['n']}: {y['title']}", "url": SITE + "/" + y["path"]} for y in DATA["years"]]},
             {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
         ])


# ---------- How it works ----------
def ideal_table():
    rows = "".join(
        f'<tr><th scope="row"><span class="b b-{l}">{l}</span> {n}</th><td>{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td></tr>'
        for l, n, a, b, c in IDEAL)
    return f"""<div class="table-wrap"><table class="ideal-table">
<thead><tr><th scope="col">Letter</th><th scope="col">Years 1 and 2</th><th scope="col">Years 3 and 4</th><th scope="col">Years 5 and 6</th></tr></thead>
<tbody>{rows}</tbody></table></div>"""


def build_how():
    d = 1
    phases = [("Remember When", "5 to 7 min", "Four quick retrieval questions from last lesson, earlier this year and a previous year. Spaced retrieval strengthens long term memory. If the answers show a gap, reteach it briefly before moving on."),
              ("Link It", "5 min", "A hook that connects to what children already know from their own lives."),
              ("Learn It", "10 to 12 min", "Explicit teaching of one big idea and its vocabulary, with a worked example and a teacher think aloud. The AI Loop and IDEAL words are always paired with the same pictures (dual coding)."),
              ("Try It", "15 to 20 min", "The signature activity: collaborative, practical and memorable, usually unplugged."),
              ("Own It", "10 min", "Pupils apply the idea independently or in pairs, usually by creating something."),
              ("IDEAL Check", "3 min", "Which IDEAL letter did we practise, and what does it look like in real life?"),
              ("Exit Ticket", "3 to 5 min", "Three short questions to check understanding and shape the next lesson.")]
    ph = "".join(f'<li><span class="ph-n">{e(n)}</span><span class="ph-t">{e(t)}</span><span class="ph-d">{e(x)}</span></li>' for n, t, x in phases)
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow">How it works</p>
<h1>How the parts fit together</h1>
<p class="lede">IDEAL Thinkers is the full, teachable AI Literacy strand of the Primary Digital Cognition Curriculum. Each part has one job: what pupils learn, the habits they build, the tools for teaching it, and how a lesson runs.</p>
</div></section>
<section class="wrap">
<ol class="ladder">
<li><h2>What pupils learn: five progression strands</h2><p>How AI works; staying in charge; safe, fair and honest; learning well; design and create. Each lesson plan names its strands, and the tracker records them. <a href="../progression/">Progression and coverage</a></p></li>
<li><h2>The habits they build: IDEAL</h2><p>Informed, Deliberate, Ethical, Accurate, Learning, with wording that grows with the children. Learning Well is how the L is taught: Try it first, Hint not answer, then Plan, use, prove. <a href="ideal/">IDEAL</a> <a href="learning-well/">Learning Well</a></p></li>
<li><h2>The tools for teaching it: the AI Loop and STAIR</h2><p>The AI Loop (Learn, Spot, Guess, Check) is a simple model of how AI that learns from examples works. STAIR is a prompting scaffold pupils use in Years 5 and 6. <a href="ai-loop/">The AI Loop</a></p></li>
<li><h2>How a lesson runs: seven phases, for teachers</h2><p>Remember When, Link It, Learn It, Try It, Own It, IDEAL Check and Exit Ticket, in 60 minutes. Pupils do not need to learn the phases. <a href="every-lesson/">Every lesson</a></p></li>
<li><h2>What it lines up with</h2><p>The Primary Digital Cognition Curriculum, the National Curriculum for computing, SEAME, UDL and cognitive science. <a href="../progression/#alignment">Alignment</a></p></li>
</ol>
<h2>AI literacy and AI fluency</h2>
<p><strong>AI literacy</strong> is knowing how the AI children meet works, at a level that fits their age; what it can and cannot do; and how it affects people, fairly or unfairly. Pupils show it by explaining these ideas in their own words and applying them to a new example.</p>
<p><strong>AI fluency</strong> is making good decisions about AI: whether to use it at all, what to ask, how to check what comes back, and how to keep the learning their own. In primary school, pupils practise these decisions through unplugged activities and teacher-led demonstrations, not by using AI tools themselves.</p>
</section>
"""
    page("how-it-works/", "How IDEAL Thinkers works: the AI Loop, IDEAL and Learning Well",
         "How IDEAL Thinkers fits together: five progression strands, the IDEAL habits with Learning Well, the AI Loop and STAIR, and the seven phase lesson shape.", body, d)

    # Every lesson
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow"><a href="../">How it works</a> / Every lesson</p>
<h1>Every lesson has the same shape</h1>
<p class="lede">A consistent structure is designed to lower cognitive load for pupils and teachers alike. The phases are for teachers to plan with; pupils do not need to learn them.</p>
</div></section>
<section class="wrap">
<ol class="phases">{ph}</ol>
<p>Individual lessons adjust these phase timings to suit their activities, and some add a short real-life story. Every plan fits within 60 minutes, most with a few minutes to spare.</p>
<h2>45 minute lessons</h2>
<p>Shorten the edges and keep the middle: two Remember When questions, a 2 minute Link It, any real life story in one sentence, a 2 minute IDEAL Check and the full exit ticket in 3 minutes. Keep the worked example, the key moment of Try It and Own It; if it still does not fit, use fewer examples, rounds or cards. Each plan says what to cut.</p>
<p class="pill-line"><span class="tag">Retrieve first, reteach if needed</span><span class="tag">Slides build on click</span><span class="tag">Unplugged first</span><span class="tag">No pupil accounts</span></p>
<p>Lesson 6 each year is the IDEAL Challenge and the end of unit assessment.</p>
<h2>IDEAL moments</h2>
<p>In each lesson, the day's IDEAL habit appears as a cue only at the moment pupils practise it. In Years 1 and 2, the teacher points to the cue and the class says the habit together. From Year 3, pupils name the habit the moment needs before the cue appears. Then the teacher asks the action question given in the lesson plan. <a href="../ideal/">More on IDEAL</a></p>
<h2>How it's built</h2>
<div class="grid grid-3">
<div class="card">{icon("brain", "i")}<h3>Grounded in cognitive science</h3><p>Spaced retrieval, concrete before abstract, worked examples and modelling, explicit vocabulary teaching, dual coding through consistent visual models, and frequent low stakes checks for understanding.</p></div>
<div class="card">{icon("people", "l")}<h3>Designed with UDL</h3><p>Every plan offers multiple ways to engage, to access content and to show understanding.</p></div>
<div class="card">{icon("slides", "d")}<h3>Slides built for low cognitive load</h3><p>Every slide builds on click in the order the teacher teaches it, as if writing on a whiteboard, so pupils meet one element at a time. Visuals carry meaning rather than decoration: each AI Loop step, each IDEAL habit and each recurring idea has its own icon, used identically in every lesson.</p></div>
</div>
<p>Teacher notes, answers and sources are in the lesson plan, not on the screen. New ideas and vocabulary are taught where pupils first need them. Earlier learning is retrieved first, and retaught briefly when Remember When or an exit ticket shows pupils have not got it yet.</p>
</section>"""
    page("how-it-works/every-lesson/", "Every lesson: the seven phase lesson shape | IDEAL Thinkers",
         "Every IDEAL Thinkers lesson follows the same seven phases: Remember When, Link It, Learn It, Try It, Own It, IDEAL Check and Exit Ticket.", body, 2)

    # AI Loop
    rows = [("Learn", "It learns from lots of examples (data) that people choose or create.", "Year 1: it learns from lots of examples. Year 5: training data, test data, permission and fairness."),
            ("Spot", "It finds patterns in those examples.", "Year 1: spotting a secret sorting rule. Year 4: patterns in words. Year 5: rules versus learning."),
            ("Guess", "It uses the patterns to make a prediction: a label, a next word, a video, a picture.", "Year 1: it makes a guess. Year 4: next word prediction and how sure it is. Year 6: generated images, text and voices."),
            ("Check", "It can be wrong without knowing. People check its guesses before they trust them.", "Every year: people check its guesses, from 'is it right?' in Year 1 to 'who is missing?' in Year 6. That is where IDEAL comes in.")]
    tr = "".join(f'<tr><th scope="row">{s}</th><td>{e(a)}</td><td>{e(b)}</td></tr>' for s, a, b in rows)
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow"><a href="../">How it works</a> / Teaching tools</p>
<h1>The AI Loop: Learn, Spot, Guess, Check</h1>
<p class="lede">How pupils understand AI that learns from examples (machine learning), the kind they meet most. It is a simple model: real systems are more complicated, and not every machine that makes a guess works this way. Every year group returns to it, so knowledge can build into a connected whole.</p>
</div></section>
<section class="wrap">
{loop_strip()}
<div class="table-wrap"><table><thead><tr><th scope="col">Step</th><th scope="col">What the AI does</th><th scope="col">How the idea grows</th></tr></thead><tbody>{tr}</tbody></table></div>
<p>Pupils meet the AI Loop in <a href="../../year-1/the-mystery-rule/">Year 1, The Mystery Rule</a>.</p>
{poster_block(2, "ai-loop")}
</section>"""
    page("how-it-works/ai-loop/", "The AI Loop: Learn, Spot, Guess, Check | IDEAL Thinkers",
         "The AI Loop is a simple model of how AI that learns from examples works, in four steps, growing from Year 1 to Year 6.", body, 2)

    # IDEAL
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow"><a href="../">How it works</a> / Habits</p>
<h1>IDEAL: how we use AI well</h1>
<p class="lede">My framework for informed learning with AI. Every lesson is tagged with the IDEAL letters it develops, and the wording grows with the children.</p>
</div></section>
<section class="wrap">
<h2>The habits grow with the children</h2>
{ideal_table()}
<h2>IDEAL moments</h2>
<p>IDEAL is not a logo in the corner of every slide. In each lesson, the day's IDEAL habit appears as a cue only on the click where pupils actually practise it, for example "A: Check it before you trust it" just as pupils go looking for evidence. In Years 1 and 2, the teacher points to the cue and the class says the habit together. From Year 3, pupils name the habit the moment needs before the cue appears, which shows they know which habit fits. Then the teacher asks the action question. Every lesson plan lists its IDEAL moments, with slide numbers, the question and the answers. The routine is taught in <a href="../../year-1/does-it-guess/">Year 1 Lesson 1</a> and used in every lesson after that. Learning Well is how the L habit is taught: <a href="../learning-well/">more on Learning Well</a>.</p>
{poster_block(2, "ideal-habits")}
</section>"""
    page("how-it-works/ideal/", "IDEAL: Informed, Deliberate, Ethical, Accurate, Learning | IDEAL Thinkers",
         "IDEAL is Mark Anderson's framework for informed learning with AI, with wording that grows from Year 1 to Year 6.", body, 2)

    # Learning Well
    lw = [("KS1", "Year 2 Lesson 3", "year-2/try-it-first/", "Try it first", "Explain that their brain grows when they do the hard thinking; use technology to practise and to show what they know, after they have had a go themselves."),
          ("Lower KS2", "Year 3 Lesson 4", "year-3/hint-not-answer/", "Hint, not answer", "Tell the difference between help that makes them think (a hint, a question, feedback) and help that thinks for them (the answer); ask for the first kind."),
          ("Upper KS2", "Year 5 Lesson 5", "year-5/climb-the-stair/", "Plan, use, prove", "Plan how AI could support a specific learning goal using STAIR (Specific, Tell, Actionable, Iterate, Role); use it to quiz themselves and to get feedback on a draft, deciding what to act on; then prove the learning is theirs by explaining it without the tool.")]
    tr = "".join(f'<tr><th scope="row">{p}<br><a href="../../{u}">{w}</a></th><td><strong>{h}</strong></td><td>{e(x)}</td></tr>' for p, w, u, h, x in lw)
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow"><a href="../">How it works</a> / Habits</p>
<h1>Learning Well with AI</h1>
<p class="lede">"Knowing how to use technology to support learning" is the most important outcome in any digital curriculum, and usually the vaguest. Here it has its own progression, as the taught form of the IDEAL L habit, drawing on cognitive science: when the machine does the thinking, the child learns less.</p>
</div></section>
<section class="wrap">
<p>It is taught explicitly once in each phase, and a short Learning Well prompt appears in other lessons so it becomes a habit rather than a topic.</p>
<div class="table-wrap"><table><thead><tr><th scope="col">Phase</th><th scope="col">The habit</th><th scope="col">What pupils can do</th></tr></thead><tbody>{tr}</tbody></table></div>
</section>"""
    page("how-it-works/learning-well/", "Learning Well with AI: Try it first, Hint not answer, Plan use prove | IDEAL Thinkers",
         "How IDEAL Thinkers teaches pupils to use AI to support their learning, with STAIR in Upper KS2.", body, 2)


# ---------- Map, years, lessons ----------
def build_map():
    d = 1
    filters = '<div class="filters" role="group" aria-label="Filter lessons">' \
              '<span class="f-label">Year</span>' + "".join(
        f'<button type="button" class="f-btn" data-f="year" data-v="{y["n"]}" aria-pressed="false">{y["n"]}</button>' for y in DATA["years"]) + \
              '<span class="f-label">IDEAL</span>' + "".join(
        f'<button type="button" class="f-btn f-{x}" data-f="letter" data-v="{x}" aria-pressed="false">{x}</button>' for x in "IDEAL") + \
              '<button type="button" class="f-btn f-clear" data-f="clear">Show all</button></div>'
    secs = ""
    for y in DATA["years"]:
        cards = "".join(lesson_card(d, l) for l in y["lessons"])
        secs += f"""<section class="map-year y{y['n']}" data-year="{y['n']}">
<h2><a href="{rel(d, y['path'])}">Year {y['n']}: {e(y['title'])}</a></h2>
<p class="bq">Big question: {e(y['big_question'])}</p>
<div class="grid grid-3">{cards}</div>
</section>"""
    spots = "".join(
        f'<a class="spot" href="{rel(d, LESSONS[c]["path"])}" style="left:{x}%;top:{y}%;width:{w}%;height:{h}%">'
        f'<span class="vh">Year {LESSONS[c]["year"]["n"]}, Lesson {LESSONS[c]["n"]}: {e(LESSONS[c]["title"])}</span></a>'
        for c, (x, y, w, h) in SPOTS.items())
    targets = {f"year-{y['n']}": (y["path"], f"Year {y['n']}: {y['title']}") for y in DATA["years"]}
    targets.update({"What pupils learn": ("progression/", "What pupils learn: the five progression strands"),
                    "The habits grow with the children": ("how-it-works/ideal/", "The habits they build: IDEAL, with Learning Well"),
                    "Tools for teaching it": ("how-it-works/ai-loop/", "Tools for teaching it: the AI Loop and STAIR"),
                    "Every lesson": ("how-it-works/every-lesson/", "Every lesson"),
                    "IDEAL": ("how-it-works/ideal/", "IDEAL: how we use AI well")})
    spots += "".join(
        f'<a class="spot" href="{rel(d, targets[k][0])}" style="left:{x}%;top:{y}%;width:{w}%;height:{h}%">'
        f'<span class="vh">{e(targets[k][1])}</span></a>'
        for k, (x, y, w, h) in EXTRA_SPOTS.items())
    roadmap = f"""<section class="wrap roadmap-sec">
<h2>The road map</h2>
<p>Click any lesson on the road map to open it, or download the A3 poster for your classroom wall. <a href="../progression/">See how the learning builds</a></p>
<figure class="roadmap">
<div class="roadmap-frame">
<img src="../images/ideal-thinkers-road-map.webp" width="2482" height="1754" alt="The IDEAL Thinkers curriculum road map: a road winding through all 36 lessons from Year 1 to Year 6, ending at secondary school. Along the bottom: what pupils learn (the five progression strands), the habits they build (IDEAL with Learning Well), and the tools for teaching it (the AI Loop and STAIR).">
{spots}
</div>
<figcaption><a class="btn" href="https://drive.google.com/uc?export=download&amp;id={ROADMAP_PDF}">Download the A3 road map (PDF, print at A3)</a> <a class="btn btn-ghost" href="../images/ideal-thinkers-road-map.webp">Open full size</a></figcaption>
</figure>
</section>"""
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow">Curriculum map</p>
<h1>All 36 lessons at a glance</h1>
<p class="lede">Six lessons per year, planned as a half-term unit. Digital Cognition links: <abbr title="Digital Citizenship">DC</abbr> Digital Citizenship, <abbr title="Digital Literacy">DL</abbr> Digital Literacy, <abbr title="Computer Science">CS</abbr> Computer Science.</p>
</div></section>
{roadmap}
<div class="wrap map"><h2 class="map-h">Every lesson</h2>{filters}
<p class="f-count" aria-live="polite"></p>
{secs}</div>
<script src="../js/map.js" defer></script>"""
    page("curriculum-map/", "Curriculum map: all 36 lessons | IDEAL Thinkers",
         "Every IDEAL Thinkers lesson from Year 1 to Year 6, with its big idea, IDEAL letters and Digital Cognition links.", body, d)


BY_END = {
    1: "pupils can tell a machine that follows steps from one that makes guesses, explain that AI learns from examples, and say who checks its guesses.",
    2: "pupils can check and fix an AI's guess, explain why missing examples cause mistakes, try first before asking for help, and stop and ask a grown-up before telling a machine anything personal.",
    3: "pupils can explain how a feed and a voice assistant use their data, say how AI can help people who see, hear or speak differently, ask for a hint rather than an answer, and say when AI has helped with their work.",
    4: "pupils can explain that a chatbot builds answers by predicting likely words, why sounding sure is not the same as being right, why a chatbot is not a friend, and how a better question changes the answer.",
    5: "pupils can tell rules written by people from patterns learned from examples, explain training and test data, ask whose data was used and who might be left out, and plan how AI could help them learn without doing the learning for them.",
    6: "pupils can use a checking routine and trusted sources to decide whether to trust or share a picture, voice or video, explain how AI can magnify unfairness, weigh the costs of AI against its benefits, say who must answer for an AI decision, and design AI for a real problem.",
}


def build_years():
    ys = DATA["years"]
    for i, y in enumerate(ys):
        d = 1
        prev_y = ys[i - 1] if i > 0 else None
        next_y = ys[i + 1] if i < len(ys) - 1 else None
        where = []
        if prev_y:
            where.append(f'Before this, in Year {prev_y["n"]}, pupils studied <a href="{rel(d, prev_y["path"])}">{e(prev_y["title"])}</a>.')
        if next_y:
            where.append(f'Next, in Year {next_y["n"]}, pupils move on to <a href="{rel(d, next_y["path"])}">{e(next_y["title"])}</a>.')
        cards = "".join(lesson_card(d, l) for l in y["lessons"])
        TY = TEACHER["years"][str(y["n"])]
        steps = ""
        for k, l in enumerate(y["lessons"]):
            txt = re.sub(r"^L\d+:\s*", "", TY["journey"][k]) if k < len(TY["journey"]) else ""
            chal = ' <span class="tag tag-challenge">IDEAL Challenge</span>' if l["challenge"] else ""
            steps += f'<li><div><a href="{rel(d, l["path"])}">Lesson {l["n"]}: {e(l["title"])}</a>{chal}</div><span>{e(txt[:1].upper() + txt[1:])}</span></li>'
        first = "".join(f"<li>{codes_text(d, x)}</li>" for x in TY["first_time"])
        yn = str(y["n"])
        deps = "".join("<li>" + codes_text(d, re.sub(r"(?<![Y\d])L(\d)", lambda m: "Y" + yn + "L" + m.group(1), x)) + "</li>" for x in TY["extra_dependencies"] or [])
        ahead = [(l, TEACHER["lessons"][l["code"]]) for l in y["lessons"] if TEACHER["lessons"][l["code"]].get("unit_advance")]
        plan_ahead = ("<p><strong>Plan ahead.</strong> " + " ".join(f'<a href="{rel(d, l["path"])}">Lesson {l["n"]}</a>: {e(t["advance"])}.' for l, t in ahead) + "</p>") if ahead else ""
        start = "Pupils start the curriculum here, from their everyday experience." if y["n"] == 1 else e(" ".join(TY["starting_point"]) if isinstance(TY["starting_point"], list) else TY["starting_point"])
        journey = f"""<section class="wrap journey-sec" aria-labelledby="journey-h">
<h2 id="journey-h">How this unit builds</h2>
<p><strong>Starting point.</strong> {start}</p>
<ol class="journey">{steps}</ol>
{plan_ahead}<p><strong>Assessment.</strong> {e(" ".join(TY["challenge"]) if isinstance(TY["challenge"], list) else TY["challenge"])} <a href="../assessment/">How assessment works</a></p>
</section>
<section class="wrap"><div class="card first-time" id="starting">
<h2>Starting Year {y['n']} with pupils new to IDEAL Thinkers</h2>
{"<p>Year 1 is the start of the curriculum: no introduction is needed.</p>" if y["n"] == 1 else f"<ul>{first}</ul>"}
{f"<h3>Lessons in this unit that depend on earlier ones</h3><ul>{deps}</ul>" if deps else ""}
<p class="small">Pupils who have had the earlier units only need the Remember When retrieval in each lesson. More in <a href="../using-the-lessons/">Using the lessons</a>.</p>
</div></section>"""
        bot = chatty("chatty chatty-head", "Chatty, the class chatbot pupils meet in Year 4") if y["n"] == 4 else ""
        body = f"""<section class="page-head year-head"><div class="wrap{' head-grid' if bot else ''}"><div>
<p class="eyebrow"><a href="../curriculum-map/">Curriculum map</a> / Year {y['n']}</p>
<div class="yh">{year_icon(y["n"], 44)}<h1>Year {y['n']}: {e(y['title'])}</h1></div>
<p class="bq big">Big question: {e(y['big_question'])}</p>
<p><strong>By the end of this unit,</strong> {e(BY_END[y['n']])}</p>
<p>{' '.join(where)}</p>
<p><a class="btn btn-ghost" href="https://drive.google.com/drive/folders/{y['folder']}">Open the Year {y['n']} folder in Google Drive</a></p>
</div>{bot}</div></section>
{journey}
<section class="wrap"><h2>Lessons</h2><div class="grid grid-3">{cards}</div>
<p class="note">Lesson 6 is the IDEAL Challenge, where pupils pull the unit together to make or decide something. It doubles as the end of unit assessment task: <a href="../assessment/">how assessment works</a>.</p>
</section>"""
        page(y["path"], f"Year {y['n']} AI literacy: {y['title']} | IDEAL Thinkers",
             f"Year {y['n']} AI literacy unit, {y['title']}: {y['big_question']} Six free lessons with plans and slides.", body, d, y["n"],
             ld=[{"@type": "Course", "@id": SITE + "/" + y["path"] + "#unit", "name": f"Year {y['n']}: {y['title']}", "url": SITE + "/" + y["path"],
                  "description": f"Year {y['n']} AI literacy unit. Big question: {y['big_question']}", "isPartOf": {"@id": COURSE_ID},
                  "provider": {"@id": AUTHOR["@id"]}, "inLanguage": "en-GB", "educationalLevel": f"Year {y['n']}", "typicalAgeRange": AGES[y["n"]],
                  "isAccessibleForFree": True, "license": LICENCE_URL,
                  "hasPart": [{"@type": "LearningResource", "name": l["title"], "url": SITE + "/" + l["path"]} for l in y["lessons"]]}],
             crumbs=[(f"Year {y['n']}: {y['title']}", y["path"])])


def build_year_groups():
    d = 1
    blocks = ""
    for y in DATA["years"]:
        chal = ' <span class="tag tag-challenge">IDEAL Challenge</span>'
        items = "".join(f'<li><a href="{rel(d, l["path"])}">{l["n"]}. {e(l["title"])}</a>{chal if l["challenge"] else ""}</li>' for l in y["lessons"])
        blocks += f"""<article class="card yg y{y['n']}">
{year_icon(y['n'])}
<h2><a href="{rel(d, y['path'])}"><span class="yg-n">Year {y['n']}</span> {e(y['title'])}</a></h2>
<p class="bq">{e(y['big_question'])}</p>
<ol class="yg-list">{items}</ol>
<p><a class="btn btn-ghost" href="{rel(d, y['path'])}">Year {y['n']} overview</a></p>
</article>"""
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow">Year groups</p>
<h1>Six units, one for each year</h1>
<p class="lede">Six lessons per year, planned as a half-term unit. The sixth lesson in each year is an IDEAL Challenge, where pupils pull the unit together to make or decide something.</p>
</div></section>
<section class="wrap"><div class="grid grid-3">{blocks}</div></section>"""
    page("year-groups/", "Year groups: Year 1 to Year 6 | IDEAL Thinkers",
         "The six IDEAL Thinkers units, one for each year from Year 1 to Year 6, with every lesson listed.", body, d)


def file_block(kind, fid, label):
    if kind == "slides":
        base = f"https://docs.google.com/presentation/d/{fid}"
        dl, dl_label = f"{base}/export/pptx", "Download PowerPoint"
    else:
        base = f"https://docs.google.com/document/d/{fid}"
        dl, dl_label = f"{base}/export?format=docx", "Download Word"
    return f"""<div class="file">
<h3 class="file-h">{icon("slides" if kind == "slides" else "plan", "d" if kind == "slides" else "i", 22)}{label}</h3>
<p class="file-btns"><a class="btn" href="{base}/copy" aria-label="Make a copy of the {label.lower()}">Make a copy</a><a class="btn btn-ghost" href="{dl}" aria-label="{dl_label}: {label.lower()}">{dl_label}</a><a class="btn btn-ghost" href="{base}/preview" aria-label="Preview the {label.lower()}">Preview</a></p>
</div>"""


SAFE_TOPIC = {"Y2L4": "personal information", "Y3L2": "privacy and what voice assistants record",
              "Y4L2": "chatbots that seem like friends", "Y6L1": "fake images and images of real people"}


def build_lessons():
    for y in DATA["years"]:
        ls = y["lessons"]
        for i, l in enumerate(ls):
            d = 2
            prev_l = ls[i - 1] if i > 0 else None
            next_l = ls[i + 1] if i < len(ls) - 1 else None
            T = TEACHER["lessons"][l["code"]]
            flags = ""
            if l["flag"] == "safeguarding":
                flags += f'<p class="flag flag-safe"><strong>Safeguarding.</strong> This lesson deals with {SAFE_TOPIC.get(l["code"], "a sensitive topic")}. The plan flags this, and any disclosure should be handled through your school\'s safeguarding procedures. <a href="{rel(d, "safety/")}">More on safety</a></p>'
            if l["flag"] == "demo":
                flags += f'<p class="flag flag-demo"><strong>Teacher demonstration.</strong> Where a demonstration helps, the teacher runs it on a school approved tool, previews it first and stays in control. The lesson can also be taught without a live demonstration, using prepared results or an unplugged version. No pupil accounts. <a href="{rel(d, "safety/")}">More on safety</a></p>'
            ch = '<span class="tag tag-challenge">IDEAL Challenge</span>' if l["challenge"] else ""
            sess = f' <span class="tag">{e(l["sessions"])}</span>' if l["sessions"] else ""
            ican = "".join(f"<li>{e(s)}</li>" for s in l["i_can"])
            nav = '<nav class="pn" aria-label="Lessons">'
            nav += f'<a class="pn-prev" href="{rel(d, prev_l["path"])}"><span>Previous</span>Lesson {prev_l["n"]}: {e(prev_l["title"])}</a>' if prev_l else '<span></span>'
            nav += f'<a class="pn-next" href="{rel(d, next_l["path"])}"><span>Next</span>Lesson {next_l["n"]}: {e(next_l["title"])}</a>' if next_l else f'<a class="pn-next" href="{rel(d, y["path"])}"><span>Back to</span>Year {y["n"]}: {e(y["title"])}</a>'
            nav += "</nav>"
            time = "Two sessions of 60 minutes" if l["sessions"] else "60 minutes, with a 45 minute version in the plan"
            devices = "Optional: one device per pair for Scratch, or the unplugged version in the plan" if l["code"] == "Y5L1" else "None needed"
            demo = "Optional: the teacher runs it on a school approved tool, or uses the prepared results in the plan" if l["flag"] == "demo" else "None"
            if l["flag"] == "safeguarding":
                safe = f'This lesson deals with {SAFE_TOPIC.get(l["code"], "a sensitive topic")}. Read the plan\'s Safeguarding row and brief your DSL. <a href="{rel(d, "safety/")}">Safety</a>'
            elif l["code"] == "Y1L5":
                safe = f'AI picture tools can make something unsuitable: preview every picture before pupils see it. Read the plan\'s Safeguarding row. <a href="{rel(d, "safety/")}">Safety</a>'
            elif l["code"] in DISCLOSURE:
                safe = f'Discussion can prompt disclosures. Read the plan\'s Safeguarding row and follow your school\'s procedures. <a href="{rel(d, "safety/")}">Safety</a>'
            else:
                safe = ""
            same = [r["code"] for a in T["already"] for r in a["from"] if r["code"][:2] == l["code"][:2]]
            earlier = [r["code"] for a in T["already"] for r in a["from"] if r["code"][:2] != l["code"][:2]]
            if l["challenge"]:
                prior = 'End of unit assessment: teach Lessons 1 to 5 first. <a href="#before">Before teaching this lesson</a>'
            elif not T["already"]:
                prior = "No formal prerequisites."
            else:
                bits = []
                if same: bits.append("earlier lessons in this unit")
                if earlier: bits.append("learning from earlier years")
                prior = "Builds on " + " and ".join(bits) + '. <a href="#before">Before teaching this lesson</a>'
            prep = f'About {T["prep_time"].replace("about ", "")}, plus the plan\'s Teacher subject knowledge.' if T["prep_time"] else "See the plan."
            rows = [("Lesson", f'Lesson {l["n"]} of 6 in Year {y["n"]}: {e(y["title"])}'), ("Time", time),
                    ("Pupils learn", f'<ul class="plain">{ican}</ul>'),
                    ("You need", e(T["need"]) if T.get("need") else "See What to prepare below."),
                    ("Preparation", f'{prep}' + (f' <strong>Plan ahead:</strong> {e(T["advance"])}.' if T.get("advance") else "") + f'<details><summary>What to prepare</summary><p>{e(T["prep"])}</p></details>'),
                    ("Pupil devices", devices), ("Demonstration", demo)]
            if safe: rows.append(("Safeguarding", safe))
            rows.append(("Prior learning", prior))
            summary = '<section class="card prep" aria-labelledby="prep-h"><h2 id="prep-h">Preparing to teach</h2><dl>' + "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in rows) + "</dl></section>"
            B = T["before"]
            if B["understand"]:
                know = "<ul>" + "".join(f"<li>{e(x)}</li>" for x in B["understand"]) + "</ul>"
                where = "<ul>" + "".join(f'<li><span class="scope">{x["scope"]}</span> {lesson_ref(d, x["code"], x["slides"])}</li>' for x in B["where"]) + "</ul>"
                if B["also"]:
                    where += '<p class="small">It also draws on ' + ", ".join(lesson_ref(d, c, title=False) for c in B["also"]) + ".</p>"
                if_not = codes_text(d, B["if_not"])
                if B.get("check"):
                    qn = " and ".join(str(x) for x in B["check"])
                    if_not = f'<strong>Check first:</strong> Remember When question{"s" if len(B["check"]) > 1 else ""} {qn} (slide 2) test{"" if len(B["check"]) > 1 else "s"} this. If most pupils answer well, carry on. If not: {if_not}'
                elif not l["challenge"]:
                    if_not = f'<strong>Check first:</strong> ask pupils to explain the idea in their own words. If most can, carry on. If not: {if_not}'

            else:
                know, where = "<p>No formal prerequisites: this lesson starts from pupils' everyday experience.</p>", "<p>Nothing earlier is needed.</p>"
                if_not = "Nothing to do: start the lesson as planned."
            if B["routines"]:
                know += '<p class="small">Routines it uses: ' + ", ".join(B["routines"]) + ".</p>"
            if B["recall"]:
                where += '<p class="small">Remember When (slide 2) recalls ' + ", ".join(lesson_ref(d, c, title=False) for c in B["recall"]) + ". These are retrieval questions: if your class has not had those lessons, swap them for a question about pupils' own experience. That does not replace any prerequisite above.</p>"
            before = f"""<section class="before" id="before" aria-labelledby="before-h"><h2 id="before-h">Before teaching this lesson</h2><div class="before-grid">
<div><h3>Pupils should already understand</h3>{know}</div>
<div><h3>Where this was taught</h3>{where}</div>
<div><h3>If your pupils haven't covered this</h3><p>{if_not}</p></div>
<div><h3>What this lesson adds</h3><p>{e(B["adds"])}</p></div></div></section>"""
            look = ""
            if T["exit"] or T["look_for"]:
                look = '<h2>What to look for</h2>'
                if T["exit"]: look += f'<p><strong>Exit ticket:</strong> {e(T["exit"])}</p>'
                if T["look_for"]: look += f'<p><strong>Look for</strong> {e(T["look_for"])}</p>'
                look += f'<p class="small">This evidence feeds the tracker for {e(T["strands"] or "the progression strands")}, and the unit ends with the <a href="{rel(d, ls[5]["path"])}">IDEAL Challenge</a>. Answers are in the plan.</p>'

            body = f"""<section class="page-head lesson-head"><div class="wrap">
<p class="eyebrow"><a href="{rel(d, 'curriculum-map/')}">Curriculum map</a> / <a href="{rel(d, y['path'])}">Year {y['n']}: {e(y['title'])}</a></p>
<p class="kicker">Year {y['n']}, Lesson {l['n']} {ch}{sess}</p>
<div class="yh">{year_icon(y['n'], 44)}<h1>{e(l['title'])}</h1></div>
<p class="lede">{e(l['big_idea'])}</p>
<p class="card-meta">{badges(l['ideal'])}<span class="links">Links: {links_text(l['links'])}</span></p>
</div></section>
<section class="wrap lesson-body">
<div class="lesson-main">
{summary}
{before}
<h2>The signature activity</h2>
<p>{e(l['activity'])}</p>
<h2>The slides</h2>
<div class="embed"><iframe src="https://docs.google.com/presentation/d/{l['slides']}/embed?start=false&amp;loop=false" title="Slides: {e(l['title'])}" loading="lazy" allowfullscreen></iframe></div>
<p class="note">Teacher notes and answers are in the lesson plan, and printable resources are at the end of the deck.</p>
{look}
</div>
<aside class="lesson-side">
{file_block('slides', l['slides'], 'Slides')}
{file_block('plan', l['plan'], 'Lesson plan')}
</aside>
</section>
<div class="wrap">{nav}</div>"""
            page(l["path"], f"{l['title']} | Year {y['n']} AI literacy lesson | IDEAL Thinkers",
                 f"Year {y['n']} AI literacy lesson: {l['big_idea']} Free lesson plan and slides.", body, d, y["n"],
                 ld=[{"@type": "LearningResource", "name": l["title"], "url": SITE + "/" + l["path"],
                      "description": f"{l['big_idea']} {l['activity']}", "learningResourceType": ["Lesson plan", "Presentation"],
                      "educationalLevel": f"Year {y['n']}", "typicalAgeRange": AGES[y["n"]], **({} if l["sessions"] else {"timeRequired": "PT60M"}),
                      "teaches": l["i_can"], "inLanguage": "en-GB", "isAccessibleForFree": True, "license": LICENCE_URL,
                      "author": {"@id": AUTHOR["@id"]}, "isPartOf": {"@id": SITE + "/" + y["path"] + "#unit"},
                      "audience": {"@type": "EducationalAudience", "educationalRole": "teacher"}}],
                 crumbs=[(f"Year {y['n']}: {y['title']}", y["path"]), (l["title"], l["path"])])


# ---------- Other pages ----------
def build_progression():
    d = 1
    prog = [("How AI works", "AI learns from examples, spots patterns and guesses; it can be wrong.", "Feeds learn from what we do; chatbots predict words and work in probabilities.", "Rules versus learning; training and testing; generated media; bias traced to data."),
            ("Staying in charge", "People make AI and should stay in charge; we check its guesses.", "Chatbots are not friends; sounding sure is not being right.", "People must explain and answer for AI decisions; different people are affected differently."),
            ("Safe, fair and honest", "Some things we never tell a machine; missing examples cause mistakes.", "Privacy and listening devices; honesty about AI help; designing for children's wellbeing.", "Permission, consent for images of real people, bias, environmental cost."),
            ("Learning Well", "Try it first.", "Hint, not answer.", "Plan, use, prove."),
            ("Design and create", "Robot Rules; directing an AI picture.", "A healthier feed; a chatbot rulebook.", "Training a class model; designing AI for good.")]
    pt = "".join(f'<tr><th scope="row">{e(a)}</th><td>{e(b)}</td><td>{e(c)}</td><td>{e(x)}</td></tr>' for a, b, c, x in prog)
    cov = [("KS1", None), ("Understanding what AI is", "Y1 L1, Y1 L2, Y1 L3"), ("Identifying common AI applications", "Y1 L4, Y2 L5"),
           ("Basic understanding of ethical behaviour with AI tools", "Y1 L6, Y2 L4, Y2 L6"), ("Simple AI games and activities", "Every KS1 lesson"),
           ("Creating AI images using simple tools", "Y1 L5 (pupils direct a teacher demonstration)"), ("KS2", None),
           ("Basic concepts of machine learning and algorithms", "Y3 L1, Y4 L1, Y4 L5, Y5 L1, Y5 L2, Y5 L6"),
           ("Exploring real-world AI applications", "Y3 L1, Y3 L2, Y3 L3, Y6 L3"), ("Discussing bias in AI and its implications", "Y5 L4, Y6 L2"),
           ("Creating basic AI projects and experiments", "Y5 L6, Y6 L6"), ("Learning prompt crafting for AI tools", "Y4 L4, Y5 L5"),
           ("Understanding the role of AI in automating tasks and enhancing productivity", "Y6 L3"),
           ("Ethical considerations, including AI bias and transparency", "Y3 L5, Y5 L3, Y6 L2, Y6 L5"), ("Across the other strands", None),
           ("Knowing how to use technology to support learning (DL)", "Learning Well progression: Y2 L3, Y3 L4, Y5 L5, plus prompts throughout"),
           ("Understanding deep fakes and AI in TV, media and social media (DC)", "Y6 L1, Y3 L1"),
           ("Copyright, fair use and Creative Commons (DC)", "Y5 L3, Y3 L5"),
           ("Recognising the importance of keeping information private (DC)", "Y2 L4, Y3 L2, Y4 L6"),
           ("Evaluating the credibility of online information (DL)", "Y2 L1, Y4 L3, Y6 L1"),
           ("Understanding data and simple ways to represent it; problem solving through patterns (CS)", "Y1 L3, Y2 L2, Y5 L1, Y5 L2")]
    ct = ""
    for a, b in cov:  # noqa
        ct += f'<tr class="grp"><th colspan="2" scope="colgroup">{e(a)}</th></tr>' if b is None else f'<tr><th scope="row">{e(a)}</th><td>{codes_html(d, b)}</td></tr>'
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow">Progression and coverage</p>
<h1>How the learning builds</h1>
<p class="lede">Pupils' learning is tracked in five progression strands, the same five used in the Assessment Tracker, across KS1, Lower KS2 and Upper KS2. The IDEAL habits, Learning Well and the AI Loop are how they are taught. Below: where each AI Literacy outcome is taught, and how it aligns with the National Curriculum.</p>
<p><a class="btn btn-ghost" href="{GUIDE_URL}">The Curriculum Guide (a one document overview)</a></p>
</div></section>
<section class="wrap">
<h2>Progression by strand</h2>
<div class="table-wrap"><table><thead><tr><th scope="col">Progression strand</th><th scope="col">KS1</th><th scope="col">Lower KS2</th><th scope="col">Upper KS2</th></tr></thead><tbody>{pt}</tbody></table></div>
<h2 id="coverage">Coverage of the AI Literacy outcomes</h2>
<div class="table-wrap"><table class="cov"><thead><tr><th scope="col">Primary Digital Cognition Curriculum outcome</th><th scope="col">Where it is taught</th></tr></thead><tbody>{ct}</tbody></table></div>
<h2 id="alignment">Alignment</h2>
<p><strong>National Curriculum for computing (England), taught directly:</strong> KS1, use technology safely and respectfully, keeping personal information private, and know where to go for help (Y1 L6, Y2 L4); recognise common uses of information technology beyond school (Y1 L1, Y2 L5). KS2, use technology safely, respectfully and responsibly, and identify ways to report concerns about content and contact (Y4 L2, Y6 L1); be discerning in evaluating digital content (Y4 L3, Y6 L1); use selection in programs (Y5 L1, Scratch version).</p>
<p><strong>Relevant connections:</strong> how feeds choose and rank what we see (Y1 L4, Y3 L1) connects to the KS2 statement on search results, but does not replace teaching search. The current curriculum does not require AI to be taught.</p>
<p><strong>SEAME</strong>, from the Raspberry Pi Computing Education Research Centre, is used as a lens to check coverage. For example: engines, Y4 L1 and Y5 L2; models, Y5 L1 and Y5 L6; applications, Y2 L5 and Y3 L1 to L3; social and ethical, Y4 L2, Y5 L3 and Y6 L1 to L5.</p>
<p><strong>The new computing curriculum:</strong> BCS is drafting a revised computing curriculum for first teaching from September 2028, and the Curriculum and Assessment Review recommended that it include AI. It is not yet statutory. IDEAL Thinkers will be mapped against the draft when it is published (checked October 2026).</p>
<p><strong>Wider curriculum:</strong> RSHE, science, maths, English, geography and careers links are flagged in each lesson plan.</p>
</section>"""
    page("progression/", "Progression and coverage | IDEAL Thinkers",
         "How IDEAL Thinkers builds from KS1 to Upper KS2, and where each AI Literacy outcome is taught.", body, d)


def build_safety():
    d = 1
    sg = [LESSONS[c] for c in ("Y2L4", "Y3L2", "Y4L2", "Y6L1")]
    dis = [LESSONS[c] for c in ("Y1L6", "Y3L1", "Y4L6", "Y5L3", "Y6L6")]
    dm = [LESSONS[c] for c in ("Y1L5", "Y3L3", "Y5L5", "Y5L6")]
    li = lambda ls: "".join(f'<li><a href="{rel(d, l["path"])}">Year {l["year"]["n"]}, Lesson {l["n"]}: {e(l["title"])}</a></li>' for l in ls)
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow">Safety</p>
<h1>Technology, safety and safeguarding</h1>
<p class="lede">Every lesson can be taught without pupil devices. Concepts outlast tools.</p>
</div></section>
<section class="wrap">
<div class="grid grid-2">
<div class="card">{icon("unplug", "e")}<h2>Unplugged first</h2><p>Every lesson can be taught without pupil devices. Concepts outlast tools.</p></div>
<div class="card">{icon("nouser", "i")}<h2>No pupil accounts</h2><p>IDEAL Thinkers never needs a pupil to use an AI tool or account. Age limits differ by tool and change often: some tools are for 13 and over with a parent's permission, some for 18 and over. Where a demonstration helps, the teacher runs it on a school approved tool, previews it first and stays in control. Every demonstration lesson can also be taught without one, using prepared results or an unplugged version.</p></div>
<div class="card">{icon("clipboard", "a")}<h2>Check your school's position</h2><p>Follow your school's AI policy and data protection guidance before using any tool, and never enter pupils' personal information. A school approved tool is one your school has checked for data protection and for filtering and monitoring. Check whether pupils' school accounts (for example Google Workspace for Education or Microsoft 365) already give them access to AI tools.</p></div>
<div class="card">{icon("heartshield", "l")}<h2>Safeguarding</h2><p>Four lessons deal directly with privacy, chatbot relationships and images of real people, and five more can prompt disclosures. Each plan's Safeguarding row says what to do, and any disclosure should be handled through your school's safeguarding procedures. Brief your DSL on all nine.</p></div>
</div>
<div class="grid grid-2">
<div><h2>The safeguarding lessons</h2><ul class="list">{li(sg)}</ul><h2>Lessons that can prompt disclosures</h2><ul class="list">{li(dis)}</ul></div>
<div><h2>The teacher demonstration lessons</h2><ul class="list">{li(dm)}</ul></div>
</div>
<h2>The guidance it follows</h2>
<p>This approach follows <a href="https://www.gov.uk/government/publications/keeping-children-safe-in-education--2">Keeping children safe in education 2026</a>, which lists harmful online interaction with other users or with generative AI applications that simulate this as a contact risk; the DfE's <a href="https://www.gov.uk/government/publications/generative-artificial-intelligence-in-education">Generative AI in education</a> guidance and <a href="https://www.gov.uk/government/publications/generative-ai-product-safety-standards">Generative AI: product safety standards</a>; and the UKCIS advice on <a href="https://www.gov.uk/government/publications/sharing-nudes-and-semi-nudes-advice-for-education-settings-working-with-children-and-young-people">sharing nudes and semi-nudes</a>, which covers AI-generated images.</p>
</section>"""
    page("safety/", "Technology, safety and safeguarding | IDEAL Thinkers",
         "IDEAL Thinkers is unplugged first, with no pupil accounts and teacher-led demonstrations only.", body, d)


def build_assessment():
    d = 1
    t = f"https://docs.google.com/spreadsheets/d/{TRACKER}"
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow">Assessment</p>
<h1>Assessment</h1>
<p class="lede">Each lesson has three "I can" statements and a three question exit ticket. Each IDEAL Challenge doubles as the end of unit assessment, where pupils show what they understand on their own.</p>
</div></section>
<section class="wrap">
<h2>Where the evidence comes from</h2>
<p>The exit ticket is the last slide of every lesson, and its questions and answers are in the lesson plan. One question always asks pupils to apply the idea to something they have not seen in the lesson. Sort the answers into got it, nearly and not yet: the middle pile chooses the next Remember When question, and you reteach briefly if the last pile is large.</p>
<p>At the end of each unit, the IDEAL Challenge and that unit's exit tickets give one judgement per pupil for each of the five progression strands. Team work is useful feedback, but every judgement rests on what each pupil shows on their own.</p>
<h2>Secure, developing and not yet</h2>
<p>Secure means the pupil explains the idea with reasons, without prompting, and applies it to a new case. Developing means they show the idea with prompting, or explain part of it. Not yet means the idea is not there yet, often with a common misconception. The tracker gives what secure looks like in each key stage, for each strand.</p>
<h2>Seeing progress across the years</h2>
<p>Keep one tracker file per class from Year 1 to Year 6. Each September, duplicate the tracker tab and choose the new year group, so earlier years stay visible. A subject leader needs only the class summary and three pupils' IDEAL Challenge work once per unit.</p>
<div class="file card">
{icon("chart", "e", 30)}<h2>The IDEAL Thinkers Assessment Tracker</h2>
<p>The tracker records secure, developing or not yet against each of the five progression strands.</p>
<p class="file-btns"><a class="btn" href="{t}/copy">Make a copy</a><a class="btn btn-ghost" href="{t}/export?format=xlsx">Download Excel</a><a class="btn btn-ghost" href="{t}/preview">Preview</a></p>
</div>
</section>"""
    page("assessment/", "Assessment | IDEAL Thinkers",
         "How pupils are assessed in IDEAL Thinkers: I can statements, exit tickets, IDEAL Challenges and the assessment tracker.", body, d)


def build_using():
    d = 1
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow">Using the lessons</p>
<h1>Using the lessons</h1>
<p class="lede">Each lesson has one lesson plan and one slide deck. Everything a teacher needs is inside those two files.</p>
</div></section>
<section class="wrap">
<div class="grid grid-3 how-cards">
<div class="card how-card"><span class="ic ic-i" aria-hidden="true"><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg></span><h2>Make a copy</h2><p>On any lesson page, choose Make a copy and the file is copied into your own Google Drive. Your copy is yours to edit.</p></div>
<div class="card how-card"><span class="ic ic-a" aria-hidden="true"><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="M7 10l5 5 5-5"/><path d="M5 21h14"/></svg></span><h2>Download</h2><p>On Microsoft 365? Download the slides as PowerPoint and the plan as Word instead.</p></div>
<div class="card how-card"><span class="ic ic-e" aria-hidden="true"><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/><path d="M8 13h8"/><path d="M8 17h5"/></svg></span><h2>Inside the files</h2><p>Teacher notes and answers are in the lesson plan, under Teacher notes by slide, and printable resources are at the end of each deck.</p></div>
</div>
<p>If Make a copy is greyed out or a file will not open, your school may block files from outside its organisation. Download the files instead, or ask your IT team to allow access.</p>
<p><a class="btn btn-ghost" href="{GUIDE_URL}">The Curriculum Guide (a one document overview)</a></p>
<h2>Starting out</h2>
<ol class="list">
<li><strong>Where it fits.</strong> Teach each year's six lessons in order, as one half term of computing. Lessons with RSHE links, such as Year 4 Lesson 2, can be taught in RSHE time, but keep them in sequence.</li>
<li><strong>Starting above Year 1.</strong> In the first year, pupils in Years 2 to 6 have not met the earlier units. Before Lesson 1, introduce Bleep, the IDEAL habits and the IDEAL moment routine (using your key stage's wording) and the AI Loop, then the ideas that year's unit builds on. How much that takes depends on the year group: each year page lists the slides to use and roughly how long to allow, under "Starting Year N with pupils new to IDEAL Thinkers" (<a href="../year-2/#starting">Year 2</a>, <a href="../year-3/#starting">Year 3</a>, <a href="../year-4/#starting">Year 4</a>, <a href="../year-5/#starting">Year 5</a>, <a href="../year-6/#starting">Year 6</a>). Treat words marked "Already taught" as new. A short introduction gives pupils the words and routines, not the years of practice behind them, so expect to revisit these ideas.</li>
<li><strong>What to assume.</strong> Assume no AI knowledge beyond the earlier units. Children's experience at home varies widely; no lesson depends on it, and you never need to ask which apps they use.</li>
<li><strong>Preparation.</strong> Read the six plans at the start of the half term. First time through, allow up to twice the stated preparation time for printing and cutting, and keep each lesson's cards in an envelope for next year. Year 5 Lesson 6 needs clean recycling collected in advance, and Year 6 Lesson 6 needs a small panel invited.</li>
<li><strong>Subject knowledge.</strong> Each plan's Teacher subject knowledge section is all you need; read it the day before. Practise two things beforehand: building the Scratch program (Year 5 Lesson 1) and running Teachable Machine (Year 5 Lesson 6).</li>
<li><strong>New to AI tools?</strong> 32 of the 36 lessons use no AI tool at all. The four demonstration lessons give the exact steps and words to type, and each can be taught with no tool.</li>
<li><strong>Devices and school policy.</strong> Every lesson needs only a screen for the slides. If your school has not approved a suitable tool, use the prepared results or the unplugged version. Never use a personal account.</li>
<li><strong>Misconceptions.</strong> Each plan lists the likely ones. If an exit ticket shows one is common, reteach it briefly at the start of the next lesson and add a Remember When question on it.</li>
<li><strong>If a lesson runs long.</strong> Stop at a natural break, do the exit ticket, and finish the rest at the start of the next lesson in place of Link It. For 45 minute lessons, use the 45 minute version in the plan.</li>
<li><strong>Checking it works.</strong> A subject leader needs only what the lessons already produce. Once per unit, look at each class tracker's summary and three pupils' IDEAL Challenge work (one secure, one developing, one not yet), and ask the teacher two questions: which lesson ran over, and which misconception came up most.</li>
</ol>
<h2>Display and posters</h2>
<div class="grid grid-3 posters-grid">
<div class="card poster-card"><a class="pc-img pc-wide" href="https://drive.google.com/uc?export=download&amp;id={ROADMAP_PDF}"><img src="{rel(d, 'images/ideal-thinkers-road-map.webp')}" width="2482" height="1754" loading="lazy" alt="Thumbnail of the A3 IDEAL Thinkers road map"></a><h3>The road map (A3)</h3><p>All 36 lessons on one poster.</p><p><a class="btn" href="https://drive.google.com/uc?export=download&amp;id={ROADMAP_PDF}">Download (PDF)</a></p></div>
""" + "".join(f'''<div class="card poster-card"><a class="pc-img" href="{rel(d, 'downloads/' + f)}" download><img src="{rel(d, 'images/posters/' + k + '.png')}" width="397" height="562" loading="lazy" alt="Thumbnail of the A4 poster: {e(t)}"></a><h3>{e(t)} (A4)</h3><p><a class="btn" href="{rel(d, 'downloads/' + f)}" download>Download (PDF)</a></p></div>''' for k, (t, f) in POSTERS.items()) + f"""
</div>
</section>"""
    page("using-the-lessons/", "Using the lessons | IDEAL Thinkers",
         "How to copy, download and teach the IDEAL Thinkers lesson plans and slides.", body, d)


def build_licence():
    d = 1
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow">Licence</p>
<h1>Licence and credit</h1>
</div></section>
<section class="wrap">
{LICENCE_PANEL.format(href='https://creativecommons.org/licenses/by-nc-sa/4.0/')}
<p>IDEAL Thinkers &copy; 2026 Mark Anderson is licensed under Creative Commons Attribution NonCommercial ShareAlike 4.0 International (CC BY-NC-SA 4.0). You may copy, adapt and share these resources for non commercial purposes, provided you credit "IDEAL Thinkers by Mark Anderson, ictevangelist.com" and share any adapted versions under the same licence.</p>
<p>Licence details: <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">creativecommons.org/licenses/by-nc-sa/4.0</a></p>
</section>"""
    page("licence/", "Licence and credit | IDEAL Thinkers",
         "IDEAL Thinkers is free to use under CC BY-NC-SA 4.0 and cannot be taken, distributed or shared for commercial purposes.", body, d)


def build_privacy():
    d = 1
    if GA_ID:
        short = """<p>I collect as little as possible. There are no accounts and no forms, and you don't need to sign up for anything to use IDEAL Thinkers; neither do your pupils. Analytics only runs if you say yes to it.</p>
<h2>Analytics</h2>
<p>I use Google Analytics to see how the site is used, which pages get read and where visitors come from, so I can make it better. It only runs if you choose Accept in the cookie banner. Google Analytics doesn't store IP addresses, and the data isn't used for advertising. If you accept, it sets two cookies, _ga and one starting _ga_, which last up to two years. Your choice is saved in your browser, and you can change your mind at any time with Cookie settings at the bottom of every page. Analytics data is kept for up to 14 months.</p>"""
    else:
        short = """<p>This site doesn't collect any personal information. There are no accounts, no forms, no analytics and no cookies set by the site itself. You don't need to sign up for anything to use IDEAL Thinkers, and neither do your pupils.</p>"""
    body = """<section class="page-head"><div class="wrap">
<p class="eyebrow">Privacy</p>
<h1>Privacy notice</h1>
<p class="lede">Last updated 18 October 2026.</p>
</div></section>
<section class="wrap">
<p>This site is run by me, Mark Anderson, trading as ICT Evangelist, in the United Kingdom. If you have any questions about your data, email me at <a href="mailto:mark@ictevangelist.com">mark@ictevangelist.com</a>.</p>
<h2>The short version</h2>
{PRIVACY_SHORT}
<h2>What other services see</h2>
<p>A few things on the site come from other services. Like any website, they see basic details such as your IP address when your browser asks them for something.</p>
<ul>
<li><strong>GitHub Pages</strong> hosts the site. GitHub logs visitors' IP addresses for security. See <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub's privacy statement</a>.</li>
<li><strong>Google Fonts</strong> supplies the fonts.</li>
<li><strong>Google Slides</strong> shows the slides on each lesson page. Google may set cookies when they load, particularly if you're signed in to a Google account.</li>
<li><strong>Make a copy, Preview, Download and the Drive folder buttons</strong> take you to Google. If you make a copy, it sits in your own or your school's Google account.</li>
</ul>
<p>What Google does with this is covered by <a href="https://policies.google.com/privacy">Google's privacy policy</a>.</p>
<h2>Your rights</h2>
<p>For your rights under UK data protection law, including how to complain to the Information Commissioner's Office, see my main <a href="https://ictevangelist.com/privacy-policy/">privacy policy</a>.</p>
</section>""".replace("{PRIVACY_SHORT}", short)
    page("privacy/", "Privacy notice | IDEAL Thinkers",
         "How IDEAL Thinkers handles data: no accounts or forms, and analytics only with your consent." if GA_ID else
         "IDEAL Thinkers collects no personal information: no accounts, forms, analytics or cookies of its own.", body, d)


def build_404():
    body = f"""<section class="page-head"><div class="wrap head-grid"><div><h1>Page not found</h1>
<p class="lede">Chatty can't find that page. Try the <a href="/curriculum-map/">curriculum map</a> or the <a href="/">home page</a>.</p></div>{chatty("chatty chatty-head")}</div></section>"""
    if PREVIEW:
        return
    doc = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    start, end = doc.index("<main id=\"main\">") + len("<main id=\"main\">"), doc.index("</main>")
    doc = doc[:start] + "\n" + body + "\n" + doc[end:]
    doc = doc.replace('href="css/', 'href="/css/').replace('href="favicon', 'href="/favicon')
    open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(doc)


def build_meta():
    if PREVIEW:
        return
    if LAUNCHED:
        open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
        urls = "".join(f"<url><loc>{SITE}/{p}</loc><lastmod>{BUILT}</lastmod></url>" for p in PAGES)
        open(os.path.join(ROOT, "sitemap.xml"), "w").write(
            f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    else:
        open(os.path.join(ROOT, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")
    build_llms()


def build_llms():
    """llms.txt: a plain summary and page list for AI assistants and answer engines."""
    t = ["# IDEAL Thinkers", "",
         "> A free AI literacy and fluency curriculum for primary schools in England, Year 1 to Year 6, by Mark Anderson FCCT (ictevangelist.com). "
         "36 lessons, six per year group, each with a lesson plan and slides. Unplugged first: every lesson can be taught without pupil devices, and pupils never need AI accounts. "
         "Licensed CC BY-NC-SA 4.0: free for schools and teachers, not for commercial use. Credit: \"IDEAL Thinkers by Mark Anderson, ictevangelist.com\".", "",
         "IDEAL Thinkers is the AI Literacy strand of the Primary Digital Cognition Curriculum from The EdTech Playbook. "
         "Pupils' learning builds in five progression strands (how AI works; staying in charge; safe, fair and honest; learning well; design and create). The IDEAL habits (Informed, Deliberate, Ethical, Accurate, Learning) are how pupils use AI well, with Learning Well (Try it first; Hint, not answer; Plan, use, prove) as the taught form of the L habit. The AI Loop (Learn, Spot, Guess, Check) is a simple model of how AI that learns from examples works.", "",
         "## How it works",
         f"- [How it works]({SITE}/how-it-works/)", f"- [The AI Loop]({SITE}/how-it-works/ai-loop/)", f"- [IDEAL]({SITE}/how-it-works/ideal/)",
         f"- [Learning Well]({SITE}/how-it-works/learning-well/)", f"- [Every lesson]({SITE}/how-it-works/every-lesson/)",
         f"- [Curriculum map]({SITE}/curriculum-map/)", f"- [Safety and safeguarding]({SITE}/safety/)", f"- [Progression]({SITE}/progression/)",
         f"- [Assessment]({SITE}/assessment/)", f"- [Using the lessons]({SITE}/using-the-lessons/)", f"- [Licence]({SITE}/licence/)", ""]
    for y in DATA["years"]:
        t.append(f"## Year {y['n']}: {y['title']} (ages {AGES[y['n']]})")
        t.append(f"Big question: {y['big_question']} [Unit overview]({SITE}/{y['path']})")
        t += [f"- [Lesson {l['n']}: {l['title']}]({SITE}/{l['path']}): {l['big_idea']}" for l in y["lessons"]]
        t.append("")
    open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write("\n".join(t))


if __name__ == "__main__":
    build_home()
    build_how()
    build_map()
    build_years()
    build_year_groups()
    build_lessons()
    build_progression()
    build_safety()
    build_assessment()
    build_using()
    build_licence()
    build_privacy()
    build_404()
    build_meta()
    print(len(PAGES), "pages")
