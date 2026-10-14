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
    ("E", "Ethical", "Be fair and kind", "Be fair, honest and kind, and ask who might be left out", "Use it fairly and question whether it is fair"),
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
        return '<span class="badges" aria-label="IDEAL: all five habits">' + "".join(
            f'<span class="b b-{x}" aria-hidden="true">{x}</span>' for x in "IDEAL") + "</span>"
    ls = letters(ideal)
    names = {x[0]: x[1] for x in IDEAL}
    lab = ", ".join(names[x] for x in ls)
    return f'<span class="badges" aria-label="IDEAL: {lab}">' + "".join(
        f'<span class="b b-{x}" aria-hidden="true">{x}</span>' for x in ls) + "</span>"


def links_text(links):
    parts = []
    for p in [x.strip() for x in links.split(",")]:
        parts.append(f'<abbr title="{LINK_NAMES[p]}">{p}</abbr>' if p in LINK_NAMES else e(p))
    return ", ".join(parts)


def code_link(depth, code):
    code = code.replace(" ", "")
    l = LESSONS.get(code)
    if not l:
        return e(code)
    return f'<a href="{rel(depth, l["path"])}">Y{l["year"]["n"]} L{l["n"]}</a>'


def codes_html(depth, s):
    return re.sub(r"Y\d L\d", lambda m: code_link(depth, m.group(0)), e(s))


NAV = [("", "Home"), ("how-it-works/", "How it works"), ("year-groups/", "Year groups"), ("curriculum-map/", "Curriculum map"),
       ("safety/", "Safety"), ("using-the-lessons/", "Using the lessons")]


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
<p class="foot-links"><a href="{rel(depth, 'progression/')}">Progression and coverage</a> <a href="{rel(depth, 'assessment/')}">Assessment</a> <a href="{rel(depth, 'licence/')}">Licence</a> <a href="https://ictevangelist.com/">ictevangelist.com</a></p>
</div>
</footer>
</body>
</html>
"""
    if PREVIEW:
        doc = re.sub(r'href="((?:\.\./)*[^":#]*/)"', r'href="\1index.html"', doc).replace('href=""', 'href="index.html"')
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
           "ideal-habits": ("The habits grow with the children", "ideal-thinkers-ideal-habits-poster-a4.pdf"),
           "every-lesson": ("Every lesson", "ideal-thinkers-every-lesson-poster-a4.pdf")}


def poster_block(depth, key):
    t, f = POSTERS[key]
    return f"""<aside class="poster card">
<img src="{rel(depth, 'images/posters/' + key + '.png')}" width="397" height="562" loading="lazy" alt="A4 poster: {e(t)}">
<div><h2>Poster: {e(t)}</h2><p>An A4 poster for your classroom wall or display board.</p>
<p><a class="btn" href="{rel(depth, 'downloads/' + f)}" download>Download the A4 poster (PDF)</a></p></div>
</aside>"""


def loop_strip():
    steps = [("Learn", "It is given lots of examples (data), chosen by people."),
             ("Spot", "It finds patterns in those examples."),
             ("Guess", "It uses the patterns to make a prediction: a label, a next word, a video, a picture."),
             ("Check", "It cannot check itself against the real world. People must.")]
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
FAQ = [('What is IDEAL Thinkers?', "A free AI literacy and fluency curriculum for primary schools, from Year 1 to Year 6. There are 36 lessons, six for each year group, and every lesson has a lesson plan and a slide deck. It's the AI Literacy strand of the Primary Digital Cognition Curriculum from The EdTech Playbook."), ('Is it free?', "Yes, for schools and teachers. It's licensed under CC BY-NC-SA 4.0, so you can copy and adapt it for your own teaching as long as you credit it and share any adapted versions under the same licence. It cannot be used for commercial purposes."), ('Do pupils need devices or their own AI accounts?', "No. Every lesson can be taught without pupil devices, and pupils never need an AI account; most generative AI tools have a minimum age of 13. Where a demonstration helps, the teacher runs it on a school approved tool, and every deck includes prepared examples in case a live demonstration isn't possible on the day."), ('How long is each lesson?', "60 minutes, and every lesson plan includes a 45 minute version. Each year's six lessons are planned as a half-term unit, and the sixth lesson is an IDEAL Challenge that doubles as the end of unit assessment."), ('Does it cover the National Curriculum for computing?', 'It addresses the KS1 and KS2 statements on using technology safely, respectfully and responsibly, keeping personal information private, recognising uses of information technology beyond school, understanding how search results are selected and ranked, and being discerning in evaluating digital content. It will be mapped against the revised computing curriculum once the draft is published.'), ('Can I use it with Microsoft 365?', 'Yes. Every slide deck downloads as PowerPoint and every lesson plan as Word, and on Google Workspace you can make your own copy in Google Drive.')]


def build_home():
    d = 0
    years = "".join(year_card(d, y) for y in DATA["years"])
    body = f"""<section class="hero">
