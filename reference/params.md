# Felucca 参数 ID

> v1.5 实测：**111 轨道参数**（id 0-110）+ 27 全局参数（id 0-26）
> 本文件只记录参数规范，不含客户端代码。

---

## ⚠️ v1.1.5.1 → v1.5 关键变化

| 区段 | v1.1.5.1 | **v1.5** |
|---|---|---|
| 91-100 | WAVE=91 DTN=92 MIX=93 NOIS=94 CUT=95 RES=96 DRV=97 KTR=98 | **SYNC=91 TRIG=92 POL=93 QNTZ=94 SPRD=95 INSRT=96 INS A=97 INS B=98 INS C=99 MIX=100** |
| 101-110 | — | **TYPE=101 ESYNC=102 WAVE=103 DTN=104 MIX=105 NOIS=106 CUT=107 RES=108 DRV=109 KTR=110** |
| pcount | 99 | **111** |
| pe0 | 91 | **103** |
| DIV 枚举 | 8 个 | **10 个**（+2BAR、4BAR） |

**迁移警示**：按旧表写 `CUT=95` → 会写进 `SPRD`（音色错位变宽）；
写 `RES=96` → 会写进 `INSRT`（无共鸣）。
**新脚本必须用新 ID**：`WAVE=103 DTN=104 CUT=107 RES=108 DRV=109 KTR=110`。

---

## 一、轨道参数（TRACK_PARAM，scope 0，id 0-110）

### 0-40（基础区，两版不变）

| ID | 名称 | 说明 |
|---|---|---|
| 0 | LVL | 轨道电平 |
| 1-4 | ATK/DEC/SUS/REL | 包络 |
| 5 | FLT | 滤波器 |
| 6 | PIT | 音高 |
| 7 | SHP | 形状 |
| 8 | FX | 效果 |
| 9-12 | LFO1 RATE/WAVE/PHS/FADE | LFO1 |
| 13-16 | LFO2 PIT/FLT/SHP/AMP | LFO2 |
| 17-24 | ARP MODE/RATE/OCT/GATE/SWG/PROB/HOLD/ORD | 琶音 |
| 25-28 | SCL ROOT/SCL/QNT/TRN | 音阶 |
| **29** | **LEN** | **步长** |
| **30** | **DIV** | **分度（10 个枚举，见 §三）** |
| 31 | SWG | 轨内摇摆 |
| 32 | GATE | 门限 |
| 33-40 | DST/CHO/DLY/REV/VCE/GLD/PAN/MUTE | 混音 |

### 41-48（v1.1.5.1 新增）

| ID | 名称 | 说明 |
|---|---|---|
| 41 | GLMOD | 滑音模式 |
| 42 | PRIO | 优先级 |
| 43 | ALLOC | 分配 |
| 44 | DTUNE | 失谐 |
| 45 | SLCR | 切片器 |
| 46-48 | MSEQ PAT/RATE/DEPTH | 微型音序器 |

### 49-60（调制矩阵，4 组）

| ID | 名称 |
|---|---|
| 49/50/51 | SRC1 / DST1 / AMT1 |
| 52/53/54 | SRC2 / DST2 / AMT2 |
| 55/56/57 | SRC3 / DST3 / AMT3 |
| 58/59/60 | SRC4 / DST4 / AMT4 |

### 61-80（4 组 ENV）

| 组 | ID |
|---|---|
| ENV1 | 61-65（ATK/DEC/SUS/REL/LVL） |
| ENV2 | 66-70 |
| ENV3 | 71-75 |
| ENV4 | 76-80 |

### 81-90（和弦 + 鼓音量）

| ID | 名称 | 说明 |
|---|---|---|
| 81 | CHRD | 和弦模式 |
| 82 | VOIC | 和弦声位（`CLOSE/OPEN/INV1/INV2/+OCT`） |
| **83-90** | **鼓 8 件套音量** | KICK=83 SNARE=84 CLAP=85 HATCL=86 HATOP=87 TOM=88 RIM=89 BELL=90 |

### 91-100（v1.5 新增：振荡器同步 + INSERT 效果）

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

### 101-110（v1.5：ANALOG EDIT 新位置）

