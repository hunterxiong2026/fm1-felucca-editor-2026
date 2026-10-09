# Felucca Editor Skill

> 用自然语言控制 M-VAVE FM-1 合成器（Felucca 固件），完成音色设计、多轨编曲与 SONG 播放。

[![Version](https://img.shields.io/badge/version-1.1.0-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

---

## 这是什么

一个 DeepSeek Harness（DSH）Skill，通过**直连 SysEx**（ctypes + winmm.dll）操控
FM-1 上的 Felucca 固件。支持：

- 多轨编曲（旋律 / 贝斯 / 和声 / 鼓）
- 音色参数编辑（**99 个轨道参数**：包络、LFO、琶音、调制矩阵、4×ENV、和弦模式等）
- 存/读项目槽位（A/B/C/D）
- SONG 链播放

**网页 / Web MIDI 方案已退役**。当前直连方案写入速度快 7-8 倍（单步 RTT ≈0.12s），
无挂起、无回读竞态。

---

## 目录结构

```
felucca-editor/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── LICENSE
├── reference/
│   └── sysx-map.md
├── scripts/
│   ├── felucca_link.py
│   ├── felucca_cli.py
│   ├── felucca_arrange.py
│   ├── felucca_arrange_ab.py
│   ├── play_slot.py
│   └── play_chain.py
└── examples/
    └── arrangement-recipes.md
```

---

## 安装

### 1. 放置 Skill

把 `felucca-editor/` 放进 `~/.dsh/skills/` 或项目 `.dsh/skills/`。

### 2. 创建独立 venv

```bash
cd scripts
python -m venv venv
venv\Scripts\activate
```

### 3. 硬件准备

- FM-1 刷入 **Felucca 1.1.5.1**（或兼容的 1.0.x）
- USB 连接电脑
- **关闭浏览器 / 任何 Web MIDI 会话**

---

## 使用

### 首次验证

```bash
python scripts/felucca_cli.py info
```

应输出（v1.1.5.1）：
```
version='FELUCCA 1.1.5.1', nengines=14, pcount=99, gcount=27,
nstep=64, pe0=91, ntrk=4, chainRows=16, uiCaps=9
```

### 日常指令示例

| 你的话 | Skill 的动作 |
|---|---|
| 写一段 12 小节 C 调布鲁斯 | 调 `felucca_arrange_ab.py` 双槽链 |
| 把轨 1 换成 BRASS，Attack 拉满 | 发 `TRACK_PARAM` 设置参数 |
| 播放槽位 A | `play_slot.py 0 1` |
| dump 一下当前编曲 | `felucca_cli.py dump <track>` |

### 命令行速查

```bash
# 设备信息
python felucca_cli.py info

# 参数描述
python felucca_cli.py desc 1 0          # BPM
python felucca_cli.py desc 0 29         # LEN

# 读写步进
python felucca_cli.py readstep <track> <step>
python felucca_cli.py wtest <track> <step> <note>
python felucca_cli.py dump <track>
python felucca_cli.py restore <track>

# 播放控制
python felucca_cli.py play <slot> <repeat>
python felucca_cli.py stop
python felucca_cli.py qsong

# 一键编曲
python felucca_arrange.py <slot> <bpm> <repeat>
python felucca_arrange_ab.py <jsonA> <slotA> <jsonB> <slotB> <bpm> <repA> <repB>
```

---

## 版本号规则

从 `1.0.0` 起，严格遵循 [Semantic Versioning](https://semver.org/)：

| 变更类型 | 版本号变化 | 示例 |
|---|---|---|
| **破坏性变更** | `MAJOR` | 协议不兼容、脚本接口重构 |
| **新增功能** | `MINOR` | 新引擎、新参数、新脚本 |
| **修复/校准** | `PATCH` | 解析校准、bug fix、文档纠正 |

### 当前版本：`1.1.0`

- **适配 Felucca 1.1.5.1**
- 轨道参数 91 → **99**（新增调制矩阵、4×ENV、和弦模式、鼓 8 件套音量）
- **ANALOG EDIT 从 83-90 移到 91-98**
- STEP_GET 回复尾部多 1 字节（忽略即可）

---

## 已知限制

- **仅支持 Windows**（依赖 winmm.dll）
- **多行链 `repeat>1` 不稳**（单遍链稳定）
- **Felucca 固件为 Beta**，刷入有变砖风险

---

## 用户硬约束

1. 独立 venv，绝不装任何包进系统
2. 播放验收以实际听声为准
3. 修改音色/编曲后直接改文件与设备，不输出提示词正文
4. 回复先给一句话总结

---

## 许可

MIT License，详见 [LICENSE](LICENSE)。

## 免责声明

Felucca 固件仍处于 Beta 阶段，刷入与使用存在变砖风险，请自行承担。
本 Skill 为第三方工具，与 M-VAVE 官方无关。