<div class="wrap hero-grid">
<div class="hero-text">
<p class="eyebrow">An AI literacy and fluency curriculum for primary schools, Year 1 to Year 6</p>
<h1>IDEAL Thinkers</h1>
<p class="lede">Children are growing up alongside AI. It chooses the next video they watch, finishes their sentences, listens from the kitchen worktop and answers questions in a voice that sounds friendly and sure of itself. Most of them meet it long before anyone teaches them what it is.</p>
<p class="lede">IDEAL Thinkers gives primary pupils the knowledge to understand how AI works, the habits to question what it tells them, the values to use it well, and the judgement to know when it helps their learning and when it gets in the way.</p>
<div class="hero-ctas">
<a class="btn" href="curriculum-map/">Find a lesson</a>
<a class="btn btn-ghost" href="how-it-works/">How it works</a>
<a class="btn btn-ghost" href="safety/">Is it safe?</a>
</div>
</div>
<div class="hero-art">{chatty("chatty chatty-hero", "Chatty, the class chatbot from the Year 4 lessons")}</div>
</div>
</section>
<section class="band">
<div class="wrap">
<h2>Six units, one for each year</h2>
<p>Six lessons per year, planned as a half-term unit. The sixth lesson in each year is an IDEAL Challenge, where pupils pull the unit together to make or decide something.</p>
<div class="grid grid-3">{years}</div>
</div>
</section>
<section class="wrap home-map">
<h2>The road map</h2>
<p>All 36 lessons on one page, from Year 1 to secondary school.</p>
<a class="home-map-img" href="curriculum-map/"><img src="images/ideal-thinkers-road-map.webp" width="2482" height="1754" loading="lazy" alt="The IDEAL Thinkers curriculum road map, showing all 36 lessons from Year 1 to Year 6"></a>
<p><a class="btn" href="curriculum-map/">Explore the curriculum map</a></p>
</section>
<section class="wrap">
<h2>Pedagogy first, technology second</h2>
<p>It is built on the principle behind all of my work: pedagogy first, technology second. Nearly every activity works without a single pupil device. Where technology appears, the teacher leads it, with a clear purpose and safeguarding built in.</p>
<p>Every lesson can be picked up and taught with minimal preparation, and every deck and plan can be copied, adapted and made your own.</p>
<h3>The AI Loop: Learn, Spot, Guess, Check</h3>
{loop_strip()}
<p class="more"><a href="how-it-works/">See the three threads that run through every lesson</a></p>
</section>
<section class="band">
<div class="wrap">
<h2>The frameworks it links to</h2>
<p>IDEAL Thinkers doesn't sit on its own. Here's what it connects to, and how.</p>
<div class="grid grid-2 frameworks">
<article class="card fw">
{icon("grid", "i")}<h3>The Primary Digital Cognition Curriculum</h3>
<p>The Primary Digital Cognition Curriculum, published in The EdTech Playbook, has four strands: Digital Citizenship, Digital Literacy, Computer Science and AI Literacy. IDEAL Thinkers is the full, teachable AI Literacy strand. AI does not stay in its own box, though, so every lesson also shows its links to the other three strands. Schools can see AI literacy as part of a whole approach to digital cognition rather than a bolt-on.</p>
</article>
<article class="card fw">
{icon("landmark", "d")}<h3>The National Curriculum for computing (England)</h3>
<p>The lessons address the KS1 and KS2 statements on using technology safely, respectfully and responsibly; keeping personal information private; recognising common uses of information technology beyond school (KS1); understanding how search results are selected and ranked, and being discerning in evaluating digital content (KS2).</p>
</article>
<article class="card fw">
{icon("layers", "e")}<h3>SEAME</h3>
<p>SEAME is a framework from the Raspberry Pi Computing Education Research Centre that sorts what we teach about AI into four levels: social and ethical, applications, models and engines (how AI actually works). Lessons cover all four levels of the model: social and ethical, applications, models and, through unplugged activities, engines.</p>
</article>
<article class="card fw">
{icon("calendar", "a")}<h3>The new computing curriculum</h3>
<p>BCS is drafting a revised National Curriculum for Computing for first teaching from September 2028, with foundational AI concepts included. This curriculum will be mapped against the draft once it is published.</p>
</article>
<article class="card fw">
{icon("people", "l")}<h3>Universal Design for Learning</h3>
<p>Every plan offers multiple ways to engage, to access content and to show understanding, with adaptations for support and stretch in each lesson.</p>
</article>
<article class="card fw">
{icon("brain", "i")}<h3>Cognitive science</h3>
<p>Spaced retrieval, concrete before abstract, worked examples and modelling, explicit vocabulary teaching, dual coding through consistent visual models, and frequent low stakes checks for understanding.</p>
</article>
<article class="card fw">
{icon("star", "d")}<h3>IDEAL</h3>
<p>My framework for informed learning with AI: Informed, Deliberate, Ethical, Accurate, Learning. Every lesson is tagged with the IDEAL letters it develops, and the wording grows with the children.</p>
<p><a href="how-it-works/ideal/">More on IDEAL</a></p>
</article>
<article class="card fw">
{icon("stairs", "e")}<h3>STAIR</h3>
<p>In Upper KS2, pupils plan how AI could support a specific learning goal using STAIR (Specific, Tell, Actionable, Iterate, Role), as part of the Learning Well habit: plan, use, prove.</p>
<p><a href="how-it-works/learning-well/">More on Learning Well</a></p>
</article>
</div>
<p>Wider curriculum: RSHE, science, maths, English, geography and careers links are flagged in each lesson plan.</p>
</div>
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
    phases = [("Remember When", "5 to 7 min", "Four quick retrieval questions from last lesson, earlier this year and a previous year. Spaced retrieval strengthens long term memory."),
              ("Link It", "5 min", "A hook that connects to what children already know from their own lives."),
              ("Learn It", "10 to 12 min", "Explicit teaching of one big idea and its vocabulary, with a worked example and a teacher think aloud. The AI Loop and IDEAL visuals are identical in every lesson (dual coding)."),
              ("Try It", "15 to 20 min", "The signature activity: collaborative, practical and memorable, usually unplugged."),
              ("Own It", "10 min", "Pupils apply the idea independently or in pairs, usually by creating something."),
              ("IDEAL Check", "3 min", "Which IDEAL letter did we practise, and what does it look like in real life?"),
              ("Exit Ticket", "3 to 5 min", "Three short questions to check understanding and shape the next lesson.")]
    ph = "".join(f'<li><span class="ph-n">{e(n)}</span><span class="ph-t">{e(t)}</span><span class="ph-d">{e(x)}</span></li>' for n, t, x in phases)
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow">How it works</p>
<h1>Three threads, one lesson shape</h1>
<p class="lede">IDEAL Thinkers is the full, teachable AI Literacy strand of the Primary Digital Cognition Curriculum. Three threads run through every lesson, and every lesson has the same shape.</p>
</div></section>
<section class="wrap">
<div class="grid grid-4">
<a class="card thread" href="ai-loop/">{icon("loop", "i", 30)}<h2>The AI Loop</h2><p>Learn, Spot, Guess, Check: how pupils understand what AI actually does.</p></a>
<a class="card thread" href="ideal/">{icon("star", "d", 30)}<h2>IDEAL</h2><p>How we use AI well: Informed, Deliberate, Ethical, Accurate, Learning.</p></a>
<a class="card thread" href="learning-well/">{icon("seedling", "e", 30)}<h2>Learning Well with AI</h2><p>Try it first, hint not answer, plan use prove.</p></a>
<a class="card thread" href="every-lesson/">{icon("clock", "a", 30)}<h2>Every lesson</h2><p>The same seven phases in every lesson, in 60 minutes.</p></a>
</div>
</section>
<section class="band"><div class="wrap">
<h2>Every lesson has the same shape</h2>
<p>A consistent structure lowers cognitive load for pupils and teachers alike: Remember When, Link It, Learn It, Try It, Own It, IDEAL Check and Exit Ticket, in 60 minutes.</p>
<p><a class="btn" href="every-lesson/">See every lesson's shape</a></p>
</div></section>
"""
    page("how-it-works/", "How IDEAL Thinkers works: the AI Loop, IDEAL and Learning Well",
         "The three threads that run through every IDEAL Thinkers lesson, and the seven phase lesson shape.", body, d)

    # Every lesson
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow"><a href="../">How it works</a> / Every lesson</p>
<h1>Every lesson has the same shape</h1>
<p class="lede">A consistent structure lowers cognitive load for pupils and teachers alike. Lessons are designed for 60 minutes and flex to 45 by trimming the Try It phase.</p>
</div></section>
<section class="wrap">
<ol class="phases">{ph}</ol>
<p>Individual lessons adjust these phase timings to suit their activities, and some add a short real-life story, but every plan still totals 60 minutes.</p>
<p class="pill-line"><span class="tag">Retrieve, never re-teach</span><span class="tag">Slides build on click</span><span class="tag">Unplugged first</span><span class="tag">No pupil accounts</span></p>
<p>Lesson 6 each year is the IDEAL Challenge and the end of unit assessment.</p>
<h2>IDEAL moments</h2>
<p>In each lesson, the day's IDEAL habit appears as a cue only on the click where pupils actually practise it. When the cue appears, the teacher points to it, the class says the habit together, and the teacher asks the action question given in the speaker notes. <a href="../ideal/">More on IDEAL</a></p>
<h2>How it's built</h2>
<div class="grid grid-3">
<div class="card">{icon("brain", "i")}<h3>Grounded in cognitive science</h3><p>Spaced retrieval, concrete before abstract, worked examples and modelling, explicit vocabulary teaching, dual coding through consistent visual models, and frequent low stakes checks for understanding.</p></div>
<div class="card">{icon("people", "l")}<h3>Designed with UDL</h3><p>Every plan offers multiple ways to engage, to access content and to show understanding.</p></div>
<div class="card">{icon("slides", "d")}<h3>Slides built for low cognitive load</h3><p>Every slide builds on click in the order the teacher teaches it, as if writing on a whiteboard, so pupils meet one element at a time. Visuals carry meaning rather than decoration: each AI Loop step, each IDEAL habit and each recurring idea has its own icon, used identically in every lesson.</p></div>
</div>
<p>Teacher-facing labels and sources sit in the speaker notes, not on the screen. New ideas and vocabulary are taught where pupils first need them; earlier learning is retrieved, not re-taught.</p>
{poster_block(2, "every-lesson")}
</section>"""
    page("how-it-works/every-lesson/", "Every lesson: the seven phase lesson shape | IDEAL Thinkers",
         "Every IDEAL Thinkers lesson follows the same seven phases: Remember When, Link It, Learn It, Try It, Own It, IDEAL Check and Exit Ticket.", body, 2)

    # AI Loop
    rows = [("Learn", "It is given lots of examples (data), chosen by people.", "Year 1: it learns from lots of examples. Year 5: training data, test data, permission and fairness."),
            ("Spot", "It finds patterns in those examples.", "Year 1: spotting a secret sorting rule. Year 4: patterns in words. Year 5: rules versus learning."),
            ("Guess", "It uses the patterns to make a prediction: a label, a next word, a video, a picture.", "Year 1: it makes a guess. Year 4: next word prediction and how sure it is. Year 6: generated images, text and voices."),
            ("Check", "It cannot check itself against the real world. People must.", "Every year: Check is always the human's job, and that is where IDEAL comes in.")]
    tr = "".join(f'<tr><th scope="row">{s}</th><td>{e(a)}</td><td>{e(b)}</td></tr>' for s, a, b in rows)
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow"><a href="../">How it works</a> / Thread 1</p>
<h1>The AI Loop: Learn, Spot, Guess, Check</h1>
<p class="lede">How pupils understand what AI actually does. Every year group returns to it, so knowledge builds into a secure schema rather than a collection of separate facts.</p>
</div></section>
<section class="wrap">
{loop_strip()}
<div class="table-wrap"><table><thead><tr><th scope="col">Step</th><th scope="col">What the AI does</th><th scope="col">How the idea grows</th></tr></thead><tbody>{tr}</tbody></table></div>
<p>Pupils meet the AI Loop in <a href="../../year-1/the-mystery-rule/">Year 1, The Mystery Rule</a>.</p>
{poster_block(2, "ai-loop")}
</section>"""
    page("how-it-works/ai-loop/", "The AI Loop: Learn, Spot, Guess, Check | IDEAL Thinkers",
         "The AI Loop explains what AI does in four steps, and grows from Year 1 to Year 6.", body, 2)

    # IDEAL
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow"><a href="../">How it works</a> / Thread 2</p>
<h1>IDEAL: how we use AI well</h1>
<p class="lede">My framework for informed learning with AI. Every lesson is tagged with the IDEAL letters it develops, and the wording grows with the children.</p>
</div></section>
<section class="wrap">
<h2>The habits grow with the children</h2>
{ideal_table()}
<h2>IDEAL moments</h2>
<p>IDEAL is not a logo in the corner of every slide. In each lesson, the day's IDEAL habit appears as a cue only on the click where pupils actually practise it, for example "A: Check it before you trust it" just as pupils go looking for evidence. When the cue appears, the teacher points to it, the class says the habit together, and the teacher asks the action question given in the speaker notes. Every lesson plan lists its IDEAL moments, with slide numbers and what to say. The routine is taught to pupils in <a href="../../year-1/does-it-guess/">Year 1 Lesson 1</a> and used in every lesson after that, so pupils learn to link each habit to the moment they use it.</p>
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
<p class="eyebrow"><a href="../">How it works</a> / Thread 3</p>
<h1>Learning Well with AI</h1>
<p class="lede">"Knowing how to use technology to support learning" is the most important outcome in any digital curriculum, and usually the vaguest. Here it has its own progression, grounded in cognitive science: if the machine does the thinking, the child does not learn.</p>
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
    targets.update({"The AI Loop": ("how-it-works/ai-loop/", "The AI Loop"),
                    "The habits grow with the children": ("how-it-works/ideal/", "The IDEAL habits grow with the children"),
                    "Every lesson": ("how-it-works/every-lesson/", "Every lesson"),
                    "IDEAL": ("how-it-works/ideal/", "IDEAL: how we use AI well")})
    spots += "".join(
        f'<a class="spot" href="{rel(d, targets[k][0])}" style="left:{x}%;top:{y}%;width:{w}%;height:{h}%">'
        f'<span class="vh">{e(targets[k][1])}</span></a>'
        for k, (x, y, w, h) in EXTRA_SPOTS.items())
    roadmap = f"""<section class="wrap roadmap-sec">
