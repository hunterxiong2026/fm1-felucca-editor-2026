---
name: felucca-editor
version: 1.0.0
author: your-name
license: MIT
description: >
  通过直连 SysEx（ctypes + winmm）操作 M-VAVE FM-1 的 Felucca 固件，
  实现音色参数编辑、多轨编曲、项目槽位管理与 SONG 播放链。
  网页/Web MIDI 方案已退役，当前使用直连协议。
keywords:
  - fm1
  - felucca
  - m-vave
  - sysex
  - winmm
  - ctypes
  - synthesizer
  - music-production
  - arrangement
categories:
  - music
  - automation
  - hardware-integration
triggers:
  - "用 Felucca 编一段"
  - "调整 FM-1 音色"
  - "写一段鼓点/贝斯/旋律"
  - "存到槽位"
  - "播放槽位 A/B"
requirements:
  - name: m-vave-fm1
    type: hardware
    optional: false
  - name: felucca-firmware
    type: firmware
    version: "v1.0.2"
    optional: false
  - name: python
    type: runtime
    version: "3.10+"
    optional: false
  - name: windows
    type: platform
    optional: false
platforms:
  - windows
---

# Felucca Editor Skill

## 概述
通过直连 SysEx 协议操控 FM-1 上的 Felucca 固件。相比已退役的 Web MIDI 方案，
直连写入快 7-8 倍（单步 RTT ≈0.12s），无挂起、无回读竞态。

## 何时使用
- 用户要求写一段编曲（旋律/贝斯/和声/鼓）
- 用户要求修改音色参数（滤波器、包络、LFO、琶音等）
- 用户要求存/读槽位、播放 SONG 链
- 用户要求验证设备状态（dump 当前工作区）

## 前置条件
1. **独立 venv**：`scripts/venv/`，绝不装任何包进系统
2. **FM-1 空闲**：直连前必须关闭浏览器/任何 Web MIDI 会话（设备输入独占）
3. **设备名**：MIDI 设备名为 `Felucca`（输出 idx=1 / 输入 idx=0）
4. **固件版本**：FELUCCA v1.0.2（其他固件协议可能不同）

## 脚本清单

| 脚本 | 作用 |
|---|---|
| `felucca_link.py` | 直连核心库（设备枚举 / open / send / req / INFO·DESC·STEP 解析） |
| `felucca_cli.py` | 命令行工具：`info` `desc` `readstep` `wtest` `dump` `restore` `readparam` `setparam` `play` `stop` `qsong` |
| `felucca_arrange.py` | 单槽一键：读 JSON → 写 4 轨 → 设 BPM → 存槽 → 播放 |
| `felucca_arrange_ab.py` | 双槽链一键：写 A→存 A→写 B→存 B→SONG 链→播放 |
| `play_slot.py` | 仅播放单个已存槽位 |
| `play_chain.py` | 仅播放多槽链 |

## 协议核心

### 帧格式
```
F0 7D 46 4C <cmd & 0x7F> <args...> F7
```
HDR = `7D 46 4C`。设备回复同帧头。

### v14 编码（参数值）
```
v14enc(v) = v + 8192 → [lo & 0x7F, (lo >> 7) & 0x7F]
v14dec(lo, hi) = (lo + (hi << 7)) - 8192
```
例：64 → [64, 64]；88 → [8, 72]；240 → [112, 65]。

### 命令枚举
| 命令 | 值 | 说明 |
|---|---|---|
| INFO | 1 | 设备信息 |
| GET / SET | 2 / 3 | 全局参数读 / 写（SET scope=1） |
| DESC | 5 | 参数描述（scope 0=轨道 / 1=全局） |
| STEP_GET / STEP_SET | 6 / 7 | 步进读 / 写 |
| PRESET | 8 | 应用引擎+预设 |
| PROJECT | 9 | 项目槽位：op 0=load 1=save 2=query |
| WATCH | 22 | 推送开关 |
| TRACK | 27 | 选择当前轨 |
| TRACK_STEP | 30 | 轨内步进读写（写步主命令） |
| TRACK_PARAM | 31 | 轨内参数读写 |
| SONG | 33 | 播放链 |

### TRACK_STEP 写步布局
```
写步(TRACK_STEP 30)：[30, tr, i, n, note0..3, time, flags, vel, hit, acc, hi, chance]
读步(STEP_GET 6)：  [6, i]     ← 只带步索引！先发 TRACK [tr] 选轨
回复(STEP_GET)：    [i, n, note0..3, time, flags, vel, hit, acc, hi, chance]
```
- `tr`=轨道 0-3；`i`=步索引 0-63；`n`=音符数 0-4
- `time`：0=NOTE 1=TIE 2=REST
- `flags`：1=accent 2=slide
- `vel`=力度 0-127；`chance`=概率 0-100
- **陷阱：STEP_GET 请求是 `[i]` 不是 `[tr, i]`**（多带 tr 会 NO REPLY）

### hit/acc 位掩码（8 鼓位 lane）
```
bit0=KICK(36) bit1=SNARE(38) bit2=CLAP(39) bit3=HATCL(42)
bit4=HATOP(46) bit5=TOM(45) bit6=RIM(37) bit7=BELL(56)

编码：hitsEnc(hit, acc) = [hit & 0x7F, acc & 0x7F, ((hit>>7)&1)|(((acc>>7)&1)<<1)]
解码：hit = h | ((x&1)<<7)；acc = (c | ((x&2)<<6)) & hit   // acc ⊆ hit
```
非鼓轨：hit=acc=0（写 [0,0,0]）。

## 参数 ID

