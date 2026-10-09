# Felucca SysEx 参数映射

> 来源：2026-10-09 实机验证 · 固件 FELUCCA **1.1.5.1**
> （1.0.2 文档为 91 参数，已过时）

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
| TRACK | 27 | 选择当前轨 |
| TRACK_STEP | 30 | 轨内步进读写 |
| TRACK_PARAM | 31 | 轨内参数读写 |
| SONG | 33 | 播放链 |

## INFO 回复结构（1.1.5.1 实测）

```
version(\0串) nengines(1B) pcount(1B) gcount(1B) nstep(1B) pe0(1B)
engines×nengines(\0串) ntrk(1B) trailer[...]
```

**实测**：`version='FELUCCA 1.1.5.1'`, nengines=14, **pcount=99**, gcount=27,
nstep=64, **pe0=91**, ntrk=4。

**trailer**（30B）：`[16,85,1,9,77,1,64,1,66,1,3,70,1,8,0,83,1,3,80,1,3,78,1,18,82,1,4,76,1,1]`

- `chainRows` 判定：`trailer[0] === 16` → chainRows=16
- `uiCaps` 判定：`trailer[0]==16 && trailer[1]==0x55 && trailer[2]==1` → `uiCaps = trailer[3] & 15`

**v1.0.2 vs 1.1.5.1**：
- pcount：91 → **99**（+8 预设）
- pe0：83 → **91**
- trailer：18B → **30B**（前 14B 相同，第 15B 起扩展）
- 判定逻辑不变

## TRACK_STEP 写步布局

```
写步(TRACK_STEP 30)：[30, tr, i, n, note0..3, time, flags, vel, hit, acc, hi, chance]
读步(STEP_GET 6)：  [6, i]     ← 只带步索引！先发 TRACK [tr] 选轨
回复(STEP_GET)：    [i, n, note0..3, time, flags, vel, hit, acc, hi, chance, ...]
```

- `time`：0=NOTE 1=TIE 2=REST
- `flags`：1=accent 2=slide
- **v1.1.5.1 新变化**：回复**尾部多 1 字节**（实测 = 1），位于 chance 之后。
  发送参数不变（仍 14 参），解析忽略尾字节。
  实测：`[0,1,64,0,0,0,0,0,100,0,0,0,100,1]`

## 轨道参数（99 个，scope 0，id 0-98）

| 区段 | ID | 参数 |
|---|---|---|
| 基础 | 0-8 | LVL, ATK, DEC, SUS, REL, FLT, PIT, SHP, FX |
| LFO1 | 9-12 | RATE, WAVE(枚举), PHS, FADE |
| LFO2 | 13-16 | PIT, FLT, SHP, AMP |
| ARP | 17-24 | MODE, RATE, OCT, GATE, SWG, PROB, HOLD, ORD |
| SCL | 25-28 | ROOT, SCL, QNT, TRN |
| 步进 | 29-32 | LEN, DIV, SWG, GATE |
| 混音 | 33-40 | DST, CHO, DLY, REV, VCE, GLD, PAN, MUTE |
| 41-45 | 41-45 | GLMOD(RATE/TIME), PRIO(LAST/LOW/HIGH), ALLOC(ROT/REUSE), DTUNE, SLCR(OFF/GATE/STUT) |
| MSEQ | 46-48 | PAT(1-16), RATE(1/8-32T), DEPTH(0-127) |
| 调制矩阵 | 49-60 | SRC1=49 DST1=50 AMT1=51；SRC2=52 DST2=53 AMT2=54；SRC3=55 DST3=56 AMT3=57；SRC4=58 DST4=59 AMT4=60 |
| 4×ENV | 61-80 | ENV1: 61-65；ENV2: 66-70；ENV3: 71-75；ENV4: 76-80（每组 ATK/DEC/SUS/REL/LVL） |
| 和弦 | 81-82 | CHRD(OFF/DIA3/DIA7/MAJ/MIN/DOM7/MAJ7/MIN7), VOIC(CLOSE/OPEN/INV1/INV2/+OCT) |
| **鼓音量** | 83-90 | KICK=83 SNARE=84 CLAP=85 HATCL=86 HATOP=87 TOM=88 RIM=89 BELL=90 |
| ANALOG EDIT | 91-98 | WAVE=91(SAW/SQR/TRI/SIN/PWM) DTN=92 MIX=93 NOIS=94 CUT=95 RES=96 DRV=97 KTR=98 |

