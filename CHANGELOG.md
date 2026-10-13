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

## [1.2.0] - 2026-10-10

### 变更（结构重组）
- `SKILL.md` 精简为入口文档，移除协议/参数细节
- 新增 `reference/protocol.md`：帧格式、命令枚举、STEP/SONG 布局、INFO 解析、直连坑
- 新增 `reference/params.md`：99 轨道参数 + 27 全局参数 + 枚举

### 说明
- 文件布局变化，属 MINOR 级别
- 不影响协议帧格式和脚本接口
- 引用索引更新：
  - `reference/protocol.md`（新）
  - `reference/params.md`（新）
  - `reference/sysx-map.md`（不变）
  - `reference/arrangement-metrics.md`（不变）

## [1.1.3] - 2026-10-10

### 修复
- **FLT（轨道 id=5）**：0-127 → **-64~63**（带符号，之前遗漏）
- 补全 4 项待校准参数：
  - **CLK（全局 id=2）**：0-2（枚举 INT/USB/TRS）
  - **TUNE（全局 id=3）**：-50~50（带符号）
  - **PAN（轨道 id=39）**：-64~63（带符号）
  - **RATE（轨道 id=47）**：0-5（枚举 1/8~32T）
- 新增「带符号参数的处理」章节（FLT/TUNE/PAN）
- 新增「参数检查清单」

### 说明
- 本次为 PATCH 级修复，`SKILL.md` 无需改动

## [1.1.2] - 2026-10-10

### 修复
- `reference/arrangement-metrics.md` 参数范围按 `fw_desc_new.txt` 实测校准：
  - **SWG（全局 id=1）**：0-127 → **0-100**
  - **LEN（轨道 id=29）**：0-127 → **1-64**
  - **SWG（轨道 id=31）**：0-127 → **0-100**
  - **GATE（轨道 id=32）**：保持 1-127（原写 0-127，近似可接受）
- 新增「参数校准来源」章节，注明以设备 DESC 实测为准
- 新增「待校准项」列表（CLK / TUNE / PAN / RATE）

### 说明
- 本次为 PATCH 级修复，不影响协议帧格式和脚本接口
- `SKILL.md` 无需改动（参数表只列 ID 和名字，不列范围）

## [1.1.1] - 2026-10-10

### 新增
- `reference/arrangement-metrics.md`：编曲质量指标（硬指标 + 参考方向）
- `SKILL.md` 参考段加该文件引用
- `SKILL.md` version → 1.1.1

### 说明
- 硬指标：音区、协议约束、TIE 语义、参数范围
- 参考方向：结构、律动、配器、织体（可打破）


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