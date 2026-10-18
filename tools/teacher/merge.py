"""Build data/teacher.json (the single source for prior learning and preparation) from the audit and the plans' own text.

Usage: python3 tools/teacher/merge.py <audit dir with Y*-Y*.json> <extract.json>
"""
import json, glob, re, sys, os
aud, ext = sys.argv[1], json.load(open(sys.argv[2]))
need = json.load(open(os.path.join(aud, "need.json"))) if os.path.exists(os.path.join(aud, "need.json")) else {}
UNIT_ADVANCE = {"Y1L5", "Y3L3", "Y4L2", "Y5L1", "Y5L5", "Y5L6", "Y6L6"}  # shown on the year page too
lessons, years = {}, {}
for f in sorted(glob.glob(os.path.join(aud, "Y*-Y*.json"))):
    d = json.load(open(f)); lessons.update(d["lessons"]); years.update(d["years"])
def where_refs(s):
    """'Y1L3 deck slide 8; Y2L1 slides 7 to 8' -> [{'code':'Y1L3','slides':'slide 8'}, ...]"""
    out = []
    for m in re.finditer(r"(Y\dL\d)(?:\s+(?:deck|plan))?(?:\s+(slides?\s+\d+(?:\s*(?:,|and|to)\s*\d+)*))?", s):
        if not any(o["code"] == m.group(1) and o["slides"] == (m.group(2) or "") for o in out):
            out.append({"code": m.group(1), "slides": m.group(2) or ""})
    return out
def one(x): return " ".join(x) if isinstance(x, list) else (x or "")
out = {"lessons": {}, "years": {}}
for code, l in sorted(lessons.items()):
    e = ext[code]
    out["lessons"][code] = {
        "already": [{"idea": i["idea"], "from": where_refs(i["where"]) or [{"code": i["first_taught"], "slides": ""}], "scope": i["scope"]} for i in l["essential"]],
        "routines": [r["routine"] for r in l.get("routines", [])],
        "recall": sorted({c for q in l.get("remember_when", []) for c in re.findall(r"Y\dL\d", " ".join(str(v) for k, v in q.items() if k in ("source_stated", "verified_source", "source")))} - {code}),
        "if_not": one(l.get("bridge")), "adds": one(l.get("adds")),
        "prep_time": e["prep_time"], "prep": e["prep"], "safeguarding": e["safeguarding"],
        "need": need.get(code, {}).get("need", ""), "advance": need.get(code, {}).get("advance", ""), "unit_advance": code in UNIT_ADVANCE,
        "exit": e["exit"], "look_for": e["look_for"], "strands": e["strands"], "time": e["time"]}
for n, y in sorted(years.items()):
    ft = y.get("first_time")
    if isinstance(ft, dict): ft = list(ft.get("concepts", [])) + [ft.get("slides_before_lesson_1", ""), ft.get("note", "")]
    elif isinstance(ft, str): ft = [ft]
    y = dict(y, first_time=[x for x in ft if x])
    out["years"][n] = {k: y.get(k) for k in ("starting_point", "first_time", "journey", "end_point", "challenge", "extra_dependencies")}
# the four parts of "Before teaching this lesson", worked out once so the site and the plans say the same thing
cur = json.load(open("data/curriculum.json"))
info = {l["code"]: (y, l) for y in cur["years"] for l in y["lessons"]}
NAMES = (("IDEAL", "IDEAL moments"), ("AI Loop", "the AI Loop"), ("Bleep", "Bleep"), ("Chatty", "Chatty"), ("STAIR", "STAIR"),
         ("Try it first", "Learning Well"), ("Hint", "Learning Well"), ("Plan, use", "Learning Well"), ("Learning Well", "Learning Well"))
for code, T in out["lessons"].items():
    y, l = info[code]
    names = []
    for r in T["routines"]:
        for key, nm in NAMES:
            if key in r and nm not in names: names.append(nm)
    refs = []
    for a in T["already"]:
        for r in a["from"]:
            item = {"scope": "This unit" if r["code"][:2] == code[:2] else "Earlier year", "code": r["code"], "slides": r["slides"]}
            if item not in refs: refs.append(item)
    if l["challenge"] in (True, "True"):
        unit = [x["code"] for x in y["lessons"][:5]]
        extra = sorted({r["code"] for r in refs if r["code"][:2] != code[:2]})
        B = {"understand": ["Everything taught in Lessons 1 to 5 of this unit. This is the end of unit assessment: pupils use that learning on their own."],
             "where": [{"scope": "This unit", "code": c, "slides": ""} for c in unit], "also": extra,
             "if_not": "Teach Lessons 1 to 5 first. This lesson assesses them, so it is not a starting point for the unit.",
             "adds": "Pupils apply the whole unit independently, which gives the evidence for the tracker."}
    elif not T["already"]:
        B = {"understand": [], "where": [], "also": [], "if_not": "", "adds": T["adds"]}
    else:
        B = {"understand": [a["idea"] for a in T["already"]], "where": refs, "also": [], "if_not": T["if_not"], "adds": T["adds"]}
    B["routines"] = names
    B["recall"] = T["recall"]
    # readiness check: the Remember When question that retrieves each prerequisite, if there is one
    qs = []
    for i, q in enumerate(lessons[code].get("remember_when", []), 1):
        src = set(re.findall(r"Y\dL\d", " ".join(str(v) for k, v in q.items() if k in ("source_stated", "verified_source", "source"))))
        if src & {r["code"] for a in T["already"] for r in a["from"]}: qs.append(i)
    B["check"] = qs if (B["understand"] and not l["challenge"] in (True, "True")) else []
    T["before"] = B
json.dump(out, open("data/teacher.json", "w"), indent=1, ensure_ascii=False)
print(len(out["lessons"]), "lessons", len(out["years"]), "years")