## 全局参数（27 个，scope 1，id 0-24）

| ID | 名称 | 说明 |
|---|---|---|
| 0 | BPM | 40-240, def120 |
| 1 | SWG | 摇摆 |
| 2 | CLK | 时钟 |
| 3 | TUNE | 调音 |
| 4 | TIME | 分度 |
| 5-9 | DLY FDBK/COLR/MIX/SIZE/DAMP | 延迟 |
| 10-11 | CRT/CDP | 滤波 |
| 12-14 | MIDI/SYNC/ROUT | MIDI |
| 15-19 | CPU/SLOT(1-4)/NAME/LOAD/SAVE | 系统 |
| 20 | ENG | 当前轨引擎 |
| 21-24 | SET/CLRSQ/INIT/TYPE | 设置 |

## 枚举

### DIV/TIME（id 4 / 30）
```
0=1/4  1=1/8  2=1/16  3=1/32  4=8T  5=16T  6=1/2  7=1/1
```
RATE（id 18 / 47）另含 8T/16T/32T。

### 引擎（ENG，id 20）
```
ANALOG=0  ''=1  PHASE=2  LOFI=3  SAMPLE=4  VOICE=5  TRIO=6
WHEEL=7   GRAIN=8  PHYS=9  DRUM=10  NOISE=11  FM6=12  SLICE=13
```

### ANALOG 预设（1.1.5.1，pcount=99）
```
1=SOFT PAD   5=SINE KEY   7=SUB BASS   9=BRASS
```

### 调制矩阵 DST
```
OFF / PITCH / CUT / SHP / AMP / PAN / DIST / CHO / ...
```

### 和弦模式 CHRD
```
OFF / DIA3 / DIA7 / MAJ / MIN / DOM7 / MAJ7 / MIN7
```

### 和弦声位 VOIC
```
CLOSE / OPEN / INV1 / INV2 / +OCT
```

## 鼓位掩码（8 鼓位 lane）

```
bit0=KICK(GM36)   bit1=SNARE(38)   bit2=CLAP(39)   bit3=HATCL(42)
bit4=HATOP(46)    bit5=TOM(45)     bit6=RIM(37)    bit7=BELL(56)

编码：hitsEnc(hit, acc) = [hit & 0x7F, acc & 0x7F, ((hit>>7)&1)|(((acc>>7)&1)<<1)]
解码：hit = h | ((x&1)<<7)；acc = (c | ((x&2)<<6)) & hit   // acc ⊆ hit
```
非鼓轨：hit=acc=0。

## SONG 播放

```
op=0 查询状态        SONG [0]
op=1 设置播放行      SONG [1, 行数, 槽位, 次数, 槽位, 次数, ...]   // 长度 = 2 + 2×行数
op=2 真正开始播放    SONG [2]
op=3 停止            SONG [3]
回复 [op, rc, count, playing, row, remaining, ...rows: slot, repeat]
```

- **只发 op=1 不出声！必须再发 op=2 才播放**
- 播放触发判据：op=2 后轮询 `SONG [0]`，第 4 字节 `playing=1`
- 已知坑：多行链 repeat>1 不稳；单遍链稳定

## TIE 语义

- `time=1` 延续**最近一个 NOTE 起始步**的音符
- 整段全 TIE 无 NOTE 起始 = 静音
- 写长音 = 首步 `time=0` + 后续步 `time=1`

## 关键坑（1.1.5.1 实测校准）

1. **命令号不要重复带**：`link.request(CMD_TRACK, [0])` 不是 `[27, 0]`
2. **写步无 chance 之外的扩展字段**：v1.1.5.1 回复多 1 字节，但发送仍 14 参
3. **TIE 需 NOTE 起始**
4. **`STEP_GET` 请求是 `[i]` 不是 `[tr, i]`**
5. **ANALOG EDIT 在 91-98**（1.0.2 的 83-90 已变为鼓音量）
6. **INFO trailer 30B**，判定逻辑不变
7. **`P_KIT` 概念不适用**（Felucca 无独立鼓组参数；鼓走 DRUM 引擎 + 8 件套音量 83-90）
8. **winmm 回调必须 5 参数**
9. **`close()` 不调用 `midiInReset`**（避免死锁）