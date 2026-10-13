# Felucca SysEx 参数映射

> 来源：2026-10-12 实机验证 · 固件 FELUCCA **v1.5**
> （v1.1.5.1 版为 99 参数 / pe0=91，已过时）

## 帧格式

```
F0 7D 46 4C <cmd & 0x7F> <args...> F7
```

## v14 编码

```
v14enc(v) = v + 8192 → [lo & 0x7F, (lo >> 7) & 0x7F]
v14dec(lo, hi) = (lo + (hi << 7)) - 8192
```

## 命令枚举

| 命令 | 值 | 说明 |
|---|---|---|
| INFO | 1 | 设备信息 |
| GET / SET | 2 / 3 | 全局参数读 / 写（SET scope=1） |
| DESC | 5 | 参数描述（scope 0=轨道 / 1=全局） |
| STEP_GET / STEP_SET | 6 / 7 | 步进读 / 写 |
| PRESET | 8 | 应用引擎+预设 |
| PROJECT | 9 | 项目槽位：op 0=load 1=save 2=query |
| WATCH | 22 | 推送开关 |
| TRACK | 27 | 选择当前轨；空参返回全部 4 轨信息 |
| TRACK_DUMP | 29 | 全参数 dump（v1.5 起有效） |
| TRACK_STEP | 30 | 轨内步进读写 |
| TRACK_PARAM | 31 | 轨内参数读写 |
| SONG | 33 | 播放链 |

## INFO 回复结构（v1.5 实测）

```
version(\0串) nengines(1B) pcount(1B) gcount(1B) nstep(1B) pe0(1B)
engines×nengines(\0串) ntrk(1B) trailer[...]
```

**实测**：`version='FELUCCA v1.5'`, nengines=14, **pcount=111**, gcount=27,
nstep=64, **pe0=103**, ntrk=4。

**trailer**（30B）判定逻辑：
- `chainRows` = `trailer[0]===16 ? 16 : 0`
- `uiCaps` = `(trailer[0]==16 && trailer[1]==0x55 && trailer[2]==1) ? trailer[3]&15 : 0`

**版本演进对照**：

| 版本 | pcount | pe0 | trailer |
|---|---|---|---|
| v1.0.2 | 91 | 83 | 18B |
| v1.1.5.1 | 99 | 91 | 30B |
| **v1.5** | **111** | **103** | 30B |

## TRACK_STEP 写步布局

```
写步(TRACK_STEP 30)：[30, tr, i, n, note0..3, time, flags, vel, hit, acc, hi, chance]
读步(STEP_GET 6)：  [6, i]     ← 只带步索引！先发 TRACK [tr] 选轨
回复(STEP_GET)：    [i, n, note0..3, time, flags, vel, hit, acc, hi, chance, 尾字节]
```

- `time`：0=NOTE 1=TIE 2=REST
- `flags`：1=accent 2=slide
- **v1.5 起回复尾部多 1 字节**（实测=1），位于 chance 之后；**发送参数不变**（仍 14 参）
- 实测：`[0,1,64,0,0,0,0,0,100,0,0,0,100,1]`

## 轨道参数（111 个，scope 0，id 0-110）

### 0-40（基础区）

| ID | 名称 | 说明 |
|---|---|---|
| 0 | LVL | 轨道电平（0-127，def 104）|
| 1-4 | ATK/DEC/SUS/REL | 包络 |
| 5 | FLT | 滤波器（**-64~63**，带符号）|
| 6 | PIT | 音高 |
| 7 | SHP | 形状 |
| 8 | FX | 效果 |
| 9-12 | LFO1 RATE/WAVE/PHS/FADE | LFO1 |
| 13-16 | LFO2 PIT/FLT/SHP/AMP | LFO2 |
| 17-24 | ARP MODE/RATE/OCT/GATE/SWG/PROB/HOLD/ORD | 琶音 |
| 25-28 | SCL ROOT/SCL/QNT/TRN | 音阶 |
| **29** | **LEN** | 步长（1-64）|
| **30** | **DIV** | 分度（10 枚举，见 §枚举）|
| 31 | SWG | 轨内摇摆（0-100）|
| 32 | GATE | 门限（1-127）|
| 33-40 | DST/CHO/DLY/REV/VCE/GLD/PAN/MUTE | 混音（PAN **-64~63**）|

