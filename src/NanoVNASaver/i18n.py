#  NanoVNASaver — 简体中文界面层
#
#  本文件为本 fork 新增，不属于上游 NanoVNASaver 项目。
#  上游代码仍为 GPL-3.0-or-later，本文件同样适用该许可。
#
#  设计原则：**不改动上游源码**。
#  通过在 Qt 控件类的文本 setter 上挂一层翻译代理，运行时把英文字面量
#  映射成中文。字典未命中的字符串原样透传，因此：
#    * 上游升级不会产生冲突（本文件是纯新增）
#    * 动态拼接的文本（含变量/数字）不会被误改
#    * 任何时候都能用 NANOVNA_LANG=en 关闭翻译回到英文
#
#  用法：
#      from NanoVNASaver import i18n
#      i18n.install()          # 在创建任何 QWidget 之前调用
#      i18n.tr("Sweep")        # 手工取译名（用于 QPainter 文字等）

from __future__ import annotations

import os
import re

from PySide6 import QtCore, QtGui, QtWidgets

# Qt6 里 QAction 在 QtGui 命名空间下
_QAction = QtGui.QAction


def retranslate(widget) -> None:
    """对已构建好的控件树补一轮翻译。

    用于两类场景：由 .ui 生成的对话框、以及在其他时机创建而错过钩子的控件。
    可重复调用（已含中文的文本会被跳过）。
    """
    W = QtWidgets
    nodes = [widget, *widget.findChildren(W.QWidget)]
    for w in nodes:
        for attr, setter in (
            ("text", "setText"),
            ("title", "setTitle"),
            ("placeholderText", "setPlaceholderText"),
        ):
            getter = getattr(w, attr, None)
            setter_fn = getattr(w, setter, None)
            if callable(getter) and callable(setter_fn):
                try:
                    value = getter()
                except Exception:
                    continue
                if isinstance(value, str) and value:
                    new = tr(value)
                    if new != value:
                        try:
                            setter_fn(new)
                        except Exception:
                            pass
        try:
            title = w.windowTitle()
            if title:
                w.setWindowTitle(tr(title))
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 字典
# ---------------------------------------------------------------------------
ZH: dict[str, str] = {
    # --- 主窗口 / 顶部工具栏 ---
    "Sweep": "扫描",
    "Stop": "停止",
    "Start": "开始",
    "Center": "中心",
    "Span": "跨度",
    "Segments": "分段数",
    "S11": "S11",
    "S21": "S21",
    "Rescan": "重新扫描",
    "Connect to device": "连接设备",
    "Disconnect": "断开",
    "Manage": "管理",
    "Port": "端口",
    "Network connection": "网络连接",
    "TCP/IP": "TCP/IP",
    "Sweep settings ...": "扫描设置…",
    "Sweep settings": "扫描设置",
    "Analysis ...": "分析…",
    "Analysis": "分析",
    "TDR": "TDR",
    "Time Domain Reflectometry ...": "时域反射…",
    "Calibration ...": "校准…",
    "Calibration": "校准",
    "Display setup ...": "显示设置…",
    "Display settings": "显示设置",
    "About ...": "关于…",
    "Files ...": "文件…",
    "Files": "文件",
    "Screenshot": "截图",
    "Live view": "实时画面",
    "Live View": "实时画面",
    "Reference sweep": "参考扫描",
    "Set current as reference": "设为参考",
    "Reset reference": "清除参考",
    "Reference": "参考",
    "Markers": "标记",
    "Bands": "频段",
    "Manage bands": "管理频段",
    "Settings": "设置",
    "Settings ...": "设置…",
    "Options": "选项",
    "Defaults": "默认值",
    "Device": "设备",
    "Status": "状态",
    "Format": "格式",
    "Power": "功率",
    "Window": "窗函数",
    "Custom": "自定义",
    "None": "无",
    "Add": "添加",
    "Add ...": "添加…",
    "Add row": "添加行",
    "Remove": "移除",
    "Delete": "删除",
    "Delete row": "删除行",
    "Save": "保存",
    "New": "新建",
    "Reset": "重置",
    "Refresh": "刷新",
    "Apply": "应用",
    # "Load"/"Open" 在 SOLT 校准里是标准件名（负载/开路），
    # 作为动词时一律出现在 "Load calibration"/"Open S1P file" 这类组合词里，
    # 由下面的整串条目覆盖，因此单独的 "Load" 只能按标准件翻译。
    "Load": "负载",
    "Open": "开路",
    "Short": "短路",
    "Through": "直通",
    "Uncalibrated": "未校准",
    "Locked": "已锁定",
    "Automatic": "自动",
    "Fixed": "固定",
    "Fixed span": "固定跨度",
    "Linear": "线性",
    "Logarithmic": "对数",
    "Negative": "负",
    "Positive": "正",
    "Notes": "备注",
    "Not connected.": "未连接。",
    "Original size": "原始尺寸",
    "2x size": "2 倍尺寸",
    "3x size": "3 倍尺寸",
    "4x size": "4 倍尺寸",
    "5x size": "5 倍尺寸",
    "(Sweep running)": "（扫描中）",
    " px": " px",
    " ps": " ps",
    "0.66": "0.66",
    # --- 扫描设置 ---
    "Sweep name": "扫描名称",
    "Single sweep": "单次扫描",
    "Continous sweep": "连续扫描",
    "Averaged sweep": "平均扫描",
    "Logarithmic sweep": "对数扫描",
    "Sweep band": "扫描频段",
    "Set band sweep": "设为频段扫描",
    "Pad band limits:": "频段边界留白：",
    "Datapoints": "数据点数",
    "Bandwidth": "带宽",
    "Custom points": "自定义点数",
    "Hz/step": "Hz/步进",
    "Logarithmic sweeping changes the step width in each segment in "
    "logarithmical manner. Useful in conjunction with small amount of "
    "datapoints and many segments. Step display in SweepControl cannot "
    "reflect this currently.": "对数扫描会按对数方式改变每个分段的步进宽度。适合数据点少、分段多的场合。"
    "当前扫描控件里的步进显示无法反映这一变化。",
    "Averaging allows discarding outlying samples to get better averages. "
    "Common values are 3/0, 5/2, 9/4 and 25/6.": "平均时可以丢弃偏离较大的样本以获得更稳定的均值。常用组合为 3/0、5/2、9/4、25/6。",
    "Some times when you measure amplifiers you need to use an attenuator in "
    "line with  the S21 input (CH1) here you can specify it.": "测量放大器时，S21 输入（CH1）前通常需要串接衰减器，可在此处填写其衰减量。",
    # --- 设备设置 ---
    "Device settings": "设备设置",
    "Validate received data": "校验接收数据",
    "Features:": "功能：",
    "Received data validation is not available on this device.": "此设备不支持接收数据校验。",
    # --- 显示设置 ---
    "Data axis": "数据轴",
    "Frequency axis": "频率轴",
    "Length axis": "长度轴",
    "Y axis": "Y 轴",
    "Unwrap": "解卷绕",
    "Show lines": "显示连线",
    "Displays a thin line between data points": "在数据点之间绘制细连线",
    "Dark mode": "深色模式",
    "Black background with white text": "黑色背景、白色文字",
    "Show marker numbers": "显示标记编号",
    "Displays the marker number next to the marker": "在标记旁显示其编号",
    "Filled markers": "实心标记",
    "Shows the marker as a filled triangle": "以实心三角形显示标记",
    "At the center of the marker": "位于标记中心",
    "At the tip of the marker": "位于标记尖端",
    "Chart colors": "图表配色",
    "Use custom chart colors": "使用自定义图表配色",
    "Font": "字体",
    "Show bands": "显示频段",
    "VSWR Markers": "驻波比参考线",
    "Displayed charts": "显示的图表",
    "Chart00": "图表 00",
    "Chart10": "图表 10",
    "Popout chart": "弹出图表",
    "Save image": "保存图片",
    "Core effective length": "磁芯有效长度",
    "Core area": "磁芯截面积",
    "Core number of windings": "绕组圈数",
    "Values are updated on each sweep.": "数值随每次扫描更新。",
    "Not enough datapoints to show.": "数据点不足，无法显示。",
    "No data to show.": "暂无数据。",
    # --- 标记 ---
    "Marker settings": "标记设置",
    "Colored marker name": "彩色标记名称",
    "Displayed data": "显示的数据",
    "Toggle visibility of marker readings area": "显示/隐藏标记读数区",
    "Enable Delta Marker": "启用差值标记",
    "Delta": "差值",
    "Values at marker": "标记处数值",
    "No marker": "无标记",
    "Frequency": "频率",
    "Resistance": "电阻",
    "Reactance": "电抗",
    "VSWR": "驻波比",
    "S21 Gain": "S21 增益",
    "Highest value": "最高值",
    "Lowest value": "最低值",
    "Length": "长度",
    "Delay": "延时",
    "Impedance": "阻抗",
    "Series L": "串联电感",
    "Series C": "串联电容",
    "Parallel R": "并联电阻",
    "Parallel X": "并联电抗",
    "Return loss": "回波损耗",
    "Phase": "相位",
    "Quality factor": "品质因数",
    "Capacitance": "电容",
    "Inductance": "电感",
    "Permeability": "磁导率",
    "Group delay": "群延时",
    # --- 频段 ---
    "Reset bands/Select region": "重置频段/选择区域",
    "Reset to Region 1 defaults": "恢复 ITU 1 区默认值",
    "Reset to Region 2 defaults": "恢复 ITU 2 区默认值",
    "Reset to Region 3 defaults": "恢复 ITU 3 区默认值",
    "Band name": "频段名称",
    "Band": "频段",
    "Low": "下限",
    "High": "上限",
    # --- 校准 ---
    "Calibration settings": "校准设置",
    "Active calibration": "当前校准",
    "Device calibration": "设备内校准",
    "NanoVNA": "NanoVNA",
    "Calibrate": "校准",
    "Calibration assistant": "校准向导",
    "Calibration standards": "校准标准件",
    "Use ideal values": "使用理想值",
    "Use s1p files": "使用 S1P 文件",
    "Use coefficients": "使用系数",
    "Short S1P file": "短路 S1P 文件",
    "Open S1P file": "开路 S1P 文件",
    "Load S1P file": "载入 S1P 文件",
    "Load calibration": "载入校准",
    "Save calibration": "保存校准",
    "Saved settings": "已保存的配置",
    "This calibration assistant will help you create a calibration in the "
    "NanoVNA and take you through all the steps.": "本校准向导会在 NanoVNA 上执行校准，并逐步引导你完成全部操作。",
    "The required steps for a 1-port calibration are now complete.\n\nIf you "
    "also want to calibrate the second port, continue.\n\nIf you are satisfied "
    "with the current calibration, press Apply.": "单端口校准所需的步骤已完成。\n\n如需校准第二个端口，请继续。\n\n"
    "若对当前校准满意，请按「应用」。",
    'Please connect the "short" standard to port 0 of the NanoVNA.\n\n'
    "Press Ok when ready.": "请把「短路」标准件接到 NanoVNA 的端口 0。\n\n就绪后按「确定」。",
    'Please connect the "open" standard to port 0 of the NanoVNA.\n\n'
    "Either use the one included with the NanoVNA, or your own.": "请把「开路」标准件接到 NanoVNA 的端口 0。\n\n可用随机附带件，也可用自备件。",
    'Please connect the "load" standard to port 0 of the NanoVNA.\n\n'
    "Press Ok when ready.": "请把「负载」标准件接到 NanoVNA 的端口 0。\n\n就绪后按「确定」。",
    'Please connect the "load" standard to port 1 of the NanoVNA.\n\n'
    "If available, use the one included with the NanoVNA.": "请把「负载」标准件接到 NanoVNA 的端口 1。\n\n如有随机附带件请优先使用。",
    'Please connect the "through" standard between port 0 and port 1 of the '
    "NanoVNA.\n\nPress Ok when ready.": "请把「直通」标准件接在 NanoVNA 的端口 0 与端口 1 之间。\n\n就绪后按「确定」。",
    'The calibration process is now complete. Press "Apply" to apply the '
    "calibration.\n\nIf you want to redo a step, press the button for that "
    "step again.": "校准流程已完成。按「应用」使校准生效。\n\n"
    "若要重做某一步，再次按下该步骤对应的按钮即可。",
    "Please ensure the NanoVNA is connected before attempting calibration.": "请先确认 NanoVNA 已连接，再进行校准。",
    "Applying calibration failed.": "应用校准失败。",
    "Error during calibration": "校准出错",
    "Calibration data": "校准数据",
    "Sweep the standards and press the buttons in order.": "扫描各标准件后依次按下对应按钮。",
    # --- 分析 ---
    "Sweep analysis": "扫描分析",
    "Select analysis": "选择分析项目",
    "Low-pass filter": "低通滤波器",
    "Band-pass filter": "带通滤波器",
    "High-pass filter": "高通滤波器",
    "Band-stop filter": "带阻滤波器",
    "Simple Peak search": "简易峰值搜索",
    "Peak search": "峰值搜索",
    "VSWR analysis": "驻波比分析",
    "Resonance analysis": "谐振分析",
    "HWEF analysis": "HWEF 天线分析",
    "EFHW analysis": "EFHW 天线分析",
    "MagLoop analysis": "磁环天线分析",
    "Run analysis": "运行分析",
    "Run automatically": "自动运行",
    "No resonance found": "未找到谐振点",
    "Lower side:": "低端：",
    "Upper side:": "高端：",
    "Multiple minimums, not magloop or try to lower VSWR limit": "存在多个极小值：不是磁环天线，或请降低驻波比门限",
    "<b>Results</b>": "<b>结果</b>",
    "<b>Settings</b>": "<b>设置</b>",
    "Cutoff frequency": "截止频率",
    "Bandwidth:": "带宽：",
    "Center frequency": "中心频率",
    # --- 文件 ---
    "Import file": "导入文件",
    "Export file": "导出文件",
    "Load as sweep": "作为扫描数据载入",
    "Load reference": "载入参考",
    "Save 1-Port file (S1P)": "保存单端口文件 (S1P)",
    "Save 2-Port file (S2P)": "保存双端口文件 (S2P)",
    "Touchstone 1-Port Files (*.s1p);;All files (*.*)": "Touchstone 单端口文件 (*.s1p);;所有文件 (*.*)",
    "Touchstone 2-Port Files (*.s2p);;All files (*.*)": "Touchstone 双端口文件 (*.s2p);;所有文件 (*.*)",
    "Touchstone Files (*.s1p *.s2p);;All files (*.*)": "Touchstone 文件 (*.s1p *.s2p);;所有文件 (*.*)",
    "All files (*.*)": "所有文件 (*.*)",
    "Save file": "保存文件",
    "Open file": "打开文件",
    "Calibration files (*.cal);;All files (*.*)": "校准文件 (*.cal);;所有文件 (*.*)",
    "Images (*.png)": "图片 (*.png)",
    # --- TDR ---
    "Velocity factor": "速度因子",
    "Cable": "线缆类型",
    "Custom velocity factor": "自定义速度因子",
    "TDR settings": "TDR 设置",
    "Step response": "阶跃响应",
    "Impedance along cable": "沿缆阻抗",
    # --- 错误 / 提示 ---
    "ERROR - Unable to determine what the latest version is!": (
        "错误：无法确定最新版本号！"
    ),
    "Data error reading versions.": "读取版本信息时数据出错。",
    "Connection error.": "连接错误。",
    "Error": "错误",
    "Warning": "警告",
    "Information": "提示",
    "Question": "询问",
    "Could not connect to device": "无法连接到设备",
    "No device found": "未找到设备",
    "Sweep error": "扫描出错",
    "Invalid data during sweep": "扫描过程中数据无效",
    # --- 图表标题（S11）---
    "S11 Smith Chart": "S11 史密斯圆图",
    "S11 Return Loss": "S11 回波损耗",
    "S11 VSWR": "S11 驻波比",
    "S11 Phase": "S11 相位",
    "S11 Group Delay": "S11 群延时",
    "S11 Quality Factor": "S11 品质因数",
    "S11 R+jX": "S11 R+jX",
    "S11 Real/Imaginary": "S11 实部/虚部",
    "S11 Serial C": "S11 串联电容",
    "S11 Serial L": "S11 串联电感",
    "S11 |Z|": "S11 |Z|",
    "S11 & S21 LogMag": "S11 与 S21 对数幅度",
    "|S11|": "|S11|",
    # --- 图表标题（S21）---
    "S21 Phase": "S21 相位",
    "S21 Polar Plot": "S21 极坐标图",
    "S21 R+jX shunt": "S21 R+jX 并联",
    "S21 R+jX series": "S21 R+jX 串联",
    "S21 Real/Imaginary": "S21 实部/虚部",
    "S21 |Z| series": "S21 |Z| 串联",
    "S21 |Z| shunt": "S21 |Z| 并联",
    "Signal Analyser dBm": "信号分析 dBm",
    "|S21|": "|S21|",
    "S11 R/Ω & X/Ω": "S11 R/Ω 与 X/Ω",
    "S11 μ": "S11 μ",
    # --- 低频/滤波器图表 ---
    "|Z| (lowpass)": "|Z|（低通）",
    "S11 (lowpass)": "S11（低通）",
    "VSWR (lowpass)": "驻波比（低通）",
    "Refl (lowpass)": "反射（低通）",
    "Refl (bandpass)": "反射（带通）",
    # --- 第二批：控件标签补全 ---
    "Sweep control": "扫描控制",
    "Serial port control": "串口控制",
    "Analysis type": "分析类型",
    "Select band": "选择频段",
    "Marker size": "标记大小",
    "Sweep color": "扫描曲线颜色",
    "Second sweep color": "第二条曲线颜色",
    "Reference color": "参考曲线颜色",
    "Second reference color": "第二条参考颜色",
    "Chart bands": "图表频段",
    "Chart background": "图表背景",
    "Chart foreground": "图表前景",
    "Chart text": "图表文字",
    "Line thickness": "线宽",
    "Point size": "点大小",
    "Font size": "字号",
    "Validation": "校验",
    "Isolation": "隔离度",
    "Thrurefl": "直通反射",
    "Offset delay": "偏移延时",
    "Offset Delay (ps)": "偏移延时 (ps)",
    "Hide data": "隐藏数据",
    "Min gain": "最小增益",
    "Max gain": "最大增益",
    "Min VSWR": "最小驻波比",
    "Estimated cable length": "估算线缆长度",
    "Lowpass filter analysis": "低通滤波器分析",
    "Please place Marker 1 in the filter passband.": (
        "请把标记 1 放在滤波器通带内。"
    ),
    "Number of measurements to average": "平均次数",
    "Number to discard": "丢弃个数",
    "Attenuator in port CH1 (s21) in dB": "CH1（S21）端口衰减量 (dB)",
    "Firmware": "固件版本",
    "Hardware": "硬件版本",
    "Result": "结果",
    "Roll-off": "滚降",
    "Source": "来源",
    "About NanoVNASaver": "关于 NanoVNASaver",
    "Runtime information": "运行环境信息",
    "Check for updates": "检查更新",
    "Copy": "复制",
    "NanoVNA Firmware": "NanoVNA 固件",
    "not connected.": "未连接。",
    "not connected": "未连接",
    "unknown": "未知",
    "Cancel": "取消",
    "OK": "确定",
    "Close": "关闭",
    "Yes": "是",
    "No": "否",
    "Continue": "继续",
    "Back": "返回",
    "Next": "下一步",
    "Finish": "完成",
    # 校准标准件系数
    "L0 (H(e-12))": "L0 (H×1e-12)",
    "L1 (H(e-24))": "L1 (H×1e-24)",
    "L2 (H(e-33))": "L2 (H×1e-33)",
    "L3 (H(e-42))": "L3 (H×1e-42)",
    "C0 (F(e-15))": "C0 (F×1e-15)",
    "C1 (F(e-27))": "C1 (F×1e-27)",
    "C2 (F(e-36))": "C2 (F×1e-36)",
    "C3 (F(e-45))": "C3 (F×1e-45)",
    "Capacitance (F(e-15))": "电容 (F×1e-15)",
    "Inductance (H(e-12))": "电感 (H×1e-12)",
    "Resistance (Ω)": "电阻 (Ω)",
    "Length (mm)": "长度 (mm)",
    "Offset": "偏移",
    "Port 1": "端口 1",
    "Port 2": "端口 2",
    "Port 0": "端口 0",
    "Port 1 extension": "端口 1 延长线",
    "Port extension": "端口延长",
    "Show": "显示",
    "Hide": "隐藏",
    "Enabled": "启用",
    "Disabled": "禁用",
    # 线缆材质（型号名保留原文，材质名翻译）
    "Polyethylene (0.66)": "聚乙烯 (0.66)",
    "PTFE (Teflon) (0.70)": "PTFE（特氟龙）(0.70)",
    "Foam or Cellular PE (0.78)": "发泡/蜂窝聚乙烯 (0.78)",
    "Semi-solid PE (SSPE) (0.84)": "半实心聚乙烯 (SSPE) (0.84)",
    "Air (Helical spacers) (0.94)": "空气（螺旋垫片）(0.94)",
    "Jelly filled (0.64)": "填充胶型 (0.64)",
    "Pulp Insulation (0.72)": "纸浆绝缘 (0.72)",
    # 图表名补全
    "S21 Group Delay": "S21 群延时",
    "S11 Capacitance": "S11 电容",
    "S11 Inductance": "S11 电感",
    "Return loss is": "回波损耗为",
    "Data point is": "数据点为",
    "Example marker": "示例标记",
    "SN": "序列号",
    "S11 Magnitude": "S11 幅度",
    "S11 Permeability": "S11 磁导率",
    # --- 上下文相关：同一个英文词在不同控件里含义不同 ---
    # Start/Stop 在扫描控件里是"起始/终止频率"，不是按钮的"开始/停止"
    "QLabel:Start": "起始频率",
    "QLabel:Stop": "终止频率",
    "QLabel:Center": "中心频率",
    "QLabel:Span": "扫频跨度",
    "QPushButton:Sweep": "开始扫描",
    "QPushButton:Stop": "停止扫描",
    # 校准里的 Load/Short/Open/Through 是标准件
    "QGroupBox:Load": "负载",
    "QPushButton:Load": "负载",
    "QGroupBox:Open": "开路",
    "QGroupBox:Short": "短路",
    "QGroupBox:Through": "直通",
    # --- 标记读数（术语按国内习惯） ---
    "Wavelength": "波长",
    "Admittance": "导纳",
    "Series R": "串联电阻",
    "Series X": "串联电抗",
    "Parallel L": "并联电感",
    "Parallel C": "并联电容",
    "Actual frequency": "实际频率",
    "S11 Polar": "S11 极坐标",
    "S21 Polar": "S21 极坐标",
    "S21 Magnitude": "S21 幅度",
    "S11 Z Magnitude": "S11 |Z|",
    "S21 Z Magnitude shunt": "S21 |Z| 并联",
    "S21 Z Magnitude series": "S21 |Z| 串联",
    "S11 Quality factor": "S11 品质因数",
    "Series equivalent L/C": "串联等效 L/C",
    "Series equivalent L": "串联等效电感",
    "Series equivalent C": "串联等效电容",
    "Parallel equivalent L/C": "并联等效 L/C",
    "Parallel equivalent L": "并联等效电感",
    "Parallel equivalent C": "并联等效电容",
}

