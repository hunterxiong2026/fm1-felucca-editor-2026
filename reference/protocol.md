# Felucca 直连协议

> 帧格式、命令枚举、STEP/SONG 布局、INFO 解析、直连坑。
> 固件版本：FELUCCA **v1.5**
> 本文件只记录协议规范，不含客户端代码。

---

## 一、帧格式

```
F0 7D 46 4C <cmd & 0x7F> <args...> F7
```

- HDR = `7D 46 4C`
- 所有数据字节 7 bit
- v14 编码：`v14enc(v) = v + 8192 → [lo & 0x7F, (lo >> 7) & 0x7F]`；
  `v14dec(lo, hi) = lo + (hi << 7) - 8192`

---

## 二、命令枚举

| 命令 | 值 | 说明 |
|---|---|---|
| INFO | 1 | 设备信息 |
| GET / SET | 2 / 3 | 全局参数读 / 写（SET scope=1） |
| DESC | 5 | 参数描述（scope 0=轨道 / 1=全局） |
| STEP_GET / STEP_SET | 6 / 7 | 步进读 / 写 |
| PRESET | 8 | 应用引擎+预设 |
| PROJECT | 9 | 项目槽位：op 0=load 1=save 2=query |
| WATCH | 22 | 推送开关 |
| TRACK | 27 | 选择当前轨；**空参返回全部 4 轨信息（v1.5 新发现）** |
| TRACK_STEP | 30 | 轨内步进读写 |
| TRACK_PARAM | 31 | 轨内参数读写 |
| **TRACK_DUMP** | **29** | **全参数 dump（v1.5 起有效）** |
| SONG | 33 | 播放链 |

---

## 三、TRACK_STEP 写步布局

```
写步(TRACK_STEP 30)：[30, tr, i, n, note0..3, time, flags, vel, hit, acc, hi, chance]
读步(STEP_GET 6)：  [6, i]     ← 只带步索引！先发 TRACK [tr] 选轨
回复(STEP_GET)：    [i, n, note0..3, time, flags, vel, hit, acc, hi, chance, ...]
```

- `tr` = 0-3；`i` = 0-63；`n` = 0-4
- `time`：0=NOTE 1=TIE 2=REST
- `flags`：1=accent 2=slide
- `vel` = 0-127；`chance` = 0-100
- **陷阱**：STEP_GET 请求是 `[i]` 不是 `[tr, i]`（多带 tr 会 NO REPLY）
- **v1.5 变化**：回复尾部**多 1 字节**（实测 = 1），位于 chance 之后；发送参数不变

### hit/acc 位掩码（8 鼓位 lane）

```
bit0=KICK(36) bit1=SNARE(38) bit2=CLAP(39) bit3=HATCL(42)
bit4=HATOP(46) bit5=TOM(45) bit6=RIM(37) bit7=BELL(56)
```

编码：`hitsEnc(hit, acc) = [hit & 0x7F, acc & 0x7F, ((hit>>7)&1)|(((acc>>7)&1)<<1)]`

非鼓轨：hit=acc=0。

---

## 四、SONG 播放

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

---

## 五、INFO 解析要点（v1.5 实测）

```
version(\0串) nengines(1B) pcount(1B) gcount(1B) nstep(1B) pe0(1B)
engines×nengines(\0串) ntrk(1B) trailer[...]
```

- **v1.5 实测**：`version='FELUCCA v1.5'`, nengines=14, **pcount=111**, gcount=27,
  nstep=64, **pe0=103**, ntrk=4, chainRows=16, uiCaps=9
- `ntrk` 是解析流 pop 出来的独立 1 字节，**不在 trailer 数组内**
- `chainRows` 判定：`trailer[0] === 16` → chainRows=16
- `uiCaps` 判定：`trailer[0]==16 && trailer[1]==0x55 && trailer[2]==1` → `uiCaps = trailer[3] & 15`

**版本演进对照**：

| 版本 | pcount | pe0 | trailer |
|---|---|---|---|
| v1.0.2 | 91 | 83 | 18B |
| v1.1.5.1 | 99 | 91 | 30B |
| **v1.5** | **111** | **103** | 30B |

---

## 六、TRACK_DUMP 解析（v1.5）

```
回复 body = [tr, engine, preset, (hi, lo) × 111]
```

- 头 3B = `[tr, engine, preset]` 单字节
- 参数值 = `(hi << 7) | lo`——⚠️ **高字节在前**（与 SLOOP 的 `(lo, hi)` 顺序相反）
- 111 个参数（id 0-110）
- v1.5 之前 TRACK_DUMP 不回复；**v1.5 起有效**

---

## 七、TRACK 查询（v1.5）

`TRACK []`（空参）返回全部 4 轨的 engine/preset/LVL：

```
[当前轨, 轨数, tr0_eng, tr0_pre, tr0_LVL_lo, tr0_LVL_hi, ?, ?, tr1_eng, tr1_pre, tr1_LVL, ...]
```

**用途**：核对引擎/预设的权威手段（不必逐轨 TRACK_DUMP）。

---

## 八、直连坑（勿重踩）

1. **MIDIHDR 的 `dwUser`/`reserved` 字段必须是 8 字节指针**
2. **`MIM_LONGDATA = 0x3C4`**（误写 0x3C6 → 回复被静默丢弃）
3. **winmm 所有函数需显式声明 argtypes**
4. **winmm 回调必须是 5 参数**
5. **close() 不调用 `midiInReset`**（避免死锁）
6. **输入必须累积按 `F7` 切完整帧**
7. **`request()` 必须跳过 rc != cmd 的帧**
8. **`send()` 用带 NUL 的 buffer**
9. **设备名动态匹配**（见 §九）

---

## 九、设备名匹配（v1.5）

**多设备场景**：系统可能有多台 "Felucca" 命名的设备（Windows 会加 `2 - ` / `3 - ` 前缀）。

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

---

## 十、标准流程

```
1. 打开设备（动态匹配，跳过 SLOOP）
2. INFO 验证（version + pcount=111 + pe0=103）
3. 写全局（BPM / SWG）
4. 写 4 轨（PRESET + TRACK_PARAM + TRACK_STEP）
5. PROJECT save（显式保存）
6. SONG [1, ...] + SONG [2]（播放）
7. 实际听声验收（playing=1 只证明已触发）
```