### 41-48（v1.1.5.1 新增）

| ID | 名称 |
|---|---|
| 41 | GLMOD |
| 42 | PRIO |
| 43 | ALLOC |
| 44 | DTUNE |
| 45 | SLCR |
| 46-48 | MSEQ PAT / RATE / DEPTH |

### 49-60（调制矩阵 4 组）

| 组 | SRC | DST | AMT |
|---|---|---|---|
| 1 | 49 | 50 | 51 |
| 2 | 52 | 53 | 54 |
| 3 | 55 | 56 | 57 |
| 4 | 58 | 59 | 60 |

### 61-80（4×ENV）

| 组 | ATK | DEC | SUS | REL | LVL |
|---|---|---|---|---|---|
| ENV1 | 61 | 62 | 63 | 64 | 65 |
| ENV2 | 66 | 67 | 68 | 69 | 70 |
| ENV3 | 71 | 72 | 73 | 74 | 75 |
| ENV4 | 76 | 77 | 78 | 79 | 80 |

### 81-90（和弦 + 鼓音量）

| ID | 名称 | 说明 |
|---|---|---|
| 81 | CHRD | 和弦模式 |
| 82 | VOIC | 和弦声位 |
| **83-90** | **鼓 8 件套音量** | KICK=83 SNARE=84 CLAP=85 HATCL=86 HATOP=87 TOM=88 RIM=89 BELL=90 |

### 91-100（⚠️ v1.5：SYNC + INSERT 区）

| ID | 名称 | 说明 |
|---|---|---|
| 91 | SYNC | 振荡器同步 |
| 92 | TRIG | 触发模式 |
| 93 | POL | 极性 |
| 94 | QNTZ | 量化 |
| 95 | SPRD | 立体声展宽 |
| 96 | INSRT | INSERT 效果总开关 |
| 97 | INS A | INSERT 参数 A |
| 98 | INS B | INSERT 参数 B |
| 99 | INS C | INSERT 参数 C |
| 100 | MIX | INSERT 干湿比 |

> ⚠️ **v1.1.5.1 时代的 91-98（WAVE/DTN/MIX/NOIS/CUT/RES/DRV/KTR）已作废**，
> v1.5 移至 101-110。按旧表写 `CUT=95` 会写进 SPRD（音色变宽）、`RES=96` 会写进 INSRT（无共鸣）。

### 101-110（⚠️ v1.5：ANALOG EDIT 新位置）

| ID | 名称 | 说明 |
|---|---|---|
| **101** | **TYPE** | 滤波器类型（LP/BP/HP）|
| 102 | ESYNC | 包络同步 |
| **103** | **WAVE** | 波形（SAW/SQR/TRI/SIN/PWM/SYNC/SUB）|
| 104 | DTN | 失谐 |
| 105 | MIX | 混合 |
| 106 | NOIS | 噪声 |
| **107** | **CUT** | 截止频率 |
| **108** | **RES** | 共振 |
| 109 | DRV | 驱动 |
| 110 | KTR | 键跟踪 |

## 全局参数（27 个，scope 1，id 0-26）