<h2>The road map</h2>
<p>Click any lesson on the road map to open it, or download the A3 poster for your classroom wall.</p>
<figure class="roadmap">
<div class="roadmap-frame">
<img src="../images/ideal-thinkers-road-map.webp" width="2482" height="1754" alt="The IDEAL Thinkers curriculum road map: a road winding through all 36 lessons from Year 1 to Year 6, ending at secondary school, with the IDEAL habits, the AI Loop and the lesson shape along the bottom.">
{spots}
</div>
<figcaption><a class="btn" href="https://drive.google.com/uc?export=download&amp;id={ROADMAP_PDF}">Download the A3 road map (PDF)</a></figcaption>
</figure>
</section>"""
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow">Curriculum map</p>
<h1>All 36 lessons at a glance</h1>
<p class="lede">Six lessons per year, planned as a half-term unit. Cross-strand links: <abbr title="Digital Citizenship">DC</abbr> Digital Citizenship, <abbr title="Digital Literacy">DL</abbr> Digital Literacy, <abbr title="Computer Science">CS</abbr> Computer Science.</p>
</div></section>
{roadmap}
<div class="wrap map"><h2 class="map-h">Every lesson</h2>{filters}
<p class="f-count" aria-live="polite"></p>
{secs}</div>
<script src="../js/map.js" defer></script>"""
    page("curriculum-map/", "Curriculum map: all 36 lessons | IDEAL Thinkers",
         "Every IDEAL Thinkers lesson from Year 1 to Year 6, with its big idea, IDEAL letters and links to the other strands.", body, d)


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
            where.append(f'Next, in Year {next_y["n"]}, they move on to <a href="{rel(d, next_y["path"])}">{e(next_y["title"])}</a>.')
        cards = "".join(lesson_card(d, l) for l in y["lessons"])
        bot = chatty("chatty chatty-head", "Chatty, the class chatbot pupils meet in Year 4") if y["n"] == 4 else ""
        body = f"""<section class="page-head year-head"><div class="wrap{' head-grid' if bot else ''}"><div>
<p class="eyebrow"><a href="../curriculum-map/">Curriculum map</a> / Year {y['n']}</p>
<div class="yh">{year_icon(y["n"], 44)}<h1>Year {y['n']}: {e(y['title'])}</h1></div>
<p class="bq big">Big question: {e(y['big_question'])}</p>
<p>{' '.join(where)}</p>
<p><a class="btn btn-ghost" href="https://drive.google.com/drive/folders/{y['folder']}">Open the Year {y['n']} folder in Google Drive</a></p>
</div>{bot}</div></section>
<section class="wrap"><div class="grid grid-3">{cards}</div>
<p class="note">Lesson 6 is the IDEAL Challenge, where pupils pull the unit together to make or decide something. It doubles as the end of unit assessment task.</p>
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
<p class="file-btns"><a class="btn" href="{base}/copy">Make a copy</a><a class="btn btn-ghost" href="{dl}">{dl_label}</a><a class="btn btn-ghost" href="{base}/preview">Preview</a></p>
</div>"""


