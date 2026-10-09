---
name: felucca-editor
version: 1.1.0
author: hunterxiong2026
license: MIT
description: "通过直连 SysEx（ctypes + winmm）操作 M-VAVE FM-1 的 Felucca 固件，实现音色参数编辑、多轨编曲、项目槽位管理与 SONG 播放链。"
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
    version: "1.1.5.1"
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
- 用户要求修改音色参数（滤波器、包络、LFO、琶音、调制矩阵等）
- 用户要求存/读槽位、播放 SONG 链
- 用户要求验证设备状态（dump 当前工作区）

## 前置条件
1. **独立 venv**：`scripts/venv/`，绝不装任何包进系统
2. **FM-1 空闲**：直连前必须关闭浏览器/任何 Web MIDI 会话（设备输入独占）
3. **设备名**：MIDI 设备名为 `Felucca`（输出 idx=1 / 输入 idx=0）
4. **固件版本**：FELUCCA **1.1.5.1**（**99 轨道参数 / 27 全局参数**）

## 脚本清单

| 脚本 | 作用 |
|---|---|
| `felucca_link.py` | 直连核心库（设备枚举 / open / send / req / INFO·DESC·STEP·SONG 解析） |
| `felucca_cli.py` | 命令行工具 |
| `felucca_arrange.py` | 单槽一键：读 JSON → 写 4 轨 → 设 BPM → 存槽 → SONG 播放 |
| `felucca_arrange_ab.py` | 双槽链一键 |
| `play_slot.py` / `play_chain.py` | 仅播放脚本 |

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
回复(STEP_GET)：    [i, n, note0..3, time, flags, vel, hit, acc, hi, chance, ...]
```
- `tr`=轨道 0-3；`i`=步索引 0-63；`n`=音符数 0-4
- `time`：0=NOTE 1=TIE 2=REST
- `flags`：1=accent 2=slide
- `vel`=力度 0-127；`chance`=概率 0-100
- **陷阱：STEP_GET 请求是 `[i]` 不是 `[tr, i]`**（多带 tr 会 NO REPLY）
- **v1.1.5.1 新变化**：STEP_GET / TRACK_STEP 回复**尾部多一个未知字节（实测 = 1）**，
  位于 chance 之后；**发送参数个数不变**（仍是 14 参），解析时忽略尾字节即可。
  实测：写 NOTE E4 → 读回 `[0,1,64,0,0,0,0,0,100,0,0,0,100,1]`（尾 1 为新增字段）。

### hit/acc 位掩码（8 鼓位 lane）
```
bit0=KICK(36) bit1=SNARE(38) bit2=CLAP(39) bit3=HATCL(42)
bit4=HATOP(46) bit5=TOM(45) bit6=RIM(37) bit7=BELL(56)