# 含 CJK 的串直接透传，避免二次翻译（例如已经是中文的动态文本）
_CJK = re.compile(r"[\u4e00-\u9fff]")
_EN_BY_ZH: dict[str, str] = {v: k for k, v in ZH.items()}


# 动态串模板
def _with_unit(m):
    """把 "S11 Serial C (F)" 这类"名称 (单位)"拆开，只译名称部分。"""
    base = ZH.get(m.group(1))
    if not base:
        return m.group(0)  # 名称不认识就保持原样
    return f"{base} ({m.group(2)})"


def _paren_inner(m):
    """括号里还有可译内容时递归翻译，例如窗口标题里的 (Sweep: …)。"""
    inner = tr(m.group(2))
    if inner == m.group(2):
        return m.group(0)
    return f"{m.group(1)}（{inner}）"


_PATTERNS: list[tuple[re.Pattern, object]] = [
    (re.compile(r"^Marker (\d+)$"), lambda m: f"标记 {m.group(1)}"),
    (
        re.compile(r"^Sweep span: (.+?) to (.+)$"),
        lambda m: f"扫描范围：{m.group(1)} 至 {m.group(2)}",
    ),
    (
        re.compile(r"^Estimated cable length: (.+)$"),
        lambda m: f"估算线缆长度：{m.group(1)}",
    ),
    (
        re.compile(r"^Cutoff frequency: (.+)$"),
        lambda m: f"截止频率：{m.group(1)}",
    ),
    (re.compile(r"^Bandwidth: (.+)$"), lambda m: f"带宽：{m.group(1)}"),
    (re.compile(r"^(.+) dB point:$"), lambda m: f"{m.group(1)} dB 点："),
    (
        re.compile(r"^Delta Marker (\d+) - Marker (\d+)$"),
        lambda m: f"差值标记 {m.group(1)} − 标记 {m.group(2)}",
    ),
    # 窗口标题里的数据源标注：整体形如
    # "NanoVNA Saver x.y (Sweep: file @ N points)"
    (
        re.compile(r"^Sweep: (.+) @ (\d+) points$"),
        lambda m: f"扫描：{m.group(1)} @ {m.group(2)} 点",
    ),
    (
        re.compile(r"^Reference: (.+) @ (\d+) points$"),
        lambda m: f"参考：{m.group(1)} @ {m.group(2)} 点",
    ),
    (re.compile(r"^(.+) \(([^)]+)\)$"), _with_unit),
    (re.compile(r"^(.+?) \((.+)\)$"), _paren_inner),
    (
        re.compile(r"^(.+): (.+)$"),
        lambda m: f"{ZH.get(m.group(1), m.group(1))}：{m.group(2)}",
    ),
]
_INSTALLED = False
_ENABLED = True

