# Changelog

本项目所有显著变更均记录于此。
格式基于 [Keep a Changelog](https://keepachangelog.com/)，
版本号遵循 [Semantic Versioning](https://semver.org/)。

## [Unreleased]

### 计划
- [ ] 多行链 `repeat>1` 稳定性修复
- [ ] 调制矩阵 / 4×ENV / 和弦模式的写入 API 封装
- [ ] MIDI 文件导出
- [ ] macOS 支持（CoreMIDI）

---

## [1.1.0] - 2026-10-09

### 新增
- **适配 Felucca 1.1.5.1**
- 轨道参数 91 → **99**
- 新增参数区段：
  - **41-45**：GLMOD / PRIO / ALLOC / DTUNE / SLCR
  - **46-48**：MSEQ PAT / RATE / DEPTH
  - **49-60**：调制矩阵（4 组 SRC×DST×AMT）
  - **61-80**：4×ENV（每组 ATK/DEC/SUS/REL/LVL）
  - **81-82**：CHRD / VOIC（和弦模式）
  - **83-90**：鼓 8 件套音量（KICK/SNARE/CLAP/HATCL/HATOP/TOM/RIM/BELL）
  - **91-98**：ANALOG EDIT（WAVE/DTN/MIX/NOIS/CUT/RES/DRV/KTR）

### 修复（1.1.5.1 实测校准）
- **ANALOG EDIT 从 83-90 移到 91-98**：83-90 已变为鼓 8 件套音量，
  旧版按 83-90 写 ANALOG 参数会错位。
- **STEP_GET / TRACK_STEP 回复尾部多 1 字节**（实测 = 1）：
  位于 chance 之后；发送参数不变（仍 14 参），解析时忽略尾字节即可。
- **INFO pcount 从 91 → 99**，**pe0 从 83 → 91**（+8 预设）。
- **INFO trailer 从 18B → 30B**：前 14B 相同，第 15B 起扩展；
  `chainRows`/`uiCaps` 判定逻辑不变。

### 变更
- `SKILL.md` version: 1.0.0 → 1.1.0
- 固件版本要求更新为 `1.1.5.1`

### 已知限制
- 仅支持 Windows
- 多行链 `repeat>1` 不稳
- Felucca 固件为 Beta，有变砖风险

---

## [1.0.0] - 2026-10-06

### 新增
- 直连 SysEx 方案（ctypes + winmm.dll）
- `scripts/felucca_link.py`：直连核心库
- `scripts/felucca_cli.py` / `felucca_arrange.py` / `felucca_arrange_ab.py` / `play_slot.py` / `play_chain.py`
- `SKILL.md` / `README.md` / `CHANGELOG.md` / `LICENSE`
- `reference/sysx-map.md`：DX7 标准参数映射
- `examples/arrangement-recipes.md`：编曲配方

### 已知限制
- 仅支持 Windows
- 多行链 `repeat>1` 不稳
- Felucca 固件为 Beta，有变砖风险

---

## 版本号规则

从 `1.0.0` 起，严格遵循 [Semantic Versioning](https://semver.org/)：

| 变更类型 | 版本号变化 | 示例 |
|---|---|---|
| **破坏性变更** | `MAJOR` | 协议不兼容、脚本接口重构 |
| **新增功能** | `MINOR` | 新引擎、新参数、新脚本 |
| **修复/校准** | `PATCH` | 解析校准、bug fix、文档纠正 |

### 每次改进的流程
1. **改代码/文档**
2. **在 `CHANGELOG.md` 的 `[Unreleased]` 段新增条目**
3. **发版时把 `[Unreleased]` 改名为 `[X.Y.Z] - YYYY-MM-DD`**
4. **同步更新 `SKILL.md` 的 `version` 字段和 `README.md` 顶部的 badge**