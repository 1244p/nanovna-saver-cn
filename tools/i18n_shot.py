"""无头渲染中文界面截图（验证用）。"""
import sys

sys.path.insert(0, "src")

from PySide6 import QtWidgets  # noqa: E402

from NanoVNASaver import i18n  # noqa: E402

i18n.install()
app = QtWidgets.QApplication(sys.argv)

from NanoVNASaver.NanoVNASaver import NanoVNASaver  # noqa: E402
from NanoVNASaver.Touchstone import Touchstone  # noqa: E402

win = NanoVNASaver()
win.resize(1500, 950)

t = Touchstone("tests/data/valid.s2p")
t.load()
win.saveData(t.s11, t.s21, "valid.s2p")
win.dataUpdated()
win.show()
app.processEvents()

win.grab().save("shot_main.png")
print("saved shot_main.png", win.size())

for name, mod, cls in [
    ("sweep", "Windows.SweepSettings", "SweepSettingsWindow"),
    ("display", "Windows.DisplaySettings", "DisplaySettingsWindow"),
    ("cal", "Windows.CalibrationSettings", "CalibrationWindow"),
    ("tdr", "Windows.TDR", "TDRWindow"),
]:
    try:
        m = __import__(f"NanoVNASaver.{mod}", fromlist=[cls])
        w = getattr(m, cls)(win)
        w.resize(700, 700)
        w.show()
        app.processEvents()
        w.grab().save(f"shot_{name}.png")
        print("saved", f"shot_{name}.png", w.windowTitle())
    except Exception as exc:  # noqa: BLE001
        print("skip", name, type(exc).__name__, exc)