# 常见缩写括注：译名以左边结尾时，在宽敞处补上右边的英文缩写。
# 只用「结尾匹配」，所以 "驻波比参考线" 这种复合词不会被拆坏。
_ABBR_PAIRS: tuple[tuple[str, str], ...] = (
    ("VSWR", "驻波比"),
    ("TDR", "时域反射"),
    ("RL", "回波损耗"),
    ("GD", "群延时"),
    ("Q", "品质因数"),
    ("μ", "磁导率"),
)

# 这些上下文的横向空间足够放括注；标记读数、下拉项、表格列头等窄处不加。
_ROOMY_CTX = {
    "Chart",  # 图表标题（QPainter 绘制）
    "QGroupBox",
    "QPushButton",
    "QMenu",
    "QAction",
    "QWidget",  # 窗口标题
    "QTabWidget",
    "QMessageBox",
    "QListWidget",
}


# 缩写括注的作用范围，可用环境变量 NANOVNA_ABBR 覆盖：
#   title（默认）—— 只加在标题/分组框/按钮这类宽敞处
#   all          —— 到处加（含标记读数、下拉项）
#   off          —— 完全不加
_ABBR_SCOPE = os.environ.get("NANOVNA_ABBR", "title").lower()


def _add_abbr(text: str) -> str:
    """给译名补上英文缩写括注，例如 'S11 驻波比' -> 'S11 驻波比（VSWR）'。

    带单位的图表标题形如 'S11 回波损耗 (dB)'，括注要插在单位之前。
    """
    if not text or "（" in text:
        return text

    # 先剥掉结尾单位 " (dB)" / " (ns)" 之类
    unit = ""
    body = text
    m = re.search(r"\s*\(([^()]*)\)\s*$", body)
    if m:
        unit = text[m.start() :]
        body = text[: m.start()]

    # 再剥掉结尾标点，稍后补回
    tail = ""
    for mark in ("…", "：", "..."):
        if body.endswith(mark):
            tail = mark
            body = body[: -len(mark)]
            break

    for abbr, zh_term in _ABBR_PAIRS:
        if body.endswith(zh_term):
            # 缩写在中文词后、单位前：S11 回波损耗（RL）(dB)
            return f"{body}（{abbr}）{unit.strip()}{tail}"
    return text


