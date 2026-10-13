# Felucca Editor

> 通过直连 SysEx（ctypes + winmm）操作 M-VAVE FM-1 上的 **Felucca v1.5** 固件，实现音色参数编辑、多轨编曲、项目槽位管理与 SONG 播放链。

![Firmware](https://img.shields.io/badge/firmware-v1.5-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-yellow)

---

## 这是什么

一套**零第三方依赖**的 Python 脚本（仅用 `ctypes` 直调 Windows `winmm.dll`），向 M-VAVE FM-1 发送 SysEx 帧，控制 Felucca v1.5 固件：

- **4 轨编曲**：旋律 / 和弦 / 贝斯 / 鼓
- **111 个轨道参数 + 27 个全局参数**（v1.5）
- **64 步 / 轨**，4 个项目槽位，16 行 SONG 播放链
- **14 种合成引擎**：ANALOG / PHASE / LOFI / SAMPLE / VOICE / DRUM / FM6 …

同时是一份 **Claude Skill**（`SKILL.md`）：AI 可据此直接生成 `arrangement.json` 并写入设备。

---

## 前置要求

| 项目 | 要求 |
|---|---|
| 硬件 | M-VAVE FM-1 |
| 固件 | **FELUCCA v1.5**（pcount=111 / pe0=103 / chainRows=16）|
| 运行时 | Python **3.10+**（独立 venv，不装系统 Python）|
| 平台 | **Windows**（依赖 winmm.dll）|

> ⚠️ 直连前**必须关闭浏览器 / 任何 Web MIDI 会话**——设备输入独占。

---

## 安装

```powershell
git clone https://github.com/hunterxiong2026/felucca-editor.git
cd felucca-editor

# 建独立 venv（勿装进系统 Python）
python -m venv scripts\venv
scripts\venv\Scripts\activate

# 无第三方依赖；如需 MIDI 导出，再装：
pip install mido
```

---

## 快速开始

### 1. 确认设备

```powershell
python scripts\felucca_cli.py info
# → version='FELUCCA v1.5', pcount=111, pe0=103, ntrk=4
```

系统里有多个 "Felucca" 设备时，脚本会**自动探测固件、跳过 SLOOP**：

```powershell
python scripts\felucca_link.py     # 枚举全部 MIDI 设备并演示匹配
```

精确指定某台设备：

```powershell
$env:FELUCCA_MIDI_NAME="3 - Felucca"
```

### 2. 一键编曲

编写 `arrangement.json`（4 轨结构见 `felucca_arrange.py` 头部注释），然后：

```powershell
python scripts\felucca_arrange.py <slot> <bpm> <repeat>

# 例：写入槽 3，BPM 72，播放 1 遍
python scripts\felucca_arrange.py 3 72 1
```

### 3. 双槽链

```powershell
python scripts\felucca_arrange_ab.py <jsonA> <slotA> <jsonB> <slotB> <bpm> <repA> <repB>
```

### 4. 只播放已保存的槽位

```powershell
python scripts\play_slot.py 3 1        # 槽 3 播放 1 遍
python scripts\play_chain.py 0 1 1 1   # 槽 0×1 → 槽 1×1
```

### 5. 命令行调试

```powershell
python scripts\felucca_cli.py dump 0             # 读轨 0 的 0..63 步
python scripts\felucca_cli.py desc 0 107         # 查轨内参数 107（CUT）的范围
python scripts\felucca_cli.py readparam 0 103    # 读轨 0 的 WAVE 值
python scripts\felucca_cli.py stop               # 停止播放
```

---

## 脚本清单

| 脚本 | 作用 |
|---|---|
| `felucca_link.py` | 直连核心库（动态设备匹配 / 收发 / INFO·DESC·STEP·SONG 解析）|
| `felucca_cli.py` | 命令行工具 |
| `felucca_arrange.py` | 单槽一键编曲（写 4 轨 → 存槽 → 播放）|
| `felucca_arrange_ab.py` | 双槽链编曲 |
| `play_slot.py` / `play_chain.py` | 仅播放脚本 |

---

## 目录结构

```
felucca-editor/
├── SKILL.md                      # Claude Skill 入口
├── README.md                     # 本文件
├── CHANGELOG.md
├── LICENSE
├── scripts/
│   ├── felucca_link.py           # 直连核心库
│   ├── felucca_cli.py
│   ├── felucca_arrange.py
│   ├── felucca_arrange_ab.py
│   ├── play_slot.py
│   └── play_chain.py
├── reference/
│   ├── protocol.md               # 帧格式 / 命令表 / STEP·SONG 布局 / 直连坑
│   ├── params.md                 # 111 轨道参数 + 27 全局参数 + 枚举（权威）
│   ├── sysx-map.md               # 实机验证的参数映射速查
│   └── arrangement-metrics.md    # 编曲质量指标（硬指标 + 参考方向）
└── examples/
    └── arrangement-recipes.md    # 已验收的编曲配方
```

---

## 参考文档

生成编曲数据前**必读**：

- **[`reference/protocol.md`](reference/protocol.md)** — 帧格式、命令枚举、STEP/SONG 布局、INFO 解析、直连坑、设备名匹配
- **[`reference/params.md`](reference/params.md)** — 111 轨道参数 + 27 全局参数 + 全部枚举（**权威参数表**）
- **[`reference/sysx-map.md`](reference/sysx-map.md)** — 参数映射速查（实机验证）
- **[`reference/arrangement-metrics.md`](reference/arrangement-metrics.md)** — 编曲质量指标（硬指标 + 参考方向）
- **[`examples/arrangement-recipes.md`](examples/arrangement-recipes.md)** — 已验收配方

---

## 关键坑速查

| 坑 | 说明 |
|---|---|
| **ANALOG EDIT 移位** | v1.5 在 **101-110**（旧 91-98 变为 SYNC/INSERT 区）|
| **STEP_GET 请求** | 只带 `[i]`，**不带 tr**（先 `TRACK [tr]` 选轨）|
| **TIE 语义** | `time=1` 必须有前序 NOTE 起始步；全 TIE = 静音 |
| **SONG 播放** | `op=1` 只配置行，**必须 `op=2` 才出声** |
| **带符号参数** | FLT(-64~63) / TUNE(-50~50) / PAN(-64~63)，写 0-127 出错 |
| **SWG 范围** | **0-100**，不是 0-127 |
| **LEN 范围** | **1-64** |
| **GATE 范围** | **1-127**（0 = 无声）|
| **RATE 枚举** | 0-5（1/8~32T）|
| **TRACK_DUMP 高字节** | v1.5 `(hi, lo)` **高字节在前**（SLOOP 是 `(lo, hi)`）|
| **多行链 repeat>1** | 不稳；单遍链（repeat=1）稳定 |

---

## 已知限制

- **仅 Windows**（依赖 `winmm.dll`）
- **多行链 `repeat>1` 不稳**（单遍链稳定）
- INSERT 效果 A/B/C 参数含义未完全逆向
- SYNC / TRIG / POL / QNTZ / SPRD 参数范围待完整校准
- Felucca 固件为 Beta，刷入有变砖风险

---

## License

[MIT](LICENSE) © hunterxiong2026