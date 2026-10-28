"""用真实线缆测试数据跑一遍 TDR，看程序算出的长度。"""
import sys

sys.path.insert(0, "src")

from PySide6 import QtWidgets  # noqa: E402

from NanoVNASaver import i18n  # noqa: E402

i18n.install()
app = QtWidgets.QApplication(sys.argv)

# 桌面上已有一个实例占着 COM 口，这里跳过枚举，避免抢端口
# （SerialControl 是 from ... import get_interfaces，要改它自己的名字）
import NanoVNASaver.Controls.SerialControl as _sc  # noqa: E402

_sc.get_interfaces = lambda: []

from NanoVNASaver.NanoVNASaver import NanoVNASaver  # noqa: E402
from NanoVNASaver.Touchstone import Touchstone  # noqa: E402

win = NanoVNASaver()
t = Touchstone("tests/data/sucoflex290mm.s1p")
t.load()
print("数据点数:", len(t.s11),
      " 频率:", t.min_freq, "-", t.max_freq, "Hz",
      " 步进:", t.s11[1].freq - t.s11[0].freq, "Hz")
win.saveData(t.s11, t.s21, "sucoflex290mm.s1p")

tdr = win.windows["tdr"]

print("\n默认速度因子:", tdr.tdr_velocity_dropdown.currentText())
tdr.updateTDR()
print("估算长度:", tdr.tdr_result_label.text())

print("\n--- 换不同速度因子 ---")
for i in range(tdr.tdr_velocity_dropdown.count()):
    if not tdr.tdr_velocity_dropdown.itemText(i):
        continue
    tdr.tdr_velocity_dropdown.setCurrentIndex(i)
    name = tdr.tdr_velocity_dropdown.currentText()
    vf = tdr.tdr_velocity_dropdown.currentData()
    print(f"  {name:<45} VF={vf:<5} -> {tdr.tdr_result_label.text() or '(空)'}")

print("\n--- 换不同格式 ---")
tdr.tdr_velocity_dropdown.setCurrentIndex(1)
for i in range(tdr.format_dropdown.count()):
    tdr.format_dropdown.setCurrentIndex(i)
    print(f"  {tdr.format_dropdown.itemText(i):<18} -> {tdr.tdr_result_label.text() or '(空)'}")
