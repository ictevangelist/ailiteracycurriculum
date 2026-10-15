"""IDEAL Thinkers A3 landscape curriculum road map: data from guide.py, rendered to PDF with Chromium."""
import json, re, subprocess, sys, html, os
HERE = os.path.dirname(os.path.abspath(__file__))
SITE_REPO = os.environ.get("SITE_REPO", "/home/user/ailiteracycurriculum")
NODE = os.environ.get("ICON_NODE_MODULES", "/tmp/claude-0/-home-user-claude-wordpress/156a12ae-ce1f-506a-a4cc-b32b86bca15c/scratchpad/rm/node_modules")

# The 36 lessons come from the curriculum site's own data, so map and site never disagree.
_cur = json.load(open(os.path.join(SITE_REPO, "data/curriculum.json"), encoding="utf-8"))
STRANDS = json.load(open(os.path.join(HERE, "strands.json")))
YEARS = []
for _y in _cur["years"]:
    _ls = []
    for _l in _y["lessons"]:
        _tag = ("(IDEAL Challenge, two sessions) " if _l.get("sessions") else "(IDEAL Challenge) ") if _l["challenge"] else ""
        _ls.append((f"Y{_y['n']} L{_l['n']}", f"**{_l['title']}** {_tag}{_l['big_idea']}", _l["activity"], _l["ideal"], _l["links"]))
    YEARS.append((f"Year {_y['n']}: {_y['title']}", _y["big_question"], "", _ls))

COL = [  # main, dark (white text passes AA), tint
    ("16A085", "0E6655", "E8F8F5"), ("27AE60", "1E8449", "E9F7EF"), ("2980B9", "1F618D", "EBF5FB"),
    ("8E44AD", "6C3483", "F4ECF7"), ("D35400", "A04000", "FDF2E9"), ("C0392B", "922B21", "FDEDEC"),
]
IDEAL = [("I", "Informed", "2980B9", "1F618D", "FaInfoCircle"), ("D", "Deliberate", "8E44AD", "6C3483", "FaCompass"),
         ("E", "Ethical", "16A085", "117A65", "FaBalanceScale"), ("A", "Accurate", "D35400", "A04000", "FaSearch"),
         ("L", "Learning", "C0392B", "922B21", "FaSeedling")]
MOTTO = {
    "I": ["Know what it is", "Know what it is and how it works", "Know how it works and where it falls short"],
    "D": ["Use it on purpose", "Use it for a reason, not as a shortcut", "Use it for a goal, deliberately and sparingly"],
    "E": ["Be fair and kind", "Be fair, honest and kind", "Use it fairly and question whether it is fair"],
    "A": ["Check it", "Check it before you trust it", "Fact check, look for bias, find the evidence"],
    "L": ["Keep learning", "Make sure it helps you learn", "Keep your own thinking in charge"],
}
LOOP = [("Learn", "It learns from lots of examples that people choose or create.", "2980B9", "1F618D", "FaBookOpen"),
        ("Spot", "It finds patterns in those examples.", "8E44AD", "6C3483", "FaEye"),
        ("Guess", "It uses the patterns to predict: a label, a word, a video, a picture.", "D35400", "A04000", "FaLightbulb"),
        ("Check", "It can be wrong without knowing. People check its guesses before they trust them.", "16A085", "117A65", "FaUserCheck")]
LESSON_ICONS = [
    ["FaBoxOpen", "FaAppleAlt", "FaShapes", "FaTv", "FaPaintBrush", "FaCrown"],
    ["FaCheckCircle", "FaDove", "FaPuzzlePiece", "FaLock", "FaTrophy", "FaBus"],
    ["FaMobileAlt", "FaMicrophone", "FaUniversalAccess", "FaKey", "FaSignature", "FaHeart"],
    ["FaComments", "FaUserFriends", "FaSearch", "FaUtensils", "FaPercentage", "FaBook"],
    ["FaCode", "FaSortAmountDown", "FaCopyright", "FaBalanceScale", "GiStairs", "FaRecycle"],
    ["FaTheaterMasks", "FaUsers", "FaBriefcase", "FaLeaf", "FaGavel", "FaRocket"],
]
PHASES = [("Key Stage 1", "Years 1 and 2", "Try it first", "My brain grows when I do the hard thinking."),
          ("Lower Key Stage 2", "Years 3 and 4", "Hint, not answer", "The best help makes me think."),
          ("Upper Key Stage 2", "Years 5 and 6", "Plan, use, prove", "I plan how AI helps, then prove the learning is mine.")]
SHAPE = ["Remember When", "Link It", "Learn It", "Try It", "Own It", "IDEAL Check", "Exit Ticket"]

STRAND_ICON = {"How AI works": "FaCogs", "Staying in charge": "FaUserShield", "Safe, fair and honest": "FaShieldAlt", "Learning Well": "FaSeedling", "Design and create": "FaPencilRuler"}
names = sorted({i for row in LESSON_ICONS for i in row} | {x[4] for x in IDEAL} | {x[4] for x in LOOP} | set(STRAND_ICON.values()) | {"FaRoute", "FaStar", "FaChevronRight"})
ICON = json.loads(subprocess.check_output(["node", os.path.join(HERE, "icons.js"), *names], env={**os.environ, "NODE_PATH": NODE}))


def ic(name, cls="ic"):
    return '<span class="%s">%s</span>' % (cls, ICON[name])


def md(s):
    s = html.escape(s)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def chips(letters):
    if letters.strip() == "All":
        return '<span class="all">All habits</span>'
    out = []
    for k in [x.strip() for x in letters.split(",")]:
        it = next(x for x in IDEAL if x[0] == k)
        out.append('<span class="chip" style="background:#%s">%s</span>' % (it[3], k))
    return "".join(out)


