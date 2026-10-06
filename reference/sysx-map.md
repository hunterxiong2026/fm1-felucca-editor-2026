# FM-1 Felucca SysEx 参数映射

## 1. SysEx 消息格式

FM-1 直接使用 **Yamaha DX7 标准 SysEx 参数变更格式**：

```
F0 43 1n pp qq vv F7
```

| 字节 | 含义 | 说明 |
|---|---|---|
| `F0` | SysEx 开始 | 固定 |
| `43` | Yamaha 厂商 ID | 固定 |
| `1n` | 子状态 + 通道 | n = MIDI 通道 - 1 (Ch1 → 0x10, Ch2 → 0x11) |
| `pp` | 参数组 | `00` = 操作器参数, `01` = 全局音色参数 |
| `qq` | 参数地址 | 见下方映射表 |
| `vv` | 值 | 必须是十六进制，范围 0x00 - 0x63 (0-99) |
| `F7` | SysEx 结束 | 固定 |

> **注意**：全局参数存在偏移错误，实际地址比 DX7 标准值 **偏移 +2**（社区已确认）。

---

## 2. 操作器参数 (pp = 00)

6 个操作器共用同一套 21 个参数，地址通过基地址 + 偏移计算：

| 操作器 | 基地址 (hex) | 基地址 (dec) |
|---|---|---|
| Operator 6 | +00 | 0 |
| Operator 5 | +15 | 21 |
| Operator 4 | +2A | 42 |
| Operator 3 | +3F | 63 |
| Operator 2 | +54 | 84 |
| Operator 1 | +69 | 105 |

### 2.1 每个操作器的 21 个参数

| 偏移 | 参数名 | 范围 | 说明 |
|---|---|---|---|
| 00 | EG Rate 1 | 0-99 | 包络 Attack 速度 |
| 01 | EG Rate 2 | 0-99 | 包络 Decay 1 速度 |
| 02 | EG Rate 3 | 0-99 | 包络 Decay 2 速度 |
| 03 | EG Rate 4 | 0-99 | 包络 Release 速度 |
| 04 | EG Level 1 | 0-99 | 包络 Peak 电平 |
| 05 | EG Level 2 | 0-99 | 包络 Decay 1 电平 |
| 06 | EG Level 3 | 0-99 | 包络 Sustain 电平 |
| 07 | EG Level 4 | 0-99 | 包络 Release/Start 电平 |
| 08 | KBD Level Scaling Break Point | 0-99 | MIDI 音符 0 (C-2) 到 99 (G6) |
| 09 | KBD Level Scaling Left Depth | 0-99 | 断点左侧衰减深度 |
| 0A | KBD Level Scaling Right Depth | 0-99 | 断点右侧衰减深度 |
| 0B | KBD Level Scaling Left Curve | 0-3 | 0=-LIN, 1=-EXP, 2=+EXP, 3=+LIN |
| 0C | KBD Level Scaling Right Curve | 0-3 | 同上 |
| 0D | KBD Rate Scaling | 0-7 | 键跟踪速度修饰 |
| 0E | Amplitude Modulation Sensitivity | 0-3 | LFO 幅度调制影响程度 |
| 0F | Key Velocity Sensitivity | 0-7 | 力度响应深度 |
| 10 | Operator Output Level | 0-99 | 总音量 / 调制输出 |
| 11 | Oscillator Mode | 0-1 | 0=频率比率, 1=固定Hz |
| 12 | Oscillator Frequency Coarse | 0-31 | 粗调 |
| 13 | Oscillator Frequency Fine | 0-99 | 微调 |
| 14 | Oscillator Detune | 0-14 | 微调失谐，7 = 居中 |

**示例**：设置 Operator 1 的 Attack 速度为 80（十六进制 0x50）

```
F0 43 10 00 69 50 F7
   ↑  ↑  ↑  ↑  ↑  ↑
   |  |  |  |  |  └─ 值 0x50 = 80
   |  |  |  |  └─ 参数地址: Op1 基地址 0x69 + EG Rate1 偏移 0x00
   |  |  |  └─ 参数组: 00 = 操作器
   |  |  └─ 子状态+通道: 0x10 = Channel 1
   |  └─ Yamaha ID
   └─ SysEx 开始
```

---

## 3. 全局音色参数 (pp = 01)

> **重要**：全局参数地址比 DX7 标准值 **偏移 +2**。