### 轨道参数（TRACK_PARAM）
```
LVL=0  ATK=1  DEC=2  SUS=3  REL=4  FLT=5  PIT=6  SHP=7  FX=8
LFO1: RATE=9 WAVE=10 PHS=11 FADE=12
LFO2: PIT=13 FLT=14 SHP=15 AMP=16
ARP:  MODE=17 RATE=18 OCT=19 GATE=20 SWG=21 PROB=22 HOLD=23 ORD=24
SCL:  ROOT=25 SCL=26 QNT=27 TRN=28
LEN=29  DIV=30  SWG=31  GATE=32
DST=33  CHO=34  DLY=35  REV=36
VCE=37  GLD=38  PAN=39  MUTE=40
DTUNE=44  SLCR=45
ANALOG EDIT: WAVE=83 DTN=84 MIX=85 NOIS=86 CUT=87 RES=88 DRV=89 KTR=90
```

### 全局参数（SET scope=1）
```
BPM=0(40-240,def120)  SWG=1  CLK=2  TUNE=3  TIME(DIV)=4
DLY: FDBK=5 COLR=6 MIX=7 SIZE=8 DAMP=9
CRT=10  CDP=11  MIDI=12  SYNC=13  ROUT=14
CPU=15  SLOT=16  NAME=17  LOAD=18  SAVE=19
ENG=20  SET=21  CLRSQ=22  INIT=23  TYPE(REV)=24
```

### 枚举
```
DIV/TIME: 0=1/4  1=1/8  2=1/16  3=1/32  4=8T  5=16T  6=1/2  7=1/1
ENG: ANALOG=0 ''=1 PHASE=2 LOFI=3 SAMPLE=4 VOICE=5 TRIO=6 WHEEL=7
     GRAIN=8 PHYS=9 DRUM=10 NOISE=11 FM6=12 SLICE=13
ANALOG 预设: 1=SOFT PAD  5=SINE KEY  7=SUB BASS  9=BRASS
```

## SONG 播放（关键修正）

```
op=0 查询状态        SONG [0]
op=1 设置播放行      SONG [1, 行数, 槽位, 次数, 槽位, 次数, ...]   // 长度 = 2 + 2×行数
op=2 真正开始播放    SONG [2]
op=3 停止            SONG [3]
回复 [op, rc, count, playing, row, remaining, ...rows: slot, repeat]
```
- **只发 op=1 是配置行，不出声！必须再发 op=2 才播放**
- 播放触发判据：op=2 后轮询 `SONG [0]`，回复第 4 字节 `playing=1`
- **已知坑**：多行链每行 repeat>1 不稳；单遍链（repeat=1）稳定
- 循环播放 = 重发 `SONG [2]`

## 操控流程

### 单槽完整编曲（≤64 步）
```
python build_xx.py                                       # 生成 arrangement.json
python felucca_arrange.py <slot> <bpm> <repeat>          # 写→存→播
```

### 双槽链编曲（>64 步，如 12 小节布鲁斯）
```
python build_xx.py
python felucca_arrange_ab.py <jsonA> <slotA> <jsonB> <slotB> <bpm> <repA> <repB>
```

### 仅播放 / 停 / 重播
```
python play_slot.py <slot> <repeat>
python play_chain.py <slot1> <rep1> <slot2> <rep2>
python felucca_cli.py stop
python felucca_cli.py qsong
```

### 播放验收
- 以**实际听声**为准（`playing=1` 只证明"已触发"）
- 链完整播放验证：轮询直到 `playing=0`

## 直连三坑（勿重踩）
1. **MIDIHDR 的 `dwUser`/`reserved` 字段必须是 8 字节指针**（误写 4 字节 → SysEx 发送永不 DONE）
2. **`MIM_LONGDATA = 0x3C4`**（误写 0x3C6 → 回复被静默丢弃）
3. **winmm 所有函数需显式声明 argtypes**（否则 x64 指针截断）
4. **`parse_info` 版本串后需 pop 掉 0x00**（否则全字段错位）

## INFO 解析要点（实测校准）

```
version(\0串) nengines(1B) pcount(1B) gcount(1B) nstep(1B) pe0(1B)
engines×nengines(\0串) ntrk(1B) trailer[...]
```
- `ntrk` 是解析流 pop 出来的**独立 1 字节**，**不在 trailer 数组内**
- `chainRows` 判定：`trailer[0] === 16` → chainRows=16
- `uiCaps` 判定：`trailer[0]==16 && trailer[1]==0x55 && trailer[2]==1` → `uiCaps = trailer[3] & 15`
- 实测 trailer：`[16, 85, 1, 9, 77, 1, 64, 1, 66, 1, ...]` → chainRows=16, uiCaps=9

## 用户硬约束
1. **独立 venv，绝不装任何包进系统**
2. MIDI 导出目录 `J:\MyMusic\midi`（仅用户正式要求导出时才写）
3. 播放验收以实际听声为准
4. 修改音色/编曲后直接改文件与设备，不需要输出提示词正文
5. 回复先给一句话总结

## 编曲迭代快捷路径
- 改速度/摇摆：改 `build_*.py` 的 BPM/SWG 参数或 `felucca_arrange*.py` 命令行参数后重跑
- 改和弦/旋律/琶音：改 `build_*.py` 的 midi 数组 → 重跑 build → 重跑 arrange
- 验证设备真实状态：`felucca_cli.py dump 64`

## 参考
- `reference/sysx-map.md`：DX7 标准参数映射
- `examples/arrangement-recipes.md`：编曲配方（爵士、布鲁斯、雨后庭院）

> 注：本地测试核心文档不随 Skill 发布，保留在开发目录。

## 已知限制
- 多行链 `repeat>1` 不稳（单遍链稳定）
- `STEP_GET` 参数布局在部分固件上需重验
- 仅支持 Windows（依赖 winmm.dll）
- Felucca 固件为 Beta，刷入有变砖风险