def build_lessons():
    for y in DATA["years"]:
        ls = y["lessons"]
        for i, l in enumerate(ls):
            d = 2
            prev_l = ls[i - 1] if i > 0 else None
            next_l = ls[i + 1] if i < len(ls) - 1 else None
            flags = ""
            if l["flag"] == "safeguarding":
                flags += f'<p class="flag flag-safe"><strong>Safeguarding.</strong> This lesson deals with privacy, chatbot relationships or images of real people. The plan flags this, and any disclosure should be handled through your school\'s safeguarding procedures. <a href="{rel(d, "safety/")}">More on safety</a></p>'
            if l["flag"] == "demo":
                flags += f'<p class="flag flag-demo"><strong>Teacher demonstration.</strong> Where a demonstration helps, the teacher runs it on a school approved tool, previews it first and stays in control. The deck also includes prepared examples, so the lesson does not depend on a live demonstration working on the day. No pupil accounts. <a href="{rel(d, "safety/")}">More on safety</a></p>'
            ch = '<span class="tag tag-challenge">IDEAL Challenge</span>' if l["challenge"] else ""
            sess = f' <span class="tag">{e(l["sessions"])}</span>' if l["sessions"] else ""
            ican = "".join(f"<li>{e(s)}</li>" for s in l["i_can"])
            nav = '<nav class="pn" aria-label="Lessons">'
            nav += f'<a class="pn-prev" href="{rel(d, prev_l["path"])}"><span>Previous</span>Lesson {prev_l["n"]}: {e(prev_l["title"])}</a>' if prev_l else '<span></span>'
            nav += f'<a class="pn-next" href="{rel(d, next_l["path"])}"><span>Next</span>Lesson {next_l["n"]}: {e(next_l["title"])}</a>' if next_l else f'<a class="pn-next" href="{rel(d, y["path"])}"><span>Back to</span>Year {y["n"]}: {e(y["title"])}</a>'
            nav += "</nav>"
            time = "Two sessions" if l["sessions"] else "60 minutes, with a 45 minute version in the plan"
            body = f"""<section class="page-head lesson-head"><div class="wrap">
<p class="eyebrow"><a href="{rel(d, 'curriculum-map/')}">Curriculum map</a> / <a href="{rel(d, y['path'])}">Year {y['n']}: {e(y['title'])}</a></p>
<p class="kicker">Year {y['n']}, Lesson {l['n']} {ch}{sess}</p>
<div class="yh">{year_icon(y['n'], 44)}<h1>{e(l['title'])}</h1></div>
<p class="lede">{e(l['big_idea'])}</p>
<p class="card-meta">{badges(l['ideal'])}<span class="links">Links: {links_text(l['links'])}</span></p>
</div></section>
<section class="wrap lesson-body">
<div class="lesson-main">
{flags}
<h2>The signature activity</h2>
<p>{e(l['activity'])}</p>
<h2>Learning intentions</h2>
<ul class="ican">{ican}</ul>
<h2>The slides</h2>
<div class="embed"><iframe src="https://docs.google.com/presentation/d/{l['slides']}/embed?start=false&amp;loop=false" title="Slides: {e(l['title'])}" loading="lazy" allowfullscreen></iframe></div>
<p class="note">Teacher notes and answers sit in the speaker notes of every slide, and printable resources are at the end of the deck.</p>
</div>
<aside class="lesson-side">
<div class="card side-card">
<p class="side-row"><span>Time</span>{time}</p>
<p class="side-row"><span>Devices</span>Unplugged first: no pupil devices needed</p>
</div>
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
            ("Staying in charge", "People make AI and are in charge; we check its guesses.", "Chatbots are not friends; sounding sure is not being right.", "People must explain and answer for AI decisions; different people are affected differently."),
            ("Safe, fair and honest", "Some things we never tell a machine; missing examples cause mistakes.", "Privacy and listening devices; honesty about AI help; designing for children's wellbeing.", "Permission, consent for images of real people, bias, environmental cost."),
            ("Learning Well", "Try it first.", "Hint, not answer.", "Plan, use, prove."),
            ("Design and create", "Robot Rules; directing an AI picture.", "A healthier feed; a chatbot rulebook.", "Training a class model; designing AI for good.")]
    pt = "".join(f'<tr><th scope="row">{e(a)}</th><td>{e(b)}</td><td>{e(c)}</td><td>{e(x)}</td></tr>' for a, b, c, x in prog)
    cov = [("KS1", None), ("Understanding what AI is", "Y1 L1, Y1 L2, Y1 L3"), ("Identifying common AI applications", "Y1 L4, Y2 L5"),
           ("Basic understanding of ethical behaviour with AI tools", "Y1 L6, Y2 L4, Y2 L6"), ("Simple AI games and activities", "Every KS1 lesson"),
           ("Creating AI images using simple tools", "Y1 L5"), ("KS2", None),
           ("Basic concepts of machine learning and algorithms", "Y4 L1, Y4 L5, Y5 L1, Y5 L2, Y5 L6"),
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
    for a, b in cov:
        ct += f'<tr class="grp"><th colspan="2" scope="colgroup">{e(a)}</th></tr>' if b is None else f'<tr><th scope="row">{e(a)}</th><td>{codes_html(d, b)}</td></tr>'
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow">Progression and coverage</p>
<h1>How the learning builds</h1>
<p class="lede">Five threads of progression across KS1, Lower KS2 and Upper KS2, and where each AI Literacy outcome is taught.</p>
</div></section>
<section class="wrap">
<h2>Progression by thread</h2>
<div class="table-wrap"><table><thead><tr><th scope="col">Thread</th><th scope="col">KS1</th><th scope="col">Lower KS2</th><th scope="col">Upper KS2</th></tr></thead><tbody>{pt}</tbody></table></div>
<h2>Coverage of the AI Literacy outcomes</h2>
<div class="table-wrap"><table><thead><tr><th scope="col">Primary Digital Cognition Curriculum outcome</th><th scope="col">Where it is taught</th></tr></thead><tbody>{ct}</tbody></table></div>
<h2>Alignment</h2>
<p><strong>National Curriculum for computing (England):</strong> using technology safely, respectfully and responsibly; keeping personal information private; recognising common uses of information technology beyond school (KS1); understanding how search results are selected and ranked, and being discerning in evaluating digital content (KS2).</p>
<p><strong>SEAME:</strong> lessons cover all four levels of the model: social and ethical, applications, models and, through unplugged activities, engines.</p>
<p><strong>The new computing curriculum:</strong> BCS is drafting a revised National Curriculum for Computing for first teaching from September 2028, with foundational AI concepts included. This curriculum will be mapped against the draft once it is published.</p>
<p><strong>Wider curriculum:</strong> RSHE, science, maths, English, geography and careers links are flagged in each lesson plan.</p>
</section>"""
    page("progression/", "Progression and coverage | IDEAL Thinkers",
         "How IDEAL Thinkers builds from KS1 to Upper KS2, and where each AI Literacy outcome is taught.", body, d)