| 地址 (hex) | 参数名 | 范围 | 说明 |
|---|---|---|---|
| 00 | Algorithm | 0-31 | FM 算法 |
| 01 | Feedback | 0-7 | 反馈量 |
| 02 | Oscillator Sync | 0-1 | 振荡器同步 |
| 03 | LFO Speed | 0-99 | LFO 速度 |
| 04 | LFO Delay | 0-99 | LFO 延迟 |
| 05 | LFO Pitch Mod Depth | 0-99 | 音高调制深度 |
| 06 | LFO Amp Mod Depth | 0-99 | 幅度调制深度 |
| 07 | LFO Wave | 0-5 | LFO 波形 |
| 08 | LFO Sync | 0-1 | LFO 键同步 |
| 09 | Pitch EG Rate 1 | 0-99 | 音高包络 Rate 1 |
| 0A | Pitch EG Rate 2 | 0-99 | 音高包络 Rate 2 |
| 0B | Pitch EG Rate 3 | 0-99 | 音高包络 Rate 3 |
| 0C | Pitch EG Rate 4 | 0-99 | 音高包络 Rate 4 |
| 0D | Pitch EG Level 1 | 0-99 | 音高包络 Level 1 |
| 0E | Pitch EG Level 2 | 0-99 | 音高包络 Level 2 |
| 0F | Pitch EG Level 3 | 0-99 | 音高包络 Level 3 |
| 10 | Pitch EG Level 4 | 0-99 | 音高包络 Level 4 |
| 11 | Transpose | 0-48 | 移调 |
| 12 | Voice Name | ASCII | 音色名（多字节） |

**示例**：设置算法为 5（十六进制 0x05）

```
F0 43 10 01 00 05 F7
         ↑  ↑  ↑  ↑
         |  |  |  └─ 值 0x05
         |  |  └─ 参数地址 0x00
         |  └─ 参数组: 01 = 全局
         └─ 通道 1
```

---

## 4. Felucca 扩展效果器参数 (pp = 02)

> 以下为 Felucca 固件扩展的效果器，非 DX7 标准。具体地址需对照 Web Editor 源码确认。

| 地址 (hex) | 参数名 | 范围 | 说明 |
|---|---|---|---|
| 00 | Filter Cutoff | 0-99 | 滤波器截止频率 |
| 01 | Filter Resonance | 0-99 | 滤波器共振 |
| 02 | Reverb Mix | 0-99 | 混响混合比 |
| 03 | Delay Mix | 0-99 | 延迟混合比 |
| 04 | Distortion | 0-99 | 失真量 |
| 05 | Chorus | 0-99 | 合唱深度 |
| 06 | Phaser | 0-99 | 移相器深度 |

---

## 5. 多引擎参数 (Felucca 特有)

Felucca 提供 **13 种引擎**，每个引擎有独立参数集。这些参数**不走 DX7 SysEx 格式**，需要通过 Felucca 自定义 SysEx 或 Web Editor 的 API 控制。

引擎列表：ANALOG, FM6, PHASE, LOFI, SAMPLE, VOICE, TRIO, WHEEL, GRAIN, PHYS, NOISE, SLICE, DRUM

---

## 6. 参数变更示例集

**6.1 改变 FM 音色亮度（Operator 1 输出电平）**

设置 Op1 输出电平为 99 (0x63)：

```
F0 43 10 00 79 63 F7
```

**6.2 改变包络 Attack**

设置 Op1 Attack (EG Rate 1) 为 0 (最快)：

```
F0 43 10 00 69 00 F7
```

**6.3 切换算法**

设置算法为 20 (0x14)：

```
F0 43 10 01 00 14 F7
```

**6.4 调整 LFO 速度**

设置 LFO 速度为 50 (0x32)：

```
F0 43 10 01 03 32 F7
```

---

## 7. 参考链接

- DX7 SysEx 格式权威文档：https://homepages.abdn.ac.uk/d.j.benson/pages/dx7/sysex-format.txt
- FM1 Controller (155 参数可视化编辑器)：https://www.zalmanim.com/2026/09/21/fm1-controller-vst3-mvave-fm-1-editor/
- Felucca 仓库：https://github.com/hugelton/Felucca
- Felucca Web Editor：https://hugelton.github.io/Felucca/webapp/editor/
- FM-1 SysEx Patch Curator：https://grandsummoner.github.io
- 社区讨论 (Elektronauts)：https://www.elektronauts.com/t/m-vave-fm-1/252170

---

## 8. 注意事项

1. **值必须是十六进制**：发送 vv 时，0-99 的十进制值需转为十六进制（99 → 0x63）。
2. **通道设置**：1n 中的 n 是 MIDI 通道减 1。Channel 1 → 10，Channel 2 → 11。
3. **全局参数偏移**：全局参数（pp = 01）的地址比 DX7 标准值偏移 +2。
4. **操作器顺序**：DX7 从 Operator 6 处理到 Operator 1。Op6 基地址为 +00，Op1 为 +69。
5. **Felucca 多引擎**：FM6 引擎使用上述 DX7 映射。其他引擎（ANALOG, PHASE, LOFI 等）的参数需通过 Web Editor API 或 Felucca 自定义 SysEx 控制，本映射表不覆盖。