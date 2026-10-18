"""Build data/teacher.json (the single source for prior learning and preparation) from the audit and the plans' own text.

Usage: python3 tools/teacher/merge.py <audit dir with Y*-Y*.json> <extract.json>
"""
import json, glob, re, sys, os
aud, ext = sys.argv[1], json.load(open(sys.argv[2]))
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
        "exit": e["exit"], "look_for": e["look_for"], "strands": e["strands"], "time": e["time"]}
for n, y in sorted(years.items()):
    ft = y.get("first_time")
    if isinstance(ft, dict): ft = list(ft.get("concepts", [])) + [ft.get("slides_before_lesson_1", ""), ft.get("note", "")]
    elif isinstance(ft, str): ft = [ft]
    y = dict(y, first_time=[x for x in ft if x])
    out["years"][n] = {k: y.get(k) for k in ("starting_point", "first_time", "journey", "end_point", "challenge", "extra_dependencies")}
json.dump(out, open("data/teacher.json", "w"), indent=1, ensure_ascii=False)
print(len(out["lessons"]), "lessons", len(out["years"]), "years")