def _translate(text: str, ctx: str) -> str:
    """核心查表逻辑（不含缩写括注）。"""
    if not _ENABLED or not isinstance(text, str) or not text:
        return text
    if _CJK.search(text):
        return text

    if ctx:
        hit = ZH.get(f"{ctx}:{text}")
        if hit is not None:
            return hit

    hit = ZH.get(text)
    if hit is not None:
        return hit

    # 尾随冒号（含结尾空格，例如 uic 里的 "NanoVNA Firmware: "）
    stripped = text.rstrip()
    if stripped.endswith(":"):
        base = stripped[:-1].rstrip()
        hit = ZH.get(base)
        if hit:
            return f"{hit}："

    # 尾随省略号
    if stripped.endswith("..."):
        base = stripped[:-3].rstrip()
        hit = ZH.get(base)
        if hit:
            return f"{hit}…"

    # 动态串：builder 返回原文表示"这条规则不适用"，继续试下一条
    for pattern, builder in _PATTERNS:
        m = pattern.match(text)
        if not m:
            continue
        out = builder(m)
        if isinstance(out, str) and out and out != text:
            return out

    return text


def tr(text: str, ctx: str = "") -> str:
    """取译名；未命中或已含中文则原样返回。

    ctx 是控件类名（"QLabel"/"QPushButton"/…）。同一个英文词在不同控件里
    可能含义不同（Start 在扫描控件里是起始频率，在别处可能是"开始"），
    因此先查 "类名:原文" 这样的上下文键，再退回纯文本键。

    宽松上下文（标题、分组框、按钮、图表标题等）还会在译名后补英文缩写，
    例如 "S11 驻波比" -> "S11 驻波比（VSWR）"；窄处保持短名。
    """
    out = _translate(text, ctx)
    if out != text and _ABBR_SCOPE != "off":
        if _ABBR_SCOPE == "all" or ctx in _ROOMY_CTX:
            out = _add_abbr(out)
    return out