| ID | 名称 | 说明 |
|---|---|---|
| 0 | BPM | 40-240, def120 |
| 1 | SWG | 摇摆（0-100）|
| 2 | CLK | 时钟（0=INT 1=USB 2=TRS）|
| 3 | TUNE | 调音（**-50~50**，带符号）|
| 4 | TIME(DIV) | 分度（0-7，枚举见下）|
| 5-9 | DLY FDBK/COLR/MIX/SIZE/DAMP | 延迟 |
| 10-11 | CRT/CDP | 滤波 |
| 12-14 | MIDI/SYNC/ROUT | MIDI |
| 15-19 | CPU/SLOT(1-4)/NAME/LOAD/SAVE | 系统 |
| 20 | ENG | 当前轨引擎 |
| 21-24 | SET/CLRSQ/INIT/TYPE(REV) | 设置 |

## 枚举

### DIV / TIME（10 个）

```
0=1/4  1=1/8  2=1/16  3=1/32  4=8T  5=16T  6=1/2  7=1/1
8=2BAR  9=4BAR    ← v1.5 新增
```

### 引擎（ENG，id 20）

```
ANALOG=0  ''=1  PHASE=2  LOFI=3  SAMPLE=4  VOICE=5  TRIO=6
WHEEL=7   GRAIN=8  PHYS=9  DRUM=10  NOISE=11  FM6=12  SLICE=13
```

### ANALOG 波形（WAVE，id 103）

```
SAW / SQR / TRI / SIN / PWM / SYNC / SUB
```
（v1.1.5.1 只有前 5 个；SYNC / SUB 为 v1.5 新增）

### ANALOG 滤波器类型（TYPE，id 101）

```
LP / BP / HP
```

### ANALOG 预设（NAMES 实测）

```
1=SOFT PAD   5=SINE KEY   7=SUB BASS   8=PLUCK   9=BRASS   11=STRINGS
```
（完整列表以 `NAMES` 命令读回为准）

### DRUM 引擎预设（v1.5 实测仅 3 个）

```
0=DRUM KIT  1=KIT  2=HIT
```

### 和弦模式 CHRD（id 81）

```
OFF / DIA3 / DIA7 / MAJ / MIN / DOM7 / MAJ7 / MIN7
```

### 和弦声位 VOIC（id 82）

```
CLOSE / OPEN / INV1 / INV2 / +OCT
```

### MSEQ RATE（id 47）

```
0=1/8  1=1/16  2=1/32  3=8T  4=16T  5=32T
```

## 鼓位掩码（8 鼓位 lane）

```
bit0=KICK(GM36)   bit1=SNARE(38)   bit2=CLAP(39)   bit3=HATCL(42)
bit4=HATOP(46)    bit5=TOM(45)     bit6=RIM(37)    bit7=BELL(56)

编码：hitsEnc(hit, acc) = [hit & 0x7F, acc & 0x7F, ((hit>>7)&1)|(((acc>>7)&1)<<1)]
解码：hit = h | ((x&1)<<7)；acc = (c | ((x&2)<<6)) & hit   // acc ⊆ hit
```

非鼓轨：hit=acc=0。

## TRACK_DUMP 解析（v1.5）

```
回复 body = [tr, engine, preset, (hi, lo) × 111]
```

- 头 3B = `[tr, engine, preset]` 单字节
- 参数值 = `(hi << 7) | lo`——⚠️ **高字节在前**（与 SLOOP 的 `(lo, hi)` 相反！）
- 111 个参数（id 0-110）
- v1.5 之前 TRACK_DUMP 不回复；**v1.5 起有效**

## TRACK 查询（v1.5）

`TRACK []`（命令 27 空参）返回全部 4 轨 engine/preset/LVL：

```
[当前轨, 轨数, tr0_eng, tr0_pre, tr0_LVL_lo, tr0_LVL_hi, ?, ?, tr1_eng, tr1_pre, tr1_LVL, ...]
```

**实测**：

```
[3, 4,
 0, 11, 80, 64, 0, 0,    # tr0 = ANALOG / STRINGS(11) / LVL 80
 0, 1, 86, 64, 0, 0,     # tr1 = ANALOG / SOFT PAD(1) / LVL 86
 0, 7, 78, 64, 0, 0,     # tr2 = ANALOG / SUB BASS(7) / LVL 78
 10, 0, 88, 64, 0, 0]    # tr3 = DRUM / DRUM KIT(0) / LVL 88
```