| ID | 名称 | 说明 |
|---|---|---|
| **101** | **TYPE** | **滤波器类型（LP/BP/HP）** |
| 102 | ESYNC | 包络同步（note value） |
| **103** | **WAVE** | **波形（SAW/SQR/TRI/SIN/PWM/SYNC/SUB）** |
| 104 | DTN | 失谐 |
| 105 | MIX | 混合 |
| 106 | NOIS | 噪声 |
| **107** | **CUT** | **截止频率** |
| **108** | **RES** | **共振** |
| 109 | DRV | 驱动 |
| 110 | KTR | 键跟踪 |

> ⚠️ **ANALOG EDIT 从旧 83-90 移到 101-110**。
> 引擎预设的 WAVE 枚举新增 **SYNC**（硬同步）和 **SUB**（低八度方波）。

---

## 二、全局参数（SET scope=1，id 0-26）

```
BPM=0(40-240,def120)  SWG=1  CLK=2  TUNE=3  TIME(DIV)=4
DLY: FDBK=5 COLR=6 MIX=7 SIZE=8 DAMP=9
CRT=10  CDP=11  MIDI=12  SYNC=13  ROUT=14
CPU=15  SLOT=16(1-4)  NAME=17  LOAD=18  SAVE=19
ENG=20  SET=21  CLRSQ=22  INIT=23  TYPE(REV)=24(ROOM/SPRING)
```

---

## 三、枚举

### DIV / TIME（10 个）

```
0=1/4  1=1/8  2=1/16  3=1/32  4=8T  5=16T  6=1/2  7=1/1
8=2BAR  9=4BAR    ← v1.5 新增
```

**注意**：写步时 `DIV=1` 表示**每步 1/8 音符**。MIDI 导出时，4/4 拍每步 tick = PPQ/2。

### 引擎（ENG，全局 id=20）

```
ANALOG=0  ''=1     PHASE=2   LOFI=3    SAMPLE=4
VOICE=5   TRIO=6   WHEEL=7   GRAIN=8   PHYS=9
DRUM=10   NOISE=11 FM6=12    SLICE=13
```

### ANALOG 波形（WAVE，id=103）

```
SAW / SQR / TRI / SIN / PWM / SYNC / SUB
```

（v1.1.5.1 只有前 5 个；SYNC / SUB 为 v1.5 新增）

### ANALOG 滤波器类型（TYPE，id=101）

```
LP / BP / HP
```

### 和弦声位（VOIC，id=82）

```
CLOSE / OPEN / INV1 / INV2 / +OCT
```

### ANALOG 预设（NAMES 实测）

```
0=808 BOOM  2=SUB BASS  4=ACID 303  6=REESE  7=SUB BASS
9=G-FUNK LD  11=STRINGS  13=WARM PAD  15=ATMOS PAD
```

完整预设名以 `NAMES` 命令读回的为准。

### DRUM 引擎预设（v1.5 实测仅 3 个）

```
0=DRUM KIT  1=KIT  2=HIT
```

---

## 四、TRACK_DUMP 格式（v1.5）

```
回复：body = [tr, engine, preset, (hi, lo) × 111]
```

- 头 3B = `[tr, engine, preset]` 单字节
- **参数值 = (hi << 7) | lo**——⚠️ **高字节在前**（与 SLOOP 相反！）
- 111 个参数（id 0-110）

> ⚠️ v1.5 之前 TRACK_DUMP(29) 不回复；**v1.5 起有效**。

---

## 五、TRACK 查询新发现（v1.5）

`TRACK []`（命令 27 空参）返回**全部 4 轨**的 engine / preset / LVL：

```
回复格式：[当前轨, 轨数, tr0_eng, tr0_pre, tr0_LVL_lo, tr0_LVL_hi, ?, ?, tr1_eng, tr1_pre, tr1_LVL, ...]
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

---

## 六、参数校准来源

参数范围以 **`fw_desc_v15.txt` 实测 DESC 值**为准。

### 已校准项

- ✅ 全部 111 个轨道参数（v1.5 实测）
- ✅ 全部 27 个全局参数
- ✅ DIV 10 个枚举
- ✅ ANALOG WAVE 7 个枚举
- ✅ 滤波器 TYPE 3 个枚举

### 待校准项

- ⏸ SYNC / TRIG / POL / QNTZ / SPRD / INSRT 各参数的完整范围
- ⏸ INSERT 效果 A/B/C 的具体含义（需对照 UI）