def untr(text: str) -> str:
    """反查：把界面上的中文译名还原成原始的英文标识。

    仅用于少量"中文文字却要当 key 用"的场合（例如图表名要写回配置）。
    """
    if not isinstance(text, str) or not text:
        return text
    return _EN_BY_ZH.get(text, text)


def _args_translate(args: tuple, index: int, ctx: str = "") -> tuple:
    """把 args[index] 是字符串时替换为译名。"""
    if len(args) > index and isinstance(args[index], str):
        lst = list(args)
        lst[index] = tr(lst[index], ctx)
        return tuple(lst)
    return args


def _wrap_method(cls, name: str, index: int) -> None:
    """给 cls.name 的第一个字符串参数套翻译（带类名上下文）。"""
    orig = getattr(cls, name)
    ctx = cls.__name__

    def wrapper(self, *args, **kwargs):
        return orig(self, *_args_translate(args, index, ctx), **kwargs)

    wrapper.__name__ = name
    setattr(cls, name, wrapper)


def _wrap_ctor(cls, index: int = 0) -> None:
    """给构造函数第 index 个字符串参数套翻译（带类名上下文）。"""
    orig = cls.__init__
    ctx = cls.__name__

    def wrapper(self, *args, **kwargs):
        return orig(self, *_args_translate(args, index, ctx), **kwargs)

    wrapper.__name__ = "__init__"
    cls.__init__ = wrapper