def build_safety():
    d = 1
    sg = [LESSONS[c] for c in ("Y2L4", "Y3L2", "Y4L2", "Y6L1")]
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
<div class="card">{icon("nouser", "i")}<h2>No pupil accounts</h2><p>Most generative AI tools have a minimum age of 13. Where a demonstration helps, the teacher runs it on a school approved tool, previews it first and stays in control. Every deck also includes prepared examples, so no lesson depends on a live demonstration working on the day.</p></div>
<div class="card">{icon("clipboard", "a")}<h2>Check your school's position</h2><p>Follow your school's AI policy and data protection guidance before using any tool, and never enter pupils' personal information.</p></div>
<div class="card">{icon("heartshield", "l")}<h2>Safeguarding</h2><p>Four lessons deal with privacy, chatbot relationships and images of real people. Each plan flags this, and any disclosure should be handled through your school's safeguarding procedures.</p></div>
</div>
<div class="grid grid-2">
<div><h2>The safeguarding lessons</h2><ul class="list">{li(sg)}</ul></div>
<div><h2>The teacher demonstration lessons</h2><ul class="list">{li(dm)}</ul></div>
</div>
</section>"""
    page("safety/", "Technology, safety and safeguarding | IDEAL Thinkers",
         "IDEAL Thinkers is unplugged first, with no pupil accounts and teacher-led demonstrations only.", body, d)


def build_assessment():
    d = 1
    t = f"https://docs.google.com/spreadsheets/d/{TRACKER}"
    body = f"""<section class="page-head"><div class="wrap">
<p class="eyebrow">Assessment</p>
<h1>Assessment</h1>
<p class="lede">Each lesson has three "I can" statements and a three question exit ticket. Each IDEAL Challenge doubles as an end of unit assessment task, producing something pupils can explain to an adult.</p>
</div></section>
<section class="wrap">
<div class="file card">
{icon("chart", "e", 30)}<h2>The IDEAL Thinkers Assessment Tracker</h2>
<p>The tracker records secure, developing or not yet against each thread.</p>
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
<div class="card how-card"><span class="ic ic-e" aria-hidden="true"><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/><path d="M8 13h8"/><path d="M8 17h5"/></svg></span><h2>Inside the files</h2><p>Teacher notes and answers sit in the speaker notes of every slide, and printable resources are at the end of each deck.</p></div>
</div>
<h2>Display and posters</h2>
<div class="grid grid-4 posters-grid">
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
         "Three threads run through every lesson: the AI Loop (Learn, Spot, Guess, Check), the IDEAL habits (Informed, Deliberate, Ethical, Accurate, Learning) and Learning Well (Try it first; Hint, not answer; Plan, use, prove).", "",
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
    build_404()
    build_meta()
    print(len(PAGES), "pages")
