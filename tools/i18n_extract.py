import ast
import collections
import json
import os
import pathlib

UI_FUNCS = {
    "setText", "setTitle", "addItem", "setPlaceholderText", "setToolTip",
    "setWindowTitle", "setStatusTip", "addTab", "setTabText", "setPrefix",
    "setSuffix", "setWhatsThis", "setAccessibleName",
}
UI_CTORS = {
    "QLabel", "QPushButton", "QGroupBox", "QCheckBox", "QRadioButton",
    "QAction", "QMenu", "QToolButton", "QTabWidget", "QDialog", "QWidget",
    "QFrame", "Chart", "FrequencyChart",
}
SKIP = {"", "-", "--", "OK", "Cancel", "%", "dB", "Hz", "kHz", "MHz", "GHz"}

out = collections.OrderedDict()
per_file = collections.Counter()
root = pathlib.Path("src/NanoVNASaver")

for p in sorted(root.rglob("*.py")):
    if "ui" in p.parts:
        continue
    try:
        tree = ast.parse(p.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print("PARSE FAIL", p, exc)
        continue
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else (
            fn.id if isinstance(fn, ast.Name) else "")
        if name not in UI_FUNCS and name not in UI_CTORS:
            continue
        cand = []
        for a in node.args:
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                cand.append(a.value)
        for kw in node.keywords:
            if kw.arg in {"text", "title", "label", "placeholder", "comment"}:
                if isinstance(kw.value, ast.Constant) and isinstance(
                        kw.value.value, str):
                    cand.append(kw.value.value)
        for s in cand:
            if not s.strip() or s in SKIP or len(s) < 2:
                continue
            rec = out.setdefault(s, {"files": [], "count": 0})
            if str(p) not in rec["files"]:
                rec["files"].append(str(p))
            rec["count"] += 1
            per_file[str(p)] += 1

dest = pathlib.Path(os.environ.get("TEMP", ".")) / "strings.json"
dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("unique:", len(out), "occurrences:", sum(per_file.values()))
print("out:", dest)
print("\nTop files:")
for f, c in per_file.most_common(12):
    print("%4d %s" % (c, f.replace("src/NanoVNASaver/", "")))
