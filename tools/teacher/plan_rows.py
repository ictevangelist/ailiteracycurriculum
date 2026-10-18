"""Rows for the plans' "Before teaching this lesson" table, from data/teacher.json (same text as the website).

Usage: python3 tools/teacher/plan_rows.py > rows.json
"""
import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
T = json.load(open(os.path.join(ROOT, "data/teacher.json")))["lessons"]
cur = json.load(open(os.path.join(ROOT, "data/curriculum.json")))
L = {l["code"]: l for y in cur["years"] for l in y["lessons"]}
def name(c, title=True): return f"Year {c[1]} Lesson {c[3]}" + (f", {L[c]['title']}" if title else "")
def plain(s): return re.sub(r"Y(\d)L(\d)", lambda m: f"Year {m.group(1)} Lesson {m.group(2)}", s)
out = {}
for c, t in T.items():
    B = t["before"]
    if B["understand"]:
        und = " ".join(B["understand"])
        where = "; ".join(("This unit: " if x['scope'] == "This unit" else "") + f"{name(x['code'])}" + (f" ({x['slides']})" if x["slides"] else "") for x in B["where"]) + "."
        if B["also"]: where += " It also draws on " + ", ".join(name(x, False) for x in B["also"]) + "."
        ifnot = plain(B["if_not"])
    else:
        und, where, ifnot = "No formal prerequisites: this lesson starts from pupils' everyday experience.", "Nothing earlier is needed.", "Nothing to do: start the lesson as planned."
    if B["routines"]: und += " Routines it uses: " + ", ".join(B["routines"]) + "."
    if B["recall"]: where += " Remember When (slide 2) recalls " + ", ".join(name(x, False) for x in B["recall"]) + "; if your class has not had these, ask about pupils' own experience instead."
    out[c] = {"plan": L[c]["plan"], "rows": [["Pupils should already understand", und], ["Where this was taught", where.strip()],
                                            ["If your pupils haven't covered this", ifnot], ["What this lesson adds", B["adds"]]]}
print(json.dumps(out, indent=1, ensure_ascii=False))