**用途**：核对引擎/预设的权威手段（不必逐轨 TRACK_DUMP）。

## SONG 播放

```
op=0 查询状态        SONG [0]
op=1 设置播放行      SONG [1, 行数, 槽位, 次数, 槽位, 次数, ...]   // 长度 = 2 + 2×行数
op=2 真正开始播放    SONG [2]
op=3 停止            SONG [3]
回复 [op, rc, count, playing, row, remaining, ...rows: slot, repeat]
```

- **只发 op=1 不出声！必须再发 op=2 才播放**
- 播放触发判据：op=2 后轮询 `SONG [0]`，回复第 4 字节 `playing=1`
- **已知坑**：多行链每行 repeat>1 不稳；单遍链（repeat=1）稳定
- 循环播放 = 重发 `SONG [2]`

## TIE 语义

- `time=1` 延续**最近一个 NOTE 起始步**的音符
- 整段全 TIE 无 NOTE 起始 = 静音
- 写长音 = 首步 `time=0` + 后续步 `time=1`

## 关键坑（v1.5 实测校准）

1. **命令号不要重复带**：`link.request(CMD_TRACK, [0])` 不是 `[27, 0]`
2. **写步仍 14 参**：v1.5 回复多 1 字节，但发送参数不变
3. **TIE 需 NOTE 起始**
4. **`STEP_GET` 请求是 `[i]` 不是 `[tr, i]`**（多带 tr → NO REPLY）
5. **⚠️ ANALOG EDIT 在 101-110**（旧 91-98 已变为 SYNC/INSERT 区）
6. **INFO pcount=111 / pe0=103**，判定逻辑不变
7. **DIV 枚举 10 个**（v1.5 新增 2BAR/4BAR）
8. **ANALOG WAVE 枚举 7 个**（v1.5 新增 SYNC/SUB）
9. **TRACK_DUMP(29) v1.5 起有效**，格式 `[tr, engine, preset, (hi,lo)×111]`（高字节在前）
10. **TRACK [] 空参返回全部 4 轨信息**（v1.5 新发现）
11. **带符号参数**：FLT(-64~63) / TUNE(-50~50) / PAN(-64~63)，写 0-127 会出错
12. **SWG 范围是 0-100**，不是 0-127
13. **LEN 范围是 1-64**（不是 0 或 65+）
14. **GATE 范围是 1-127**（0 = 无声）
15. **winmm 回调必须 5 参数**
16. **`close()` 不调用 `midiInReset`**（避免死锁）

## 设备名匹配（v1.5）

系统可能有多台 "Felucca" 命名设备（Windows 会加 `2 - ` / `3 - ` 前缀）。

- **端口名后缀 `Felucca`** 是固件 USB 描述符所写，**不可由软件修改**
- **索引由系统按插拔顺序动态分配**，不可写死
- 匹配策略：
  1. 按名称关键字匹配（默认 `felucca`）
  2. 多候选时**探测每台固件**：跳过 SLOOP（`FELUCCA SLOOP`），选非 SLOOP 的 Felucca
  3. 支持环境变量 `FELUCCA_MIDI_NAME` 精确指定（如 `"3 - Felucca"`）

**实测多设备快照**（2026-10-12）：

```
outs: [(0,'Microsoft GS Wavetable Synth'), (1,'Volt 276'), (2,'X0X FM-1'), (3,'2 - Felucca'), (4,'3 - Felucca')]
ins:  [(0,'Volt 276'), (1,'X0X FM-1'), (2,'2 - Felucca'), (3,'3 - Felucca')]
# 2 - Felucca = SLOOP 2.5（无关）；3 - Felucca = FELUCCA v1.5（我们的设备）
```