def install() -> None:
    """挂上翻译层。可在任何 QWidget 创建之前调用，重复调用无副作用。"""
    global _INSTALLED, _ENABLED  # noqa: PLW0603
    if _INSTALLED:
        return
    if os.environ.get("NANOVNA_LANG", "").lower() in {"en", "en_us"}:
        _ENABLED = False
        _INSTALLED = True
        return

    W = QtWidgets

    # 窗口 / 控件文本
    _wrap_method(W.QWidget, "setWindowTitle", 0)
    _wrap_method(W.QWidget, "setToolTip", 0)
    _wrap_method(W.QWidget, "setStatusTip", 0)
    _wrap_method(W.QLabel, "setText", 0)
    _wrap_method(W.QAbstractButton, "setText", 0)  # 按钮/复选/单选/工具按钮
    _wrap_method(W.QGroupBox, "setTitle", 0)
    _wrap_method(W.QLineEdit, "setPlaceholderText", 0)
    _wrap_method(W.QTabWidget, "setTabText", 1)
    _wrap_method(W.QComboBox, "setItemText", 1)
    _wrap_method(W.QMenu, "setTitle", 0)

    # 构造期文本（setText 覆盖不到 C++ 构造函数里的赋值）
    for cls in (
        W.QLabel,
        W.QPushButton,
        W.QCheckBox,
        W.QRadioButton,
        W.QToolButton,
        W.QGroupBox,
        _QAction,
        W.QMenu,
    ):
        _wrap_ctor(cls, 0)

    # 下拉框
    _orig_add_item = W.QComboBox.addItem

    def add_item(self, *args, **kwargs):
        # 常见两种签名：addItem(text) / addItem(text, userData)，
        # 少数用 addItem(icon, text)
        if args and isinstance(args[0], str):
            return _orig_add_item(
                self, tr(args[0], "QComboBox"), *args[1:], **kwargs
            )
        if len(args) >= 2 and isinstance(args[1], str):
            return _orig_add_item(
                self, args[0], tr(args[1], "QComboBox"), *args[2:], **kwargs
            )
        return _orig_add_item(self, *args, **kwargs)

    W.QComboBox.addItem = add_item

    _orig_add_items = W.QComboBox.addItems

    def add_items(self, items):
        return _orig_add_items(self, [tr(i, "QComboBox") for i in items])

    W.QComboBox.addItems = add_items

    # 关键：不少代码把 currentText() 当「逻辑键」用（比较 "Refl (bandpass)"、
    # 查 FORMAT_DEFAULTS 表、拼配置名…）。下拉项显示的是译名，读取时必须
    # 还原成英文，否则这些逻辑会静默失效（TDR 窗口就因此崩溃过）。
    _orig_current_text = W.QComboBox.currentText

    def current_text(self):
        return untr(_orig_current_text(self))

    W.QComboBox.currentText = current_text

    # 标签页
    _orig_add_tab = W.QTabWidget.addTab

    def add_tab(self, *args, **kwargs):
        if len(args) == 2:
            return _orig_add_tab(
                self, args[0], tr(args[1], "QTabWidget"), **kwargs
            )
        if len(args) == 3:
            return _orig_add_tab(
                self, args[0], args[1], tr(args[2], "QTabWidget"), **kwargs
            )
        return _orig_add_tab(self, *args, **kwargs)

    W.QTabWidget.addTab = add_tab

    # 列表 / 表格
    _orig_lw_add_item = W.QListWidget.addItem

    def lw_add_item(self, item):
        if isinstance(item, str):
            return _orig_lw_add_item(self, tr(item, "QListWidget"))
        return _orig_lw_add_item(self, item)

    W.QListWidget.addItem = lw_add_item

    _orig_lw_add_items = W.QListWidget.addItems

    def lw_add_items(self, items):
        return _orig_lw_add_items(self, [tr(i, "QListWidget") for i in items])

    W.QListWidget.addItems = lw_add_items

    for name in ("setHorizontalHeaderLabels", "setVerticalHeaderLabels"):
        _orig = getattr(W.QTableWidget, name)

        def make(orig):
            def wrapper(self, labels):
                return orig(self, [tr(x, "QTableWidget") for x in labels])

            return wrapper

        setattr(W.QTableWidget, name, make(_orig))

    # 消息框（静态方法走 C++，不经 Python 的 setText）
    for name in ("information", "warning", "critical", "question"):
        _orig_box = getattr(W.QMessageBox, name)

        def make_box(orig):
            def wrapper(parent, title, text, *rest, **kw):
                return orig(
                    parent,
                    tr(title, "QMessageBox"),
                    tr(text, "QMessageBox"),
                    *rest,
                    **kw,
                )

            return wrapper

        setattr(W.QMessageBox, name, make_box(_orig_box))

    # 文件对话框
    for name in ("getOpenFileName", "getSaveFileName"):
        _orig_fd = getattr(W.QFileDialog, name)

        def make_fd(orig):
            def wrapper(
                parent=None, caption="", directory="", filter="", *rest, **kw
            ):
                return orig(
                    parent,
                    tr(caption, "QFileDialog"),
                    directory,
                    tr(filter, "QFileDialog"),
                    *rest,
                    **kw,
                )

            return wrapper

        setattr(W.QFileDialog, name, make_fd(_orig_fd))

    _orig_ged = W.QFileDialog.getExistingDirectory

    def get_existing_dir(parent=None, caption="", directory="", *a, **kw):
        return _orig_ged(
            parent, tr(caption, "QFileDialog"), directory, *a, **kw
        )

    W.QFileDialog.getExistingDirectory = get_existing_dir

    # 输入对话框
    for name in ("getText", "getInt", "getDouble", "getItem"):
        _orig_id = getattr(W.QInputDialog, name)

        def make_id(orig):
            def wrapper(parent, title, label, *rest, **kw):
                return orig(
                    parent,
                    tr(title, "QInputDialog"),
                    tr(label, "QInputDialog"),
                    *rest,
                    **kw,
                )

            return wrapper

        setattr(W.QInputDialog, name, make_id(_orig_id))

    # 表单布局：addRow("标签", 控件) 的标签由 C++ 侧创建 QLabel，钩不到
    # 普通控件的 setText，只能在这里拦截
    for name in ("addRow", "insertRow"):
        _orig_row = getattr(W.QFormLayout, name)

        def make_row(orig):
            def wrapper(self, *args, **kwargs):
                if args and isinstance(args[0], str):
                    args = (tr(args[0], "QFormLayout"), *args[1:])
                return orig(self, *args, **kwargs)

            return wrapper

        setattr(W.QFormLayout, name, make_row(_orig_row))

    # 图表轴标签等由 QPainter 直接绘制的文字
    _orig_draw_text = QtGui.QPainter.drawText

    def draw_text(self, *args, **kwargs):
        if args and isinstance(args[-1], str):
            # 图表标题与轴标签都走这里；标题空间够，允许带缩写括注
            args = (*args[:-1], tr(args[-1], "Chart"))
        return _orig_draw_text(self, *args, **kwargs)

    QtGui.QPainter.drawText = draw_text

    # pyside6-uic 生成的界面代码调用 QCoreApplication.translate(context, text)
    def _qt_translate(context, text, disambiguation=None, n=-1):
        return tr(text)

    QtCore.QCoreApplication.translate = _qt_translate

    _INSTALLED = True
