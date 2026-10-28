"""汉化审计：无头模式构建全部窗口，统计残留英文。

用法：
    QT_QPA_PLATFORM=offscreen python tools_i18n_audit.py [--no-install]
"""
from __future__ import annotations

import re
import sys

sys.path.insert(0, "src")

from PySide6 import QtWidgets  # noqa: E402

from NanoVNASaver import i18n  # noqa: E402

CJK = re.compile(r"[\u4e00-\u9fff]")
# 纯 ASCII 的可见文本才算"英文残留"；数字/单位/符号不算
EN = re.compile(r"^[ -~]+$")
# 纯数据（数字 + 单位），不该翻译
DATA = re.compile(r"^[-+]?[\d.,]+\s*(%|[A-Za-zΩ/]+)?$")
# 线缆型号/材质条目，形如 "... (0.66)"，保留原文
CABLE = re.compile(r".*\(\d\.\d+\)$")
# 串口条目，形如 "COM6 (H)"，是设备数据不是界面文案
PORT = re.compile(r"^(COM\d+|/dev/[\w/.-]+)( \(.+\))?$")
# 刻意保留英文的技术词
ALLOW = {
    "S11", "S21", "|S11|", "|S21|", "S11 R+jX", "S11 |Z|", "S21 R+jX",
    "TCP/IP", "NanoVNA", "Hanning", "Blackman", "TDR", "Hz", "dB",
}


def is_translatable(s: str) -> bool:
    if s in ALLOW:
        return False
    if DATA.match(s) or CABLE.match(s) or PORT.match(s):
        return False
    if s.startswith("NanoVNA Saver"):
        return False
    return len(s) >= 2


def texts_of(widget):
    """收集一个控件树里所有用户可见文本。"""
    out = []
    W = QtWidgets

    def add(s):
        if isinstance(s, str) and s.strip():
            out.append(s.strip())

    for w in [widget, *widget.findChildren(W.QWidget)]:
        try:
            add(w.windowTitle())
            add(w.toolTip())
        except Exception:  # noqa: BLE001
            pass
        for attr in ("text", "title", "placeholderText"):
            fn = getattr(w, attr, None)
            if callable(fn):
                try:
                    add(fn())
                except Exception:  # noqa: BLE001
                    pass
        if isinstance(w, W.QComboBox):
            # currentText() 被 i18n 还原成英文逻辑键，审计要看真正显示的文字
            for i in range(w.count()):
                add(w.itemText(i))
        if isinstance(w, W.QTabWidget):
            for i in range(w.count()):
                add(w.tabText(i))
        if isinstance(w, (W.QListWidget,)):
            for i in range(w.count()):
                add(w.item(i).text())
    return out


def main():
    if "--no-install" not in sys.argv:
        i18n.install()

    app = QtWidgets.QApplication(sys.argv)

    from NanoVNASaver.NanoVNASaver import NanoVNASaver

    main_win = NanoVNASaver()

    windows = {"主窗口": main_win}
    for mod, cls in [
        ("Windows.SweepSettings", "SweepSettingsWindow"),
        ("Windows.CalibrationSettings", "CalibrationWindow"),
        ("Windows.DisplaySettings", "DisplaySettingsWindow"),
        ("Windows.DeviceSettings", "DeviceSettingsWindow"),
        ("Windows.AnalysisWindow", "AnalysisWindow"),
        ("Windows.Bands", "BandsWindow"),
        ("Windows.Files", "FilesWindow"),
        ("Windows.MarkerSettings", "MarkerSettingsWindow"),
        ("Windows.TDR", "TDRWindow"),
        ("Windows.About", "AboutWindow"),
    ]:
        try:
            m = __import__(f"NanoVNASaver.{mod}", fromlist=[cls])
            windows[cls] = getattr(m, cls)(main_win)
        except Exception as exc:  # noqa: BLE001
            windows[cls] = None
            print(f"[skip] {cls}: {type(exc).__name__}: {exc}")

    total, zh, untranslated = 0, 0, {}
    for label, win in windows.items():
        if win is None:
            continue
        for s in set(texts_of(win)):
            if not EN.match(s):
                total += 1
                zh += 1
                continue
            if not is_translatable(s):
                continue
            total += 1
            untranslated.setdefault(s, []).append(label)

    print(f"\n可见文本条目: {total}   含中文: {zh}   纯 ASCII: {total - zh}")
    print(f"中文覆盖率: {zh / total * 100:.1f}%\n")
    lines = [f"--- 未翻译 {len(untranslated)} 条 ---"]
    for s, where in sorted(untranslated.items(), key=lambda kv: -len(kv[0])):
        lines.append(f"  {s!r}   <- {','.join(sorted(set(where)))}")
    report = "\n".join(lines)
    print(report)
    from pathlib import Path
    Path("untranslated.txt").write_text(report, encoding="utf-8")
    print("\n→ untranslated.txt")


if __name__ == "__main__":
    main()