编码：hitsEnc(hit, acc) = [hit & 0x7F, acc & 0x7F, ((hit>>7)&1)|(((acc>>7)&1)<<1)]
解码：hit = h | ((x&1)<<7)；acc = (c | ((x&2)<<6)) & hit   // acc ⊆ hit
```
非鼓轨：hit=acc=0（写 [0,0,0]）。

## 参数 ID（v1.1.5.1，99 轨道参数）

### 轨道参数（TRACK_PARAM，scope 0，id 0-98）

| 区段 | ID | 参数 |
|---|---|---|
| 基础 | 0-8 | LVL=0 ATK=1 DEC=2 SUS=3 REL=4 FLT=5 PIT=6 SHP=7 FX=8 |
| LFO1 | 9-12 | RATE=9 WAVE=10 PHS=11 FADE=12 |
| LFO2 | 13-16 | PIT=13 FLT=14 SHP=15 AMP=16 |
| ARP | 17-24 | MODE=17 RATE=18 OCT=19 GATE=20 SWG=21 PROB=22 HOLD=23 ORD=24 |
| SCL | 25-28 | ROOT=25 SCL=26 QNT=27 TRN=28 |
| 步进 | 29-32 | **LEN=29 DIV=30 SWG=31 GATE=32** |
| 混音 | 33-40 | DST=33 CHO=34 DLY=35 REV=36 VCE=37 GLD=38 PAN=39 MUTE=40 |
| 新增 41-45 | 41-45 | GLMOD=41 PRIO=42 ALLOC=43 DTUNE=44 SLCR=45 |
| MSEQ | 46-48 | PAT=46(1-16) RATE=47 DEPTH=48(0-127) |
| 调制矩阵 | 49-60 | SRC1=49 DST1=50 AMT1=51 SRC2=52 DST2=53 AMT2=54 SRC3=55 DST3=56 AMT3=57 SRC4=58 DST4=59 AMT4=60 |
| 4×ENV | 61-80 | ENV1: ATK=61 DEC=62 SUS=63 REL=64 LVL=65；ENV2: 66-70；ENV3: 71-75；ENV4: 76-80 |
| 和弦 | 81-82 | CHRD=81 VOIC=82 |
| **鼓 8 件套音量** | 83-90 | **KICK=83 SNARE=84 CLAP=85 HATCL=86 HATOP=87 TOM=88 RIM=89 BELL=90** |
| ANALOG EDIT | 91-98 | **WAVE=91 DTN=92 MIX=93 NOIS=94 CUT=95 RES=96 DRV=97 KTR=98** |

> **⚠️ v1.1.5.1 关键变化**：ANALOG EDIT 从 83-90 **移到 91-98**；83-90 变为**鼓 8 件套音量**；
> 新增 41-82（调制/包络/和弦模式）；LEN=29 DIV=30 等旧 ID **不变**。

### 全局参数（SET scope=1，id 0-24，与 1.0.2 一致）
```
BPM=0(40-240,def120)  SWG=1  CLK=2  TUNE=3  TIME(DIV)=4
DLY: FDBK=5 COLR=6 MIX=7 SIZE=8 DAMP=9
CRT=10  CDP=11  MIDI=12  SYNC=13  ROUT=14
CPU=15  SLOT=16(1-4)  NAME=17  LOAD=18  SAVE=19
ENG=20  SET=21  CLRSQ=22  INIT=23  TYPE(REV)=24
```

### 枚举
```
DIV/TIME: 0=1/4  1=1/8  2=1/16  3=1/32  4=8T  5=16T  6=1/2  7=1/1
          (RATE=18/47 另含 8T/16T/32T)
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

### 双槽链编曲（>64 步）
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

## INFO 解析要点（v1.1.5.1 实测校准）

```
version(\0串) nengines(1B) pcount(1B) gcount(1B) nstep(1B) pe0(1B)
engines×nengines(\0串) ntrk(1B) trailer[...]
```
- `ntrk` 是解析流 pop 出来的**独立 1 字节**，**不在 trailer 数组内**
- `chainRows` 判定：`trailer[0] === 16` → chainRows=16
- `uiCaps` 判定：`trailer[0]==16 && trailer[1]==0x55 && trailer[2]==1` → `uiCaps = trailer[3] & 15`
- **v1.0.2 trailer**（18B）：`[16,85,1,9,77,1,64,1,66,1,3,70,1,8,27,83,1,3]`
- **v1.1.5.1 trailer**（30B）：前 14B 相同，**第 15B 起扩展**
  `[16,85,1,9,77,1,64,1,66,1,3,70,1,8,0,83,1,3,80,1,3,78,1,18,82,1,4,76,1,1]`
- **固件版本差异**：v1.0.2 `pcount=91 pe0=83`；**v1.1.5.1 `pcount=99 pe0=91`**（+8）
- INFO 结构/判定不变，**仅 trailer 变长**；解析代码无需改动

## 直连三坑（勿重踩）
1. **MIDIHDR 的 `dwUser`/`reserved` 字段必须是 8 字节指针**
2. **`MIM_LONGDATA = 0x3C4`**（误写 0x3C6 → 回复被静默丢弃）
3. **winmm 所有函数需显式声明 argtypes**
4. **winmm 回调必须是 5 参数**（`hMidiIn, wMsg, dwInstance, dwParam1, dwParam2`）

## 用户硬约束
1. **独立 venv，绝不装任何包进系统**
2. 播放验收以实际听声为准
3. 修改音色/编曲后直接改文件与设备，不需要输出提示词正文
4. 回复先给一句话总结

## 参考
- `reference/sysx-map.md`：DX7 标准参数映射 + Felucca 扩展参数

## 已知限制
- 仅支持 Windows（依赖 winmm.dll）
- 多行链 `repeat>1` 不稳（单遍链稳定）
- Felucca 固件为 Beta，刷入有